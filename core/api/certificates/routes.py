from flask import Blueprint, request, jsonify
from core.api.certificates.services import CertificateServices


class CertificatesRoutes:
    def __init__(self):
        self.certificate_services = CertificateServices()
        self.bp = Blueprint("certificates", __name__, url_prefix="/api/v2/certificates")
        self.register_routes()

    def register_routes(self):
        @self.bp.route("/", methods=["POST"])
        def generate_certificate():
            data = request.json or {}
            request_id = data.get("request_id")

            if not request_id:
                return jsonify({"error": "request_id is required"}), 400

            return self.certificate_services.generate_certificate(request_id)

        @self.bp.route("/download/<string:request_id>", methods=["GET"])
        def download_certificates(request_id):
            return self.certificate_services.download_certificates(request_id)

        @self.bp.route("/", methods=["GET"])
        def list_certificates():
            return self.certificate_services.list_certificates()

        @self.bp.route("/<string:certificate_id>", methods=["DELETE"])
        def delete_certificates(certificate_id):
            return self.certificate_services.remove_certificate(certificate_id)
