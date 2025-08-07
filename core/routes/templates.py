import os
from flask import Blueprint, request, jsonify
from core.models import TemplateModel
from werkzeug.utils import secure_filename
from datetime import datetime

templates_bp = Blueprint("templates", __name__, url_prefix="/api/templates")

# Ensure the upload directory exists
UPLOAD_DIR = "uploads/templates"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@templates_bp.route("/", methods=["POST"])
def upload_template():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_name = secure_filename(file.filename)
    if not file_name:
        return jsonify({"error": "Invalid filename"}), 400

    # Save file with timestamp prefix
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_name = f"{timestamp}_{file_name}"
    file_path = os.path.join(UPLOAD_DIR, saved_name)
    file.save(file_path)

    # Save metadata in DB
    template_id = TemplateModel.create(name=file_name, image_url=file_path)
    return jsonify({"template_id": template_id}), 201


@templates_bp.route("/", methods=["GET"])
def list_templates():
    templates = TemplateModel.get_all()
    result = []

    for template in templates:
        result.append({
            "_id": str(template["_id"]),
            "name": template.get("name"),
            "image_url": template.get("image_url"),
            "created_at": template.get("created_at").isoformat() if template.get("created_at") else None
        })

    return jsonify(result), 200
