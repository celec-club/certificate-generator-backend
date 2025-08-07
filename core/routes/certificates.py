import os
import tempfile
from flask import Blueprint, request, jsonify, send_file
from core.models import CertificateRequestModel, CertificateModel, TemplateModel
from PIL import Image, ImageDraw, ImageFont
from bson import ObjectId
import zipfile
import io

certificates_bp = Blueprint("certificates", __name__, url_prefix="/api/certificates")
FONT_PATH = "arial.ttf"


@certificates_bp.route("/generate/<string:request_id>", methods=["POST"])
def generate_certificate(request_id):
    req = CertificateRequestModel.get_collection().find_one(
        {"_id": ObjectId(request_id)}
    )
    if not req:
        return jsonify({"error": "Request not found"}), 404

    template = TemplateModel.get(req["template_id"])
    if not template:
        return jsonify({"error": "Template not found"}), 404

    image_url = template["image_url"]
    names = req["names"]
    cert_ids = []

    temp_dir = tempfile.mkdtemp()
    font = ImageFont.truetype(FONT_PATH, 100)

    for name in names:
        with Image.open(image_url) as img:
            draw = ImageDraw.Draw(img)
            draw.text((500, 500), name, font=font, fill="black", align="center")

            output_path = os.path.join(temp_dir, f"{name}.png")
            img.save(output_path)

            cert_id = CertificateModel.create(
                request_id=request_id, name=name, image_url=output_path
            )
            CertificateRequestModel.add_certificate(request_id, cert_id)
            cert_ids.append(cert_id)

    CertificateRequestModel.update_status(request_id, "completed")

    return jsonify({"status": "done", "certificate_ids": cert_ids}), 200


@certificates_bp.route("/download/<string:request_id>", methods=["GET"])
def download_certificates(request_id):
    req = CertificateRequestModel.get_collection().find_one(
        {"_id": ObjectId(request_id)}
    )

    if not req or not req.get("certificates"):
        return jsonify({"error": "No certificates found for this request"}), 404

    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, "w") as zf:
        for cert_id in req["certificates"]:
            cert = CertificateModel.get_collection().find_one(
                {"_id": ObjectId(cert_id)}
            )
            if cert:
                file_path = cert["image_url"]
                file_name = f"{cert["name"]}.png"
                zf.write(file_path, file_name)

    memory_file.seek(0)
    return send_file(
        memory_file,
        download_name=f"certificates_{request_id}.zip",
        as_attachment=True,
        mimetype="application/zip",
    )


@certificates_bp.route("/", methods=["GET"])
def list_certificates():
    return jsonify(
        {
            "message": "This endpoint returns a ZIP file. Use 'Send and Download' in Postman or a direct download tool to retrieve it."
        }
    ), 405
