from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.inspector import Inspector


def get_all_inspectors():
    inspectors = Inspector.query.all()

    result = []

    for inspector in inspectors:
        result.append({
            "id": inspector.id,
            "employee_number": inspector.employee_number,
            "first_name": inspector.first_name,
            "last_name": inspector.last_name,
            "email": inspector.email,
            "department": inspector.department,
            "role": inspector.role,
            "is_active": inspector.is_active,
        })

    return result, 200

def create_inspectors_from_json(data):
    added_inspectors = []
    existing_inspectors = []
    incorrect_inspectors = []

    for inspector_json in data:
        try:
            inspector = Inspector(
                employee_number=inspector_json["employee_number"],
                first_name=inspector_json["first_name"],
                last_name=inspector_json["last_name"],
                email=inspector_json["email"],
                department=inspector_json.get("department"),
                role=inspector_json["role"],
                is_active=inspector_json.get("is_active", True),
            )

            db.session.add(inspector)
            db.session.commit()

            added_inspectors.append(inspector_json)

        except IntegrityError:
            db.session.rollback()
            existing_inspectors.append(inspector_json)

        except KeyError:
            incorrect_inspectors.append(inspector_json)

        except SQLAlchemyError:
            db.session.rollback()
            incorrect_inspectors.append(inspector_json)

    result = {
        "added_inspectors": added_inspectors,
        "existing_inspectors": existing_inspectors,
        "incorrect_inspectors": incorrect_inspectors,
    }

    if added_inspectors:
        return result, 201

    if incorrect_inspectors and not existing_inspectors:
        return result, 400

    return result, 200

def update_inspector(inspector_id, data):
    inspector = db.session.get(Inspector, inspector_id)

    if inspector is None:
        return {
            "error": "Inspector not found."
        }, 404

    try:
        if "employee_number" in data:
            inspector.employee_number = data["employee_number"]

        if "first_name" in data:
            inspector.first_name = data["first_name"]

        if "last_name" in data:
            inspector.last_name = data["last_name"]

        if "email" in data:
            inspector.email = data["email"]

        if "department" in data:
            inspector.department = data["department"]

        if "role" in data:
            inspector.role = data["role"]

        if "is_active" in data:
            inspector.is_active = data["is_active"]

        db.session.commit()

        return {
            "updated_inspector": {
                "id": inspector.id,
                "employee_number": inspector.employee_number,
                "first_name": inspector.first_name,
                "last_name": inspector.last_name,
                "email": inspector.email,
                "department": inspector.department,
                "role": inspector.role,
                "is_active": inspector.is_active,
            }
        }, 200

    except IntegrityError:
        db.session.rollback()

        return {
            "error": "Inspector with this employee_number or email already exists."
        }, 409

    except SQLAlchemyError:
        db.session.rollback()

        return {
            "error": "Database error."
        }, 500


def delete_inspector(inspector_id):
    inspector = db.session.get(Inspector, inspector_id)

    if inspector is None:
        return {
            "error": "Inspector not found."
        }, 404

    try:
        inspector.is_active = False

        db.session.commit()

        return {
            "message": "Inspector deactivated.",
            "inspector": {
                "id": inspector.id,
                "employee_number": inspector.employee_number,
                "first_name": inspector.first_name,
                "last_name": inspector.last_name,
                "email": inspector.email,
                "is_active": inspector.is_active,
            }
        }, 200

    except SQLAlchemyError:
        db.session.rollback()

        return {
            "error": "Database error."
        }, 500