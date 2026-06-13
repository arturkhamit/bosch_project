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

    return result

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

    return {
        "added_products": added_products,
        "existing_products": existing_products,
        "incorrect_products": incorrect_products,
    }