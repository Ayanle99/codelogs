import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user

from config import Config

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'  # redirect to this route if login is required


def create_app(class_config=Config):
    app = Flask(__name__)
    app.config.from_object(class_config)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)


    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.users import bp as users_bp
    app.register_blueprint(users_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Track user activity (online status)
    @app.before_request
    def update_last_seen():
        if current_user.is_authenticated:
            now = datetime.utcnow()
            if not current_user.last_seen or (now - current_user.last_seen).total_seconds() > 60:
                current_user.last_seen = now
                try:
                    db.session.commit()
                except Exception as e:
                    app.logger.warning(f"Failed to update last_seen: {e}")
                    db.session.rollback()

    # --- Logging Setup ---
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/app.log', maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        ))
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')

        # Optional: log all incoming requests (comment out if not needed)
        @app.before_request
        def log_request_info():
            app.logger.info(f"{request.remote_addr} - {request.method} {request.path}")

        # Optional: log unhandled exceptions
        @app.errorhandler(Exception)
        def handle_unexpected_error(e):
            app.logger.exception(f"Unhandled Exception: {e}")
            return "Internal Server Error", 500

    return app


# Ensure models are imported after db is defined
from app.models import User
from app.users.models import ProfileViewRequest
