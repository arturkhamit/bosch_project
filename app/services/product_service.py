from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.product import Product

def get_all_products():
    products = Product.query.all()

    result = []

    for product in products:
        result.append({
            "id": product.id,
            "product_code": product.product_code,
            "name": product.name,
            "product_family": product.product_family,
            "revision": product.revision,
            "is_active": product.is_active,
        })

    return result, 200


def create_products_from_json(data):
    added_products = []
    existing_products = []
    incorrect_products = []

    for product_json in data:
        try:
            product = Product(
                product_code=product_json["product_code"],
                name=product_json["name"],
                product_family=product_json.get("product_family"),
                revision=product_json.get("revision"),
                is_active=product_json.get("is_active", True),
            )

            db.session.add(product)
            db.session.commit()

            added_products.append(product_json)

        except IntegrityError:
            db.session.rollback()
            existing_products.append(product_json)

        except KeyError:
            incorrect_products.append(product_json)

        except SQLAlchemyError:
            db.session.rollback()
            incorrect_products.append(product_json)

    result = {
        "added_products": added_products,
        "existing_products": existing_products,
        "incorrect_products": incorrect_products,
    }

    if added_products:
        return result, 201

    if incorrect_products and not existing_products:
        return result, 400

    return result, 200

def update_product(product_id, data):
    product = db.session.get(Product, product_id)

    if product is None:
        return {
            "error": "Product not found."
        }, 404

    try:
        if "product_code" in data:
            product.product_code = data["product_code"]

        if "name" in data:
            product.name = data["name"]

        if "product_family" in data:
            product.product_family = data["product_family"]

        if "revision" in data:
            product.revision = data["revision"]

        if "is_active" in data:
            product.is_active = data["is_active"]

        db.session.commit()

        return {
            "updated_product": {
                "id": product.id,
                "product_code": product.product_code,
                "name": product.name,
                "product_family": product.product_family,
                "revision": product.revision,
                "is_active": product.is_active,
            }
        }, 200

    except IntegrityError:
        db.session.rollback()

        return {
            "error": "Product with this product_code already exists."
        }, 409

    except SQLAlchemyError:
        db.session.rollback()

        return {
            "error": "Database error."
        }, 500

def delete_product(product_id):
    product = db.session.get(Product, product_id)

    if product is None:
        return {
            "error": "Product not found."
        }, 404

    try:
        product.is_active = False

        db.session.commit()

        return {
            "message": "Product deactivated.",
            "product": {
                "id": product.id,
                "product_code": product.product_code,
                "name": product.name,
                "is_active": product.is_active,
            }
        }, 200

    except SQLAlchemyError:
        db.session.rollback()

        return {
            "error": "Database error."
        }, 500