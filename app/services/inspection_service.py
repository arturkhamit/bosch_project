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

    return result

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

    return {
        "added_inspections": added_inspections,
        "existing_inspections": existing_inspections,
        "incorrect_inspections": incorrect_inspections,
    }