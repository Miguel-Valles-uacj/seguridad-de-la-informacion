import os
import re
import logging
import unicodedata

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Email
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Logging to file (no trazas en respuesta al usuario)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    handler = logging.FileHandler('logs/app.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        # CSP mínimo (ajusta según tu app)
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"
        return response

    # Forms
    class UserForm(FlaskForm):
        name = StringField('Nombre', validators=[DataRequired(), Length(min=1, max=80)])
        email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])

    def normalize_string(s: str) -> str:
        # Normalización unicode y eliminación de caracteres no permitidos (whitelist básica)
        s = unicodedata.normalize('NFKC', s)
        s = re.sub(r'[^\w\s@.\-+]', '', s, flags=re.UNICODE)
        return s.strip()

    @app.route('/')
    def index():
        users = User.query.order_by(User.id.desc()).all()
        return render_template('index.html', users=users)

    @app.route('/add', methods=['GET', 'POST'])
    def add_user():
        form = UserForm()
        if form.validate_on_submit():
            name = normalize_string(form.name.data)
            email = form.email.data.lower().strip()
            if len(name) == 0:
                flash('Nombre inválido', 'error')
                return redirect(url_for('index'))
            # Uso de ORM -> evita inyección SQL
            user = User(name=name, email=email)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Usuario agregado', 'success')
            except Exception as e:
                db.session.rollback()
                app.logger.exception('Error al agregar usuario')
                flash('Ocurrió un error al procesar la solicitud', 'error')
            return redirect(url_for('index'))
        return render_template('add_user.html', form=form)

    @app.route('/search')
    def search():
        email = request.args.get('email', '').lower().strip()
        # Validación básica antes de usar en consultas
        if not email:
            return redirect(url_for('index'))
        if len(email) > 120:
            abort(400)
        # Ejemplo de consulta parametrizada usando text()
        row = db.session.execute(
            text('SELECT id, name, email FROM user WHERE email = :email'), {'email': email}
        ).fetchone()
        if row:
            # row es un Row object; convertir a lista con un pequeño dic
            user = {'id': row[0], 'name': row[1], 'email': row[2]}
            return render_template('index.html', users=[user])
        flash('No encontrado', 'info')
        return redirect(url_for('index'))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', message='Página no encontrada'), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception('Error interno')
        return render_template('error.html', message='Error interno del servidor'), 500

    return app

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    # No usar debug=True en producción
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
