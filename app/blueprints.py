from flask import Flask

from app.routes.product import product_bp
from app.routes.defect import defect_bp
from app.routes.inspector import inspector_bp
from app.routes.inspection import inspection_bp
from app.routes.report import report_bp


def register_blueprints(app: Flask):
    app.register_blueprint(product_bp, url_prefix="/product")
    app.register_blueprint(defect_bp, url_prefix="/defect")
    app.register_blueprint(inspection_bp, url_prefix="/inspection")
    app.register_blueprint(inspector_bp, url_prefix="/inspector")
    app.register_blueprint(report_bp, url_prefix="/report")

