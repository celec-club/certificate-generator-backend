from flask import request, jsonify
from core.api.requests.models import CertificateRequestModel


class CertificateRequestServices:
    def __init__(self):
        self.certificate_request = CertificateRequestModel()

    def create_request(self):
        data = request.json or {}
        template_id = data.get("template_id")
        names = data.get("names", [])

        if not template_id or not names:
            return jsonify({"error": "Template ID and names are required"}), 400

        request_id = self.certificate_request.create_req(
            user_id=None, template_id=template_id, names=names
        )
        return jsonify({"request_id": request_id}), 201

    def get_requests(self, request_id):
        req = self.certificate_request.get_request_by_id(request_id)

        if not req:
            return jsonify({"error": "Request not found"}), 404

        result = {
            "_id": str(req["_id"]),
            "template_id": str(req["template_id"]) if req.get("template_id") else None,
            "names": req.get("names", []),
            "status": req.get("status"),
            "report_path": req.get("report_path"),
            "certificates": [str(c) for c in req.get("certificates", [])],
        }

        return jsonify(result), 200

    def get_all_requests(self):
        requests = self.certificate_request.get_all_requests()

        result = []
        for req in requests:
            result.append(
                {
                    "_id": str(req["_id"]),
                    "template_id": (
                        str(req["template_id"]) if req.get("template_id") else None
                    ),
                    "names": req.get("names", []),
                    "status": req.get("status"),
                    "certificates": [str(c) for c in req.get("certificates", [])],
                    "report_path": req.get("report_path"),
                    "timestamp": (
                        req.get("timestamp").isoformat()
                        if req.get("timestamp")
                        else None
                    ),
                }
            )

        return jsonify(result), 200
