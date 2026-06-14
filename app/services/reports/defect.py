from io import BytesIO

import pandas as pd

from app.models.defect import Defect
from app.models.enums import DefectStatusEnum
from app.services.defect_service import create_defects_from_json


def get_defect_pareto_report(group_by="defect_type"):
    allowed_group_fields = [
        "defect_code",
        "defect_type",
        "severity",
        "status",
        "product_id",
        "inspection_id",
    ]

    if group_by not in allowed_group_fields:
        return {
            "error": "Invalid group_by value.",
            "allowed_group_fields": allowed_group_fields,
        }, 400

    defects = Defect.query.all()

    rows = []

    for defect in defects:
        rows.append({
            "defect_code": defect.defect_code,
            "defect_type": defect.defect_type,
            "severity": defect.severity.value,
            "status": defect.status.value,
            "product_id": defect.product_id,
            "inspection_id": defect.inspection_id,
        })

    if not rows:
        return [], 200

    df = pd.DataFrame(rows)

    pareto = (
        df.groupby(group_by)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    total = pareto["count"].sum()

    pareto["percentage"] = (pareto["count"] / total * 100).round(2)
    pareto["cumulative_percentage"] = pareto["percentage"].cumsum().round(2)

    return pareto.to_dict("records"), 200


def get_open_defects_report():
    rows = Defect.query.with_entities(
        Defect.id,
        Defect.defect_code,
        Defect.defect_type,
        Defect.severity,
        Defect.status,
        Defect.description,
        Defect.detected_at,
        Defect.resolved_at,
        Defect.root_cause,
        Defect.corrective_action,
        Defect.product_id,
        Defect.inspection_id,
    ).filter(
        Defect.status.in_([
            DefectStatusEnum.OPEN,
            DefectStatusEnum.IN_PROGRESS,
        ])
    ).all()

    if not rows:
        return [], 200

    df = pd.DataFrame([
        {
            "id": row.id,
            "defect_code": row.defect_code,
            "defect_type": row.defect_type,
            "severity": row.severity.value,
            "status": row.status.value,
            "description": row.description,
            "detected_at": row.detected_at.isoformat() if row.detected_at else None,
            "resolved_at": row.resolved_at.isoformat() if row.resolved_at else None,
            "root_cause": row.root_cause,
            "corrective_action": row.corrective_action,
            "product_id": row.product_id,
            "inspection_id": row.inspection_id,
        }
        for row in rows
    ])


    df = df.sort_values(
        by=["severity", "detected_at"],
        ascending=[True, True],
    )

    return df.to_dict("records"), 200


def export_defects_report(file_format):
    rows = Defect.query.with_entities(
        Defect.id,
        Defect.defect_code,
        Defect.defect_type,
        Defect.severity,
        Defect.status,
        Defect.description,
        Defect.detected_at,
        Defect.resolved_at,
        Defect.root_cause,
        Defect.corrective_action,
        Defect.product_id,
        Defect.inspection_id,
        Defect.created_at,
    ).all()

    df = pd.DataFrame([
        {
            "id": row.id,
            "defect_code": row.defect_code,
            "defect_type": row.defect_type,
            "severity": row.severity.value,
            "status": row.status.value,
            "description": row.description,
            "detected_at": row.detected_at.isoformat() if row.detected_at else None,
            "resolved_at": row.resolved_at.isoformat() if row.resolved_at else None,
            "root_cause": row.root_cause,
            "corrective_action": row.corrective_action,
            "product_id": row.product_id,
            "inspection_id": row.inspection_id,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ])

    if file_format == "csv":
        stream = BytesIO(df.to_csv(index=False).encode("utf-8"))
        stream.seek(0)

        return {
            "file": stream,
            "filename": "defects.csv",
            "mimetype": "text/csv",
        }, 200

    if file_format == "xlsx":
        stream = BytesIO()

        with pd.ExcelWriter(stream, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="defects")

        stream.seek(0)

        return {
            "file": stream,
            "filename": "defects.xlsx",
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }, 200

    return {
        "error": "Unsupported export format. Use csv or xlsx."
    }, 400


def import_defects_from_file(file):
    df = _read_file(file)

    if isinstance(df, tuple):
        return df

    required_columns = [
        "defect_code",
        "defect_type",
        "severity",
        "status",
        "description",
        "detected_at",
        "product_id",
        "inspection_id",
    ]

    missing_columns = []

    for column in required_columns:
        if column not in df.columns:
            missing_columns.append(column)

    if missing_columns:
        return {
            "error": "Missing required columns.",
            "missing_columns": missing_columns,
        }, 400

    df = df.where(pd.notna(df), None)

    df["detected_at"] = pd.to_datetime(
        df["detected_at"],
        errors="coerce",
    )

    df["detected_at"] = df["detected_at"].apply(
        lambda value: value.isoformat() if pd.notna(value) else None
    )

    if "resolved_at" in df.columns:
        df["resolved_at"] = pd.to_datetime(
            df["resolved_at"],
            errors="coerce",
        )

        df["resolved_at"] = df["resolved_at"].apply(
            lambda value: value.isoformat() if pd.notna(value) else None
        )

    defects = df.to_dict("records")

    return create_defects_from_json(defects)


def _read_file(file):
    filename = file.filename.lower()

    try:
        if filename.endswith(".csv"):
            return pd.read_csv(file)

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            return pd.read_excel(file)

        return {
            "error": "Unsupported file format. Use CSV, XLSX, or XLS."
        }, 400

    except Exception as error:
        return {
            "error": "Could not read uploaded file.",
            "details": str(error),
        }, 400