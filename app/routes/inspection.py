from flask import Blueprint, request, jsonify

from app.services.inspection_service import (
    create_inspections_from_json,
    get_all_inspections,
)


inspection_bp = Blueprint("inspection_bp", __name__)


@inspection_bp.route("/", methods=["GET"])
def get_inspections():
    inspections = get_all_inspections()

    return jsonify(inspections)


@inspection_bp.route("/", methods=["POST"])
def create_inspections():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Request body must be a list of inspections."
        }), 400

    result = create_inspections_from_json(data)

    status_code = 201 if result["added_inspections"] else 200

    return jsonify(result), status_code