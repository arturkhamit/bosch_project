from flask import Blueprint, request, jsonify

from app.services.inspector_service import (
    create_inspectors_from_json,
    get_all_inspectors,
)


inspector_bp = Blueprint("inspector_bp", __name__)


@inspector_bp.route("/", methods=["GET"])
def get_inspectors():
    inspectors = get_all_inspectors()

    return jsonify(inspectors)


@inspector_bp.route("/", methods=["POST"])
def create_inspectors():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Request body must be a list of inspectors."
        }), 400

    result = create_inspectors_from_json(data)

    status_code = 201 if result["added_inspectors"] else 200

    return jsonify(result), status_code