from flask import request, jsonify
from core.api.templates.models import TemplateModel
import cloudinary as cd
import cloudinary.uploader as cu


class TemplateServices:
    def __init__(self):
        self.temp = TemplateModel()

    def upload_template(self):
        file = request.files.get("file")
        name = request.form.get("name")
        uploaded_by = request.form.get("uploaded_by")

        if not file:
            return jsonify({"error": "No file provided"}), 400

        if not name:
            return jsonify({"error": "Template name is required"}), 400

        try:
            upload_result = cu.upload(file)
            image_url = upload_result.get("secure_url")
            public_id = upload_result.get("public_id")

            template_id = self.temp.create_template(
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

        except cd.exceptions.Error as e:
            return jsonify({"error": str(e)}), 500

    def list_templates(self):
        templates = self.temp.get_all_templates()

        result = [
            {
                "_id": str(t["_id"]),
                "name": t.get("name"),
                "image_url": t.get("image_url"),
                "uploaded_by": (
                    str(t.get("uploaded_by")) if t.get("uploaded_by") else None
                ),
                "created_at": (
                    t.get("created_at").isoformat() if t.get("created_at") else None
                ),
            }
            for t in templates
        ]

        return jsonify(result), 200
