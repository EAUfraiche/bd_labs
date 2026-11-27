from flask import Blueprint, jsonify, request


def json_body():
    data = request.get_json(silent=True)
    if data is None:
        raise ValueError("Valid JSON body required")
    return data


def not_found(what="Resource"):
    return jsonify({"error": f"{what} not found"}), 404


def make_crud_blueprint(name, prefix, service):
    bp = Blueprint(name, __name__, url_prefix=prefix)

    @bp.get("")
    def get_all():
        return jsonify(service.get_all())

    @bp.get("/<int:obj_id>")
    def get_one(obj_id):
        r = service.get_one(obj_id)
        return jsonify(r) if r else not_found()

    @bp.post("")
    def create():
        return jsonify(service.create(json_body())), 201

    @bp.put("/<int:obj_id>")
    def update(obj_id):
        r = service.update(obj_id, json_body())
        return jsonify(r) if r else not_found()

    @bp.delete("/<int:obj_id>")
    def delete(obj_id):
        return ("", 204) if service.delete(obj_id) else not_found()

    return bp


def add_children_routes(bp, service, key):
    """M:1: GET /<prefix>/<id>/<key> та GET /<prefix>/<key> (для кожного запису - його дочірні)."""

    @bp.get(f"/<int:obj_id>/{key}", endpoint=f"{key}_of_one")
    def of_one(obj_id):
        r = service.get_with(obj_id, key)
        return jsonify(r) if r else not_found()

    @bp.get(f"/{key}", endpoint=f"all_with_{key}")
    def all_with():
        return jsonify(service.get_all_with(key))
