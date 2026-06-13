from flask import Blueprint, request, jsonify

from app.services.inspector_service import (
    create_inspectors_from_json,
    get_all_inspectors, update_inspector, delete_inspector,
)


inspector_bp = Blueprint("inspector_bp", __name__)


@inspector_bp.route("/", methods=["GET"])
def get_inspectors():
    inspectors, status_code = get_all_inspectors()

    return jsonify(inspectors), status_code


@inspector_bp.route("/", methods=["POST"])
def create_inspectors():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Request body must be a list."
        }), 400

    result, status_code = create_inspectors_from_json(data)

    return jsonify(result), status_code

@inspector_bp.route("/<int:inspector_id>", methods=["PATCH"])
def patch_inspector(inspector_id):
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a dictionary."
        }), 400

    result, status_code = update_inspector(inspector_id, data)

    return jsonify(result), status_code


@inspector_bp.route("/<int:inspector_id>", methods=["DELETE"])
def remove_inspector(inspector_id):
    result, status_code = delete_inspector(inspector_id)

    return jsonify(result), status_code