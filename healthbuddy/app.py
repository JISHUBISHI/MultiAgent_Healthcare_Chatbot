"""Flask application factory and assembled feature registration."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from healthbuddy.features.analysis.routes import analysis_bp
from healthbuddy.features.auth.routes import auth_bp
from healthbuddy.features.frontend.routes import frontend_bp
from healthbuddy.features.system.routes import api_method_not_allowed, api_not_found, system_bp


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def create_app() -> Flask:
    """Create the Flask app and register feature modules."""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    app.config["BASE_DIR"] = Path(__file__).resolve().parent.parent
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "healthbuddy-dev-secret-key")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    public_base_url = os.environ.get("PUBLIC_BASE_URL", "").strip().lower()
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production" or public_base_url.startswith("https://")
    app.config["PREFERRED_URL_SCHEME"] = "https"
    CORS(app)

    app.register_blueprint(system_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(frontend_bp)

    @app.errorhandler(404)
    def handle_not_found(error):
        if request.path.startswith("/api/"):
            return api_not_found(request.path)
        return error

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        if request.path.startswith("/api/"):
            return api_method_not_allowed(request.path)
        return error

    return app


app = create_app()
