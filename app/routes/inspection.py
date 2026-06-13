from flask import Blueprint, request, jsonify

from app.services.inspection_service import (
    create_inspections_from_json,
    get_all_inspections, update_inspection, delete_inspection,
)


inspection_bp = Blueprint("inspection_bp", __name__)


@inspection_bp.route("/", methods=["GET"])
def get_inspections():
    inspections, status_code = get_all_inspections()

    return jsonify(inspections), status_code


@inspection_bp.route("/", methods=["POST"])
def create_inspections():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Request body must be a list."
        }), 400

    result, status_code = create_inspections_from_json(data)

    return jsonify(result), status_code

@inspection_bp.route("/<int:inspection_id>", methods=["PATCH"])
def patch_inspection(inspection_id):
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a dictionary."
        }), 400

    result, status_code = update_inspection(inspection_id, data)

    return jsonify(result), status_code


@inspection_bp.route("/<int:inspection_id>", methods=["DELETE"])
def remove_inspection(inspection_id):
    result, status_code = delete_inspection(inspection_id)

    return jsonify(result), status_code