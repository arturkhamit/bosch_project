from flask import Blueprint, request, jsonify

from app.services.defect_service import (
    create_defects_from_json,
    get_all_defects, update_defect, delete_defect,
)


defect_bp = Blueprint("defect_bp", __name__)


@defect_bp.route("/", methods=["GET"])
def get_defects():
    defects, status_code = get_all_defects()

    return jsonify(defects), status_code


@defect_bp.route("/", methods=["POST"])
def create_defects():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Request body must be a list."
        }), 400

    result, status_code = create_defects_from_json(data)

    return jsonify(result), status_code

@defect_bp.route("/<int:defect_id>", methods=["PATCH"])
def patch_defect(defect_id):
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a dictionary."
        }), 400

    result, status_code = update_defect(defect_id, data)

    return jsonify(result), status_code


@defect_bp.route("/<int:defect_id>", methods=["DELETE"])
def remove_defect(defect_id):
    result, status_code = delete_defect(defect_id)

    return jsonify(result), status_code