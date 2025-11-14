import os
import tempfile
import requests
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

    try:
        # Download template image once
        response = requests.get(image_url)
        response.raise_for_status()
        base_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        return jsonify({"error": f"Failed to fetch template image: {e}"}), 500

    image_width, image_height = base_img.size
    font_size = max(20, min(int(image_width * 0.05), 120))
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except IOError:
        font = ImageFont.load_default()

    for name in names:
        img = base_img.copy()
        draw = ImageDraw.Draw(img)

        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = (image_width - text_width) // 2
        y = (image_height - text_height) // 2

        draw.text((x, y), name, font=font, fill="black", align="center")

        output_path = os.path.join(temp_dir, f"{name}.png")
        img.save(output_path)

        cert_id = CertificateModel.create(
            request_id=request_id, name=name, image_url=output_path
        )
        CertificateRequestModel.add_certificate(request_id, cert_id)
        cert_ids.append(cert_id)

    # Save TXT report
    report_path = os.path.join(temp_dir, "names.txt")
    with open(report_path, "w", encoding="utf-8") as report_file:
        for name in names:
            report_file.write(name + "\n")

    # Update request with report path & status
    CertificateRequestModel.update_report_path(request_id, report_path)
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
        # Add certificate images
        for cert_id in req["certificates"]:
            cert = CertificateModel.get_collection().find_one(
                {"_id": ObjectId(cert_id)}
            )
            if cert:
                file_path = cert["image_url"]
                file_name = f"{cert['name']}.png"
                zf.write(file_path, file_name)

        # Add names.txt if available
        report_path = req.get("report_path")
        if report_path and os.path.exists(report_path):
            zf.write(report_path, arcname="names.txt")

    memory_file.seek(0)
    return send_file(
        memory_file,
        download_name=f"certificates_{request_id}.zip",
        as_attachment=True,
        mimetype="application/zip",
    )


@certificates_bp.route("/", methods=["GET"])
def list_certificates():
    certificates = CertificateModel.get_collection().find()
    result = []

    for cert in certificates:
        cert["_id"] = str(cert["_id"])
        cert["request_id"] = str(cert["request_id"]) if cert["request_id"] else None
        result.append(cert)

    return jsonify(result), 200


@certificates_bp.route("/<string:certificate_id>", methods=["DELETE"])
def remove_certificates(certificate_id):
    rv_certificate = CertificateModel.get_collection().find_one_and_delete(
        {"_id": ObjectId(certificate_id)}
    )

    # Checking if the certificate exist or not
    if not rv_certificate:
        return jsonify({"error": f"No certificate found with id {certificate_id}"}), 404

    # Convert ObjectIds to strings
    rv_certificate["_id"] = str(rv_certificate["_id"])
    rv_certificate["request_id"] = (
        str(rv_certificate["request_id"]) if rv_certificate.get("request_id") else None
    )

    return (
        jsonify(
            {
                "success": f"Deleted certificate with id {rv_certificate['_id']} successfully"
            }
        ),
        200,
    )
