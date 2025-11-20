from flask import Blueprint
from core.api.templates.services import TemplateServices


class TemplateRoutes:
    def __init__(self):
        self.template_services = TemplateServices()
        self.bp = Blueprint("templates", __name__, url_prefix="/api/v2/templates")
        self.register_routes()

    def register_routes(self):
        @self.bp.route("/", methods=["POST"])
        def upload_template():
            return self.template_services.upload_template()

        @self.bp.route("/", methods=["GET"])
        def list_templates():
            return self.template_services.list_templates()
