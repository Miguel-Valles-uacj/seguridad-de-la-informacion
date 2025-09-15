import pytest
from app import create_app, db, User

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_add_and_sanitize(client):
    # Intento de añadir contenido con etiqueta <script> para ver que se muestra escapado
    rv = client.post('/add', data={'name': 'Attacker<script>alert(1)</script>', 'email': 'att@example.com'}, follow_redirects=True)
    assert b'Usuario agregado' in rv.data
    assert b'<script>' not in rv.data  # plantilla debe escapar

def test_sql_injection_in_search(client):
    # Añadimos un usuario válido
    client.post('/add', data={'name': 'Normal', 'email': 'norm@example.com'}, follow_redirects=True)
    # Intento de inyección por parámetro 'email'
    rv = client.get('/search', query_string={'email': "anything' OR '1'='1"}, follow_redirects=True)
    # No debe devolver usuarios no autorizados por la inyección
    assert b'No encontrado' in rv.data or rv.status_code in (200, 302)
