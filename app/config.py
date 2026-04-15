"""Application configuration."""
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-local-only-change-in-prod')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV', 'development') == 'production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin1234')
    GOOGLE_MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY', '')
    GOOGLE_MYMAPS_ID = os.environ.get(
        'GOOGLE_MYMAPS_ID', '18iuL7lKBF0vyFaFOhFdCTRYtpMg'
    )
