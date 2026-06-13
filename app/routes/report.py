from flask import Blueprint, request, jsonify

from app.services.report import (get_quality_summary, )

report_bp = Blueprint("report_bp", __name__)

@report_bp.route("/report", methods=["GET"])
def quality_summary():
    summary = get_quality_summary()

    return jsonify(summary)