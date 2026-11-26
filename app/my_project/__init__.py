import os
import yaml
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError

db = SQLAlchemy()


def create_app(config_override=None):
    app = Flask(__name__)
    path = os.path.join(os.path.dirname(__file__), "..", "config", "app.yml")
    with open(path, encoding="utf-8") as f:
        app.config.update(yaml.safe_load(f)["development"])
    if os.environ.get("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    from .auth.route import register_routes
    register_routes(app)

    @app.errorhandler(ValueError)
    def bad_request(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(IntegrityError)
    def conflict(e):
        db.session.rollback()
        return jsonify({"error": "Integrity constraint violated",
                        "detail": str(e.orig)}), 409

    @app.errorhandler(DataError)
    def bad_data(e):
        db.session.rollback()
        return jsonify({"error": "Invalid data", "detail": str(e.orig)}), 400

    return app
