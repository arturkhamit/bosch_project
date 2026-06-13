from flask import Blueprint, request, jsonify

from app.services.defect_service import (
    create_defects_from_json,
    get_all_defects,
)


defect_bp = Blueprint("defect_bp", __name__)


@defect_bp.route("/", methods=["GET"])
def get_defects():
    defects = get_all_defects()

    return jsonify(defects)


@defect_bp.route("/", methods=["POST"])
def create_defects():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Request body must be a list of defects."
        }), 400

    result = create_defects_from_json(data)

    status_code = 201 if result["added_defects"] else 200

    return jsonify(result), status_code