from app.models.inspection import Inspection
from app.models.defect import Defect
from app.models.enums import InspectionResultEnum, DefectStatusEnum, DefectSeverityEnum


def get_quality_summary():
    total_inspections = Inspection.query.count()

    passed_inspections = Inspection.query.filter_by(
        result=InspectionResultEnum.PASS
    ).count()

    failed_inspections = Inspection.query.filter_by(
        result=InspectionResultEnum.FAIL
    ).count()

    warning_inspections = Inspection.query.filter_by(
        result=InspectionResultEnum.WARNING
    ).count()

    open_defects = Defect.query.filter_by(
        status=DefectStatusEnum.OPEN
    ).count()

    critical_defects = Defect.query.filter_by(
        severity=DefectSeverityEnum.CRITICAL
    ).count()

    return {
        "total_inspections": total_inspections,
        "passed_inspections": passed_inspections,
        "failed_inspections": failed_inspections,
        "warning_inspections": warning_inspections,
        "open_defects": open_defects,
        "critical_defects": critical_defects,
    }