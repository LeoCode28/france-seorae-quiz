"""Local entry point. For PythonAnywhere / WSGI, import `app` from here."""
import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true',
        host='127.0.0.1',
    )
