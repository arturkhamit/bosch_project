from datetime import date, datetime

import pandas as pd

from app.models.product import Product
from app.models.inspector import Inspector
from app.models.inspection import Inspection
from app.models.defect import Defect
from app.models.enums import (
    InspectionResultEnum,
    DefectStatusEnum,
    DefectSeverityEnum,
)


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

    total_defects = Defect.query.count()

    open_defects = Defect.query.filter_by(
        status=DefectStatusEnum.OPEN
    ).count()

    in_progress_defects = Defect.query.filter_by(
        status=DefectStatusEnum.IN_PROGRESS
    ).count()

    resolved_defects = Defect.query.filter_by(
        status=DefectStatusEnum.RESOLVED
    ).count()

    closed_defects = Defect.query.filter_by(
        status=DefectStatusEnum.CLOSED
    ).count()

    critical_defects = Defect.query.filter_by(
        severity=DefectSeverityEnum.CRITICAL
    ).count()

    high_defects = Defect.query.filter_by(
        severity=DefectSeverityEnum.HIGH
    ).count()

    if total_inspections > 0:
        pass_rate = round(passed_inspections / total_inspections * 100, 2)
        fail_rate = round(failed_inspections / total_inspections * 100, 2)
        warning_rate = round(warning_inspections / total_inspections * 100, 2)
    else:
        pass_rate = 0
        fail_rate = 0
        warning_rate = 0

    return {
        "inspections": {
            "total": total_inspections,
            "passed": passed_inspections,
            "failed": failed_inspections,
            "warning": warning_inspections,
            "pass_rate": pass_rate,
            "fail_rate": fail_rate,
            "warning_rate": warning_rate,
        },
        "defects": {
            "total": total_defects,
            "open": open_defects,
            "in_progress": in_progress_defects,
            "resolved": resolved_defects,
            "closed": closed_defects,
            "high": high_defects,
            "critical": critical_defects,
        },
    }, 200


def get_daily_quality_report(report_date=None):
    if report_date is None:
        target_date = date.today()
    else:
        try:
            target_date = datetime.fromisoformat(report_date).date()
        except ValueError:
            return {
                "error": "Invalid date format. Use YYYY-MM-DD."
            }, 400

    inspections = Inspection.query.all()
    defects = Defect.query.all()

    inspection_rows = []

    for inspection in inspections:
        if inspection.inspection_date.date() == target_date:
            inspection_rows.append({
                "id": inspection.id,
                "result": inspection.result.value,
                "product_id": inspection.product_id,
                "inspector_id": inspection.inspector_id,
            })

    defect_rows = []

    for defect in defects:
        if defect.detected_at.date() == target_date:
            defect_rows.append({
                "id": defect.id,
                "severity": defect.severity.value,
                "status": defect.status.value,
                "product_id": defect.product_id,
                "inspection_id": defect.inspection_id,
            })

    inspections_df = pd.DataFrame(inspection_rows)
    defects_df = pd.DataFrame(defect_rows)

    total_inspections = len(inspections_df)
    total_defects = len(defects_df)

    if total_inspections > 0:
        passed = int((inspections_df["result"] == "PASS").sum())
        failed = int((inspections_df["result"] == "FAIL").sum())
        warning = int((inspections_df["result"] == "WARNING").sum())

        pass_rate = round(passed / total_inspections * 100, 2)
        fail_rate = round(failed / total_inspections * 100, 2)
        warning_rate = round(warning / total_inspections * 100, 2)
    else:
        passed = 0
        failed = 0
        warning = 0
        pass_rate = 0
        fail_rate = 0
        warning_rate = 0

    if total_defects > 0:
        critical_defects = int((defects_df["severity"] == "CRITICAL").sum())
        high_defects = int((defects_df["severity"] == "HIGH").sum())
        open_defects = int((defects_df["status"] == "OPEN").sum())
    else:
        critical_defects = 0
        high_defects = 0
        open_defects = 0

    return {
        "report_date": target_date.isoformat(),
        "inspections": {
            "total": total_inspections,
            "passed": passed,
            "failed": failed,
            "warning": warning,
            "pass_rate": pass_rate,
            "fail_rate": fail_rate,
            "warning_rate": warning_rate,
        },
        "defects": {
            "total": total_defects,
            "open": open_defects,
            "high": high_defects,
            "critical": critical_defects,
        },
    }, 200


def get_product_quality_overview():
    products = Product.query.all()
    inspections = Inspection.query.all()
    defects = Defect.query.all()

    rows = []

    for product in products:
        product_inspections = []

        for inspection in inspections:
            if inspection.product_id == product.id:
                product_inspections.append(inspection)

        product_defects = []

        for defect in defects:
            if defect.product_id == product.id:
                product_defects.append(defect)

        total_inspections = len(product_inspections)
        total_defects = len(product_defects)

        passed = 0
        failed = 0
        warning = 0

        for inspection in product_inspections:
            if inspection.result == InspectionResultEnum.PASS:
                passed += 1
            elif inspection.result == InspectionResultEnum.FAIL:
                failed += 1
            elif inspection.result == InspectionResultEnum.WARNING:
                warning += 1

        critical_defects = 0
        open_defects = 0

        for defect in product_defects:
            if defect.severity == DefectSeverityEnum.CRITICAL:
                critical_defects += 1

            if defect.status == DefectStatusEnum.OPEN:
                open_defects += 1

        if total_inspections > 0:
            pass_rate = round(passed / total_inspections * 100, 2)
            defect_rate = round(total_defects / total_inspections * 100, 2)
        else:
            pass_rate = 0
            defect_rate = 0

        rows.append({
            "product_id": product.id,
            "product_code": product.product_code,
            "name": product.name,
            "total_inspections": total_inspections,
            "passed": passed,
            "failed": failed,
            "warning": warning,
            "pass_rate": pass_rate,
            "total_defects": total_defects,
            "open_defects": open_defects,
            "critical_defects": critical_defects,
            "defect_rate": defect_rate,
        })

    return rows, 200


def get_inspector_performance_report():
    inspectors = Inspector.query.all()
    inspections = Inspection.query.all()

    rows = []

    for inspector in inspectors:
        inspector_inspections = []

        for inspection in inspections:
            if inspection.inspector_id == inspector.id:
                inspector_inspections.append(inspection)

        total_inspections = len(inspector_inspections)

        passed = 0
        failed = 0
        warning = 0

        for inspection in inspector_inspections:
            if inspection.result == InspectionResultEnum.PASS:
                passed += 1
            elif inspection.result == InspectionResultEnum.FAIL:
                failed += 1
            elif inspection.result == InspectionResultEnum.WARNING:
                warning += 1

        if total_inspections > 0:
            pass_rate = round(passed / total_inspections * 100, 2)
            fail_rate = round(failed / total_inspections * 100, 2)
            warning_rate = round(warning / total_inspections * 100, 2)
        else:
            pass_rate = 0
            fail_rate = 0
            warning_rate = 0

        rows.append({
            "inspector_id": inspector.id,
            "employee_number": inspector.employee_number,
            "first_name": inspector.first_name,
            "last_name": inspector.last_name,
            "department": inspector.department,
            "role": inspector.role,
            "total_inspections": total_inspections,
            "passed": passed,
            "failed": failed,
            "warning": warning,
            "pass_rate": pass_rate,
            "fail_rate": fail_rate,
            "warning_rate": warning_rate,
        })

    return rows, 200


def get_quality_alerts():
    defects = Defect.query.all()

    alerts = []

    for defect in defects:
        if defect.severity == DefectSeverityEnum.CRITICAL and defect.status != DefectStatusEnum.CLOSED:
            alerts.append({
                "alert_type": "CRITICAL_DEFECT_OPEN",
                "message": "Critical defect is not closed.",
                "defect_id": defect.id,
                "defect_code": defect.defect_code,
                "defect_type": defect.defect_type,
                "status": defect.status.value,
                "severity": defect.severity.value,
                "product_id": defect.product_id,
                "inspection_id": defect.inspection_id,
            })

        if defect.status == DefectStatusEnum.RESOLVED and defect.resolved_at is None:
            alerts.append({
                "alert_type": "RESOLVED_WITHOUT_RESOLVED_DATE",
                "message": "Defect status is RESOLVED, but resolved_at is empty.",
                "defect_id": defect.id,
                "defect_code": defect.defect_code,
                "defect_type": defect.defect_type,
                "status": defect.status.value,
                "severity": defect.severity.value,
                "product_id": defect.product_id,
                "inspection_id": defect.inspection_id,
            })

        if defect.status in [DefectStatusEnum.RESOLVED, DefectStatusEnum.CLOSED] and not defect.corrective_action:
            alerts.append({
                "alert_type": "CLOSED_OR_RESOLVED_WITHOUT_CORRECTIVE_ACTION",
                "message": "Defect is resolved or closed, but corrective_action is empty.",
                "defect_id": defect.id,
                "defect_code": defect.defect_code,
                "defect_type": defect.defect_type,
                "status": defect.status.value,
                "severity": defect.severity.value,
                "product_id": defect.product_id,
                "inspection_id": defect.inspection_id,
            })

    return {
        "total_alerts": len(alerts),
        "alerts": alerts,
    }, 200