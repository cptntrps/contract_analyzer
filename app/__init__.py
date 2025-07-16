# app/__init__.py
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['REPORTS_FOLDER'] = 'reports'
    app.config['TEMPLATES_FOLDER'] = 'contract_templates'

    # Create directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMPLATES_FOLDER'], exist_ok=True)

    with app.app_context():
        from .routes import init_routes
        init_routes(app)

    return app 