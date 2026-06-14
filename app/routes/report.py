from flask import Blueprint, jsonify, request, send_file

from app.services.reports.defect import (
    get_defect_pareto_report,
    get_open_defects_report,
    export_defects_report,
)
from app.services.reports.inspection import (
    get_inspection_summary_report,
    export_inspections_report,
)

from app.services.reports.report import (
    get_quality_summary,
    get_daily_quality_report,
    get_product_quality_overview,
    get_inspector_performance_report,
    get_quality_alerts,
)


report_bp = Blueprint("report_bp", __name__)

@report_bp.route("/quality-summary", methods=["GET"])
def quality_summary():
    result, status_code = get_quality_summary()

    return jsonify(result), status_code


@report_bp.route("/daily-quality", methods=["GET"])
def daily_quality():
    report_date = request.args.get("date")

    result, status_code = get_daily_quality_report(report_date)

    return jsonify(result), status_code


@report_bp.route("/product-quality", methods=["GET"])
def product_quality():
    result, status_code = get_product_quality_overview()

    return jsonify(result), status_code


@report_bp.route("/inspector-performance", methods=["GET"])
def inspector_performance():
    result, status_code = get_inspector_performance_report()

    return jsonify(result), status_code


@report_bp.route("/quality-alerts", methods=["GET"])
def quality_alerts():
    result, status_code = get_quality_alerts()

    return jsonify(result), status_code

@report_bp.route("/defect-pareto", methods=["GET"])
def defect_pareto():
    group_by = request.args.get("group_by", "defect_type")

    result, status_code = get_defect_pareto_report(group_by)

    return jsonify(result), status_code


@report_bp.route("/inspection-summary", methods=["GET"])
def inspection_summary():
    result, status_code = get_inspection_summary_report()

    return jsonify(result), status_code

@report_bp.route("/open-defects", methods=["GET"])
def open_defects():
    result, status_code = get_open_defects_report()

    return jsonify(result), status_code


@report_bp.route("/export/defects", methods=["GET"])
def export_defects():
    file_format = request.args.get("format", "xlsx")

    result, status_code = export_defects_report(file_format)

    if status_code != 200:
        return jsonify(result), status_code

    return send_file(
        result["file"],
        mimetype=result["mimetype"],
        as_attachment=True,
        download_name=result["filename"],
    )


@report_bp.route("/export/inspections", methods=["GET"])
def export_inspections():
    file_format = request.args.get("format", "xlsx")

    result, status_code = export_inspections_report(file_format)

    if status_code != 200:
        return jsonify(result), status_code

    return send_file(
        result["file"],
        mimetype=result["mimetype"],
        as_attachment=True,
        download_name=result["filename"],
    )