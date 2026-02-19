import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'devkey')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///examcards.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    # Rate limiting defaults (used by Flask-Limiter)
    RATELIMIT_DEFAULT = [
        "200 per day",
        "50 per hour"
    ]
    # Enforce secure cookies in production
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'