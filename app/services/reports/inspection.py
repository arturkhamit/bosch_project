from io import BytesIO

import pandas as pd

from app.models.inspection import Inspection
from app.services.inspection_service import create_inspections_from_json


def get_inspection_summary_report():
    inspections = Inspection.query.all()

    rows = []

    for inspection in inspections:
        rows.append({
            "id": inspection.id,
            "batch_number": inspection.batch_number,
            "serial_number": inspection.serial_number,
            "inspection_date": inspection.inspection_date,
            "result": inspection.result.value,
            "product_id": inspection.product_id,
            "inspector_id": inspection.inspector_id,
        })

    if not rows:
        return {
            "total_inspections": 0,
            "pass_count": 0,
            "fail_count": 0,
            "warning_count": 0,
            "pass_rate": 0,
            "fail_rate": 0,
            "warning_rate": 0,
        }, 200

    df = pd.DataFrame(rows)

    total_inspections = len(df)

    pass_count = int((df["result"] == "PASS").sum())
    fail_count = int((df["result"] == "FAIL").sum())
    warning_count = int((df["result"] == "WARNING").sum())

    return {
        "total_inspections": total_inspections,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "warning_count": warning_count,
        "pass_rate": round(pass_count / total_inspections * 100, 2),
        "fail_rate": round(fail_count / total_inspections * 100, 2),
        "warning_rate": round(warning_count / total_inspections * 100, 2),
    }, 200


def export_inspections_report(file_format):
    inspections = Inspection.query.all()

    rows = []

    for inspection in inspections:
        rows.append({
            "id": inspection.id,
            "batch_number": inspection.batch_number,
            "serial_number": inspection.serial_number,
            "inspection_date": inspection.inspection_date.isoformat() if inspection.inspection_date else None,
            "result": inspection.result.value,
            "notes": inspection.notes,
            "product_id": inspection.product_id,
            "inspector_id": inspection.inspector_id,
            "created_at": inspection.created_at.isoformat() if inspection.created_at else None,
        })

    df = pd.DataFrame(rows)

    if file_format == "csv":
        stream = BytesIO(df.to_csv(index=False).encode("utf-8"))
        stream.seek(0)

        return {
            "file": stream,
            "filename": "inspections.csv",
            "mimetype": "text/csv",
        }, 200

    if file_format == "xlsx":
        stream = BytesIO()

        with pd.ExcelWriter(stream, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="inspections")

        stream.seek(0)

        return {
            "file": stream,
            "filename": "inspections.xlsx",
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }, 200

    return {
        "error": "Unsupported export format. Use csv or xlsx."
    }, 400


def import_inspections_from_file(file):
    df = _read_file(file)

    if isinstance(df, tuple):
        return df

    required_columns = [
        "batch_number",
        "serial_number",
        "inspection_date",
        "result",
        "product_id",
        "inspector_id",
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

    df["inspection_date"] = pd.to_datetime(
        df["inspection_date"],
        errors="coerce",
    )

    df["inspection_date"] = df["inspection_date"].apply(
        lambda value: value.isoformat() if pd.notna(value) else None
    )

    inspections = df.to_dict("records")

    return create_inspections_from_json(inspections)


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