import os
import yaml
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError, OperationalError

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

    from .auth.dao import ProcedureError

    @app.errorhandler(OperationalError)
    def db_error(e):
        db.session.rollback()
        errno = e.orig.args[0] if e.orig is not None and e.orig.args else None
        if errno == 1644:  # SIGNAL з тригера
            return jsonify({"error": "Rejected by database trigger",
                            "detail": str(e.orig.args[1])}), 409
        return jsonify({"error": "Database error", "detail": str(e.orig)}), 500

    @app.errorhandler(ProcedureError)
    def procedure_error(e):
        status = 400 if e.errno == 1644 else 409 if e.errno in (1062, 1451, 1452) else 500
        return jsonify({"error": "Stored procedure failed", "detail": str(e)}), status

    return app
