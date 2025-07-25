from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .config import Config
from .routes import register_routes

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    register_routes(app)
    return app
