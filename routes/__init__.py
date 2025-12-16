##routes/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from .auth import auth_bp
from .main import main_bp
from .export import export_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(export_bp, url_prefix='/export')
