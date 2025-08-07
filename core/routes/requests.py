from flask import Blueprint, request, jsonify
from core.models import CertificateRequestModel
from bson import ObjectId

requests_bp = Blueprint("requests", __name__, url_prefix="/api/requests")


@requests_bp.route("/", methods=["POST"])
def create_request():
    data = request.json
    template_id = data.get("template_id")
    names = data.get("names", [])

    if not template_id or not names:
        return jsonify({"error": "Template ID and names are required"}), 400

    request_id = CertificateRequestModel.create(
        user_id=None, template_id=template_id, names=names
    )
    return jsonify({"request_id": request_id}), 201


@requests_bp.route("/<request_id>", methods=["GET"])
def get_requests(request_id):
    doc = CertificateRequestModel.collection.find_one({"_id": ObjectId(request_id)})

    if not doc:
        return jsonify({"error": "Request not found"}), 404

    doc["_id"] = str(doc["_id"])
    doc["template_id"] = str(doc["template_id"]) if doc["template_id"] else None
    doc["certificates"] = [str(cid) for cid in doc.get("certificates", [])]

    return jsonify(doc), 200

@requests_bp.route("/", methods=["GET"])
def list_requests():
    docs = CertificateRequestModel.get_collection().find().sort("timestamp", -1)
    result = []
    
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        doc["template_id"] = str(doc["template_id"]) if doc["template_id"] else None
        doc["certificates"] = [str(cid) for cid in doc.get("certificates", [])]
        result.append(doc)
    return jsonify(result), 200
