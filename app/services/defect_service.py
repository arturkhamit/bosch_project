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

    return result

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

    return {
        "added_defects": added_defects,
        "existing_defects": existing_defects,
        "incorrect_defects": incorrect_defects,
    }