from datetime import datetime

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.inspection import Inspection
from app.models.enums import InspectionResultEnum


def get_all_inspections():
    inspections = Inspection.query.all()

    result = []

    for inspection in inspections:
        result.append({
            "id": inspection.id,
            "batch_number": inspection.batch_number,
            "serial_number": inspection.serial_number,
            "inspection_date": inspection.inspection_date.isoformat() if inspection.inspection_date else None,
            "result": inspection.result.value,
            "notes": inspection.notes,
            "product_id": inspection.product_id,
            "inspector_id": inspection.inspector_id,
        })

    return result, 200

def create_inspections_from_json(data):
    added_inspections = []
    existing_inspections = []
    incorrect_inspections = []

    for inspection_json in data:
        try:
            inspection = Inspection(
                batch_number=inspection_json["batch_number"],
                serial_number=inspection_json["serial_number"],
                inspection_date=datetime.fromisoformat(
                    inspection_json["inspection_date"]
                ),
                result=InspectionResultEnum(inspection_json["result"]),
                notes=inspection_json.get("notes"),
                product_id=inspection_json["product_id"],
                inspector_id=inspection_json["inspector_id"],
            )

            db.session.add(inspection)
            db.session.commit()

            added_inspections.append(inspection_json)

        except IntegrityError:
            db.session.rollback()
            existing_inspections.append(inspection_json)

        except KeyError:
            incorrect_inspections.append(inspection_json)

        except ValueError:
            incorrect_inspections.append(inspection_json)

        except SQLAlchemyError:
            db.session.rollback()
            incorrect_inspections.append(inspection_json)

    result = {
        "added_inspections": added_inspections,
        "existing_inspections": existing_inspections,
        "incorrect_inspections": incorrect_inspections,
    }

    if added_inspections:
        return result, 201

    if incorrect_inspections and not existing_inspections:
        return result, 400

    return result, 200

def update_inspection(inspection_id, data):
    inspection = db.session.get(Inspection, inspection_id)

    if inspection is None:
        return {
            "error": "Inspection not found."
        }, 404

    try:
        if "batch_number" in data:
            inspection.batch_number = data["batch_number"]

        if "serial_number" in data:
            inspection.serial_number = data["serial_number"]

        if "inspection_date" in data:
            inspection.inspection_date = datetime.fromisoformat(data["inspection_date"])

        if "result" in data:
            inspection.result = InspectionResultEnum(data["result"])

        if "notes" in data:
            inspection.notes = data["notes"]

        if "product_id" in data:
            inspection.product_id = data["product_id"]

        if "inspector_id" in data:
            inspection.inspector_id = data["inspector_id"]

        db.session.commit()

        return {
            "updated_inspection": {
                "id": inspection.id,
                "batch_number": inspection.batch_number,
                "serial_number": inspection.serial_number,
                "inspection_date": inspection.inspection_date.isoformat() if inspection.inspection_date else None,
                "result": inspection.result.value,
                "notes": inspection.notes,
                "product_id": inspection.product_id,
                "inspector_id": inspection.inspector_id,
            }
        }, 200

    except ValueError:
        db.session.rollback()

        return {
            "error": "Invalid inspection_date or result value."
        }, 400

    except IntegrityError:
        db.session.rollback()

        return {
            "error": "Database integrity error. Check product_id and inspector_id."
        }, 409

    except SQLAlchemyError:
        db.session.rollback()

        return {
            "error": "Database error."
        }, 500


def delete_inspection(inspection_id):
    inspection = db.session.get(Inspection, inspection_id)

    if inspection is None:
        return {
            "error": "Inspection not found."
        }, 404

    try:
        db.session.delete(inspection)
        db.session.commit()

        return {
            "message": "Inspection deleted.",
            "inspection_id": inspection_id,
        }, 200

    except IntegrityError:
        db.session.rollback()

        return {
            "error": "Cannot delete inspection because it is connected to another record."
        }, 409

    except SQLAlchemyError:
        db.session.rollback()

        return {
            "error": "Database error."
        }, 500