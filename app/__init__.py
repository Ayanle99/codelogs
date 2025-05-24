from flask import Flask
from config import Config

def create_app(class_config=Config):
    app = Flask(__name__)
    app.config.from_object(class_config)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app