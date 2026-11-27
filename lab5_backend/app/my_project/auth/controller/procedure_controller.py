from flask import Blueprint, jsonify, request
from ..service import ProcedureService
from .crud import json_body

service = ProcedureService()
procedure_bp = Blueprint("procedure", __name__, url_prefix="/procedures")


@procedure_bp.post("/artists")            # 2.a  CALL sp_insert_artist(...)
def insert_artist():
    return jsonify(service.insert_artist(json_body())), 201


@procedure_bp.post("/track-artists")      # 2.b  CALL sp_add_track_artist(...)
def add_track_artist():
    return jsonify(service.add_track_artist(json_body())), 201


@procedure_bp.post("/noname-batch")       # 2.c  CALL sp_insert_noname_batch()
def noname_batch():
    return jsonify(service.insert_noname_batch()), 201


@procedure_bp.get("/duration-stat")       # 2.d  CALL sp_duration_stat(?stat=MAX|MIN|SUM|AVG)
def duration_stat():
    return jsonify(service.duration_stat(request.args.get("stat")))


@procedure_bp.post("/split-artists")      # 2.e  CALL sp_split_artists_random()
def split_artists():
    return jsonify(service.split_artists_randomly()), 201
