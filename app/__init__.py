from flask import Flask
from flask_cors import CORS

from .config import DB_CONFIG
from .db import init_db
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    CORS(app)
    init_db()
    register_routes(app)
    return app