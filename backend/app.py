"""
app.py
Flask application factory + development entry point.

Run:
    python app.py
"""
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db
from routes.auth import auth_bp


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)

    # Allow requests from the Vite dev server and any localhost origin.
    # In production, replace "*" with your actual frontend domain.
    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]}})

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)

    # ── Create tables ─────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Generic error handlers ────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify(error="Endpoint not found."), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify(error="Method not allowed."), 405

    @app.errorhandler(500)
    def internal_error(_e):
        return jsonify(error="Internal server error."), 500

    return app


# ── Dev server entry point ────────────────────────────────────────────────────
if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
