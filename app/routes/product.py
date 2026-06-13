from flask import Blueprint, request, jsonify

from app.services.product_service import (
    create_products_from_json, get_all_products, update_product, delete_product,
)


product_bp = Blueprint("product_bp", __name__)


@product_bp.route("/", methods=["GET"])
def get_products():
    products, status_code = get_all_products()

    return jsonify(products), status_code


@product_bp.route("/", methods=["POST"])
def create_products():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Request body must be a list."
        }), 400

    result, status_code = create_products_from_json(data)

    return jsonify(result), status_code

@product_bp.route("/<int:product_id>", methods=["PATCH"])
def patch_product(product_id):
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a dictionary."
        }), 400

    result, status_code = update_product(product_id, data)

    return jsonify(result), status_code


@product_bp.route("/<int:product_id>", methods=["DELETE"])
def remove_product(product_id):
    result, status_code = delete_product(product_id)

    return jsonify(result), status_code