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

    return result

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

    return {
        "added_inspectors": added_inspectors,
        "existing_inspectors": existing_inspectors,
        "incorrect_inspectors": incorrect_inspectors,
    }