import pandas as pd

from app.services.inspector_service import create_inspectors_from_json


def import_inspectors_from_file(file):
    df = _read_file(file)

    if isinstance(df, tuple):
        return df

    required_columns = [
        "employee_number",
        "first_name",
        "last_name",
        "email",
        "role",
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

    inspectors = df.to_dict("records")

    return create_inspectors_from_json(inspectors)


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