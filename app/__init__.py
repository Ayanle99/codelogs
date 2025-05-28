import logging  # <-- added for logging
from logging.handlers import RotatingFileHandler  # <-- added for rotating file logging
import os  # <-- to check/create logs directory
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager



db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'


def create_app(class_config=Config):
    app = Flask(__name__)
    app.config.from_object(class_config)

    db.init_app(app)
    migrate.init_app(app, db)

    login.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.users import bp as users_bp
    app.register_blueprint(users_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # --- Logging Setup START ---
    # Only set up logging in production (not in debug or testing)
    if True:
    #if not app.debug and not app.testing:

        # Create 'logs' directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # Set up a rotating file handler (10KB max size, 10 backup files)
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)

        # Format log messages: timestamp - level - module - message
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        ))

        # Set the file handler log level to INFO
        file_handler.setLevel(logging.INFO)

        # Add the handler to the app's logger
        app.logger.addHandler(file_handler)

        # Set the overall app logger level
        app.logger.setLevel(logging.INFO)

        # Initial log message when the app starts
        app.logger.info('App startup')
    # --- Logging Setup END ---

    return app


from app.models import User