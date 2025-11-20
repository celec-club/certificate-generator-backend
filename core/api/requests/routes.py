from flask import Blueprint
from core.api.requests.services import CertificateRequestServices


class CertificateRequestRoutes:
    def __init__(self):
        self.certificate_requests = CertificateRequestServices()
        self.bp = Blueprint("requests", __name__, url_prefix="/api/v2/requests")
        self.register_routes()

    def register_routes(self):
        @self.bp.route("/", methods=["POST"])
        def create_request():
            return self.certificate_requests.create_request()

        @self.bp.route("/<string:request_id>", methods=["GET"])
        def get_req_by_id(request_id):
            return self.certificate_requests.get_requests(request_id)

        @self.bp.route("/", methods=["GET"])
        def list_requests():
            return self.certificate_requests.get_all_requests()
