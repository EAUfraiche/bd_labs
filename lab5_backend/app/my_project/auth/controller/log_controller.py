from flask import Blueprint, jsonify
from ..service import LogService

service = LogService()
log_bp = Blueprint("log", __name__, url_prefix="/logs")


@log_bp.get("/playlists-deleted")
def playlists_deleted():
    return jsonify(service.get_all())
