from flask import Blueprint, request, jsonify

from app.services.product_service import (
    create_products_from_json,
    get_all_products,
)


product_bp = Blueprint("product_bp", __name__)


@product_bp.route("/", methods=["GET"])
def get_products():
    products = get_all_products()

    return jsonify(products)


@product_bp.route("/", methods=["POST"])
def create_products():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."
        }), 415

    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({
            "error": "Request body must be a list of products."
        }), 400

    result = create_products_from_json(data)

    status_code = 201 if result["added_products"] else 200

    return jsonify(result), status_code