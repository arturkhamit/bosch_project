from datetime import datetime

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.defect import Defect
from app.models.enums import DefectSeverityEnum, DefectStatusEnum


def get_all_defects():
    defects = Defect.query.all()

    result = []

    for defect in defects:
        result.append({
            "id": defect.id,
            "defect_code": defect.defect_code,
            "defect_type": defect.defect_type,
            "severity": defect.severity.value,
            "status": defect.status.value,
            "description": defect.description,
            "detected_at": defect.detected_at.isoformat() if defect.detected_at else None,
            "resolved_at": defect.resolved_at.isoformat() if defect.resolved_at else None,
            "root_cause": defect.root_cause,
            "corrective_action": defect.corrective_action,
            "product_id": defect.product_id,
            "inspection_id": defect.inspection_id,
        })

    return result, 200

def create_defects_from_json(data):
    added_defects = []
    existing_defects = []
    incorrect_defects = []

    for defect_json in data:
        try:
            defect = Defect(
                defect_code=defect_json["defect_code"],
                defect_type=defect_json["defect_type"],
                severity=DefectSeverityEnum(defect_json["severity"]),
                status=DefectStatusEnum(defect_json["status"]),
                description=defect_json["description"],
                detected_at=datetime.fromisoformat(defect_json["detected_at"]),
                resolved_at=datetime.fromisoformat(defect_json["resolved_at"])
                if defect_json.get("resolved_at") else None,
                root_cause=defect_json.get("root_cause"),
                corrective_action=defect_json.get("corrective_action"),
                product_id=defect_json["product_id"],
                inspection_id=defect_json["inspection_id"],
            )

            db.session.add(defect)
            db.session.commit()

            added_defects.append(defect_json)

        except IntegrityError:
            db.session.rollback()
            existing_defects.append(defect_json)

        except KeyError:
            incorrect_defects.append(defect_json)

        except ValueError:
            incorrect_defects.append(defect_json)

        except SQLAlchemyError:
            db.session.rollback()
            incorrect_defects.append(defect_json)

    result = {
        "added_defects": added_defects,
        "existing_defects": existing_defects,
        "incorrect_defects": incorrect_defects,
    }

    if added_defects:
        return result, 201

    if incorrect_defects and not existing_defects:
        return result, 400

    return result, 200

def update_defect(defect_id, data):
    defect = db.session.get(Defect, defect_id)

    if defect is None:
        return {
            "error": "Defect not found."
        }, 404

    try:
        if "defect_code" in data:
            defect.defect_code = data["defect_code"]

        if "defect_type" in data:
            defect.defect_type = data["defect_type"]

        if "severity" in data:
            defect.severity = DefectSeverityEnum(data["severity"])

        if "status" in data:
            defect.status = DefectStatusEnum(data["status"])

        if "description" in data:
            defect.description = data["description"]

        if "detected_at" in data:
            defect.detected_at = datetime.fromisoformat(data["detected_at"])

        if "resolved_at" in data:
            defect.resolved_at = datetime.fromisoformat(data["resolved_at"]) if data["resolved_at"] else None

        if "root_cause" in data:
            defect.root_cause = data["root_cause"]

        if "corrective_action" in data:
            defect.corrective_action = data["corrective_action"]

        if "product_id" in data:
            defect.product_id = data["product_id"]

        if "inspection_id" in data:
            defect.inspection_id = data["inspection_id"]

        db.session.commit()

        return {
            "updated_defect": {
                "id": defect.id,
                "defect_code": defect.defect_code,
                "defect_type": defect.defect_type,
                "severity": defect.severity.value,
                "status": defect.status.value,
                "description": defect.description,
                "detected_at": defect.detected_at.isoformat() if defect.detected_at else None,
                "resolved_at": defect.resolved_at.isoformat() if defect.resolved_at else None,
                "root_cause": defect.root_cause,
                "corrective_action": defect.corrective_action,
                "product_id": defect.product_id,
                "inspection_id": defect.inspection_id,
            }
        }, 200

    except ValueError:
        db.session.rollback()

        return {
            "error": "Invalid datetime, severity, or status value."
        }, 400

    except IntegrityError:
        db.session.rollback()

        return {
            "error": "Database integrity error. Check product_id and inspection_id."
        }, 409

    except SQLAlchemyError:
        db.session.rollback()

        return {
            "error": "Database error."
        }, 500


def delete_defect(defect_id):
    defect = db.session.get(Defect, defect_id)

    if defect is None:
        return {
            "error": "Defect not found."
        }, 404

    try:
        db.session.delete(defect)
        db.session.commit()

        return {
            "message": "Defect deleted.",
            "defect_id": defect_id,
        }, 200

    except SQLAlchemyError:
        db.session.rollback()

        return {
            "error": "Database error."
        }, 500