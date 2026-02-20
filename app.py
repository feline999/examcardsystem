from flask import Flask
from config import Config
from extensions import db, login
import logging
import os

# Optional Sentry monitoring
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
except Exception:
    sentry_sdk = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login.init_app(app)
    from extensions import csrf, talisman, limiter
    csrf.init_app(app)
    
    # Configure rate limiter with proper defaults
    limiter.init_app(app)
    limiter._default_limits = ["200 per day", "50 per hour"]  # Set default limits directly
    # Structured logging setup
    from pythonjsonlogger import jsonlogger
    from logging.handlers import TimedRotatingFileHandler

    log_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(log_formatter)

    log_dir = os.environ.get('LOG_DIR', os.path.join(app.root_path, 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, os.environ.get('LOG_FILE', 'app.log'))
    handler_file = TimedRotatingFileHandler(log_file, when='midnight', backupCount=14)
    handler_file.setFormatter(log_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler_console)
    root_logger.addHandler(handler_file)
    app.logger = root_logger

    # Initialize Sentry if DSN provided
    sentry_dsn = os.environ.get('SENTRY_DSN')
    if sentry_sdk is not None and sentry_dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration(), sentry_logging],
            traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', 0.0))
        )

    # Content Security Policy: allow self and CDN used by bootstrap and jsdelivr
    csp = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "https://cdn.jsdelivr.net"],
        "style-src": ["'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'"],
        "font-src": ["'self'", "https://cdn.jsdelivr.net"],
        "img-src": ["'self'", "data:"]
    }
     # Apply security headers
         # Apply security headers
    talisman.init_app(app, content_security_policy=csp)
    
    # Initialize rate limiter with defaults from config
    limiter.init_app(app)
    limiter.enabled = False  # This disables rate limiting temporarily
    
        # Rate limits are now set directly on the limiter instance
    # To customize limits per route, use @limiter.limit("1 per day") decorators
    
    from auth import auth_bp
    
    from auth import auth_bp
    from admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
