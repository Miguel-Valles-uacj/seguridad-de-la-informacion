# Práctica C3 — Desarrollo de software seguro (Ejemplo Flask)

Este repositorio contiene una aplicación **Flask** mínima y segura diseñada como ejemplo para la práctica **C3 - Práctica software seguro**.
Implementa validación de entradas, normalización, codificación de salida (Jinja2 auto-escape), manejo de errores controlado y uso de consultas parametrizadas/ORM para evitar inyección SQL.

---
## Contenido
- `app.py` — aplicación Flask principal (modelo, rutas, validación, seguridad headers, logging).
- `templates/` — plantillas Jinja2 (base, lista, formulario, error).
- `requirements.txt` — dependencias.
- `.env.example` — variables de entorno ejemplo.
- `Procfile` — para despliegue con gunicorn (Heroku/Render).
- `tests/test_app.py` — tests básicos con pytest que incluyen intento de inyección.
- `.gitignore`

---
## Requisitos (instalar)

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate    # Windows (PowerShell)
pip install -r requirements.txt
```

## Variables de entorno
Copia `.env.example` a `.env` y define `SECRET_KEY` y opcionalmente `DATABASE_URL`.

Ejemplo `.env`:
```
SECRET_KEY=un-secret-aleatorio
DATABASE_URL=sqlite:///data.db
```

## Ejecutar localmente (desarrollo)
```bash
python app.py
```
Esto crea la base de datos `data.db` y lanza el servidor en `http://127.0.0.1:5000/`.

## Ejecutar tests
```bash
pytest -q
```

## Despliegue (resumen)
1. Sube el repositorio a GitHub.
2. Elige un proveedor (Render, Railway, Heroku, etc.).
3. Conecta el repo, configura variables de entorno `SECRET_KEY` y `DATABASE_URL` (si usas Postgres en producción).
4. Comando de inicio: `gunicorn app:app`

---
## Evidencias sugeridas para entregar
- Enlace público de la aplicación desplegada.
- `README.md` (este archivo) con medidas de seguridad implementadas.
- Captura de pantalla o video de pruebas: intento de inyección y resultado (fallido), logs de servidor.
- Repositorio con código.

---
## Seguridad implementada (resumen)
- **Validación servidor-side** con WTForms y validadores (email, longitudes).
- **Normalización** de cadenas (unicodedata + regex whitelist).
- **ORM / consultas parametrizadas** (SQLAlchemy); muestra de `text()` con parámetros ligados.
- **Codificación de salida**: Jinja2 autoescape; plantillas usan `|e` si es necesario.
- **Manejo de errores**: handlers 404/500 genéricos; logging a archivo `logs/app.log` y rollback en errores de BD.
- **Encabezados de seguridad**: CSP, X-Frame-Options, X-Content-Type-Options.

Si quieres que genere el repositorio en tu GitHub automáticamente o que lo prepare como un ZIP para descargar, dímelo y lo preparo.
