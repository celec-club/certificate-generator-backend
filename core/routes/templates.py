from flask import Blueprint, request, jsonify
from core.models import TemplateModel
from werkzeug.utils import secure_filename
from datetime import datetime
import cloudinary
import cloudinary.uploader

templates_bp = Blueprint("templates", __name__, url_prefix="/api/templates")


@templates_bp.route("/", methods=["POST"])
def upload_template():
    file = request.files.get("file")
    name = request.form.get("name")
    uploaded_by = request.form.get("uploaded_by")

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(file=file)
        image_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")

        # Save to DB
        template_id = TemplateModel.create(
            name=name, image_url=image_url, uploaded_by=uploaded_by
        )

        return (
            jsonify(
                {
                    "template_id": template_id,
                    "image_url": image_url,
                    "public_id": public_id,
                }
            ),
            201,
        )
    except cloudinary.exceptions.Error as e:
        return jsonify({"error": str(e)}), 500


@templates_bp.route("/", methods=["GET"])
def list_templates():
    templates = TemplateModel.get_all()
    result = []

    for template in templates:
        result.append(
            {
                "_id": str(template["_id"]),
                "name": template.get("name"),
                "image_url": template.get("image_url"),
                "created_at": (
                    template.get("created_at").isoformat()
                    if template.get("created_at")
                    else None
                ),
            }
        )

    return jsonify(result), 200
