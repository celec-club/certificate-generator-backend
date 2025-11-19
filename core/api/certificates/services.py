import os, tempfile, requests, io, zipfile
from PIL import Image, ImageDraw, ImageFont
from flask import jsonify, send_file
from bson import ObjectId

from core.api.certificates.models import CertificateModel
from core.api.requests.models import CertificateRequestModel
from core.api.templates.models import TemplateModel


FONT_PATH = "arial.ttf"


class CertificateServices:
    def __init__(self):
        self.certificate_model = CertificateModel()
        self.certificate_request = CertificateRequestModel()
        self.template_model = TemplateModel()

    def generate_certificate(self, request_id):
        request_data = self.certificate_request.get_request_by_id(request_id)

        if not request_data:
            return jsonify({"error": "Request not found"}), 404

        template = self.template_model.get_template_by_id(
            str(request_data["template_id"])
        )
        if not template:
            return jsonify({"error": "Template not found"}), 404

        image_url = template["image_url"]
        names = request_data.get("names", [])
        cert_ids = []

        template_dir = tempfile.mkdtemp()

        # Download template image
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            base_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        except Exception as e:
            return jsonify({"error": f"Failed to fetch template image: {e}"}), 500

        image_width, image_height = base_img.size

        # Font
        font_size = max(20, min(int(image_width * 0.05), 120))
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            font = ImageFont.load_default()

        for name in names:
            image = base_img.copy()
            draw = ImageDraw.Draw(image)

            text_bbox = draw.textbbox((0, 0), name, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]

            x = (image_width - text_w) // 2
            y = (image_height - text_h) // 2

            draw.text((x, y), name, fill="black", font=font)

            output_path = os.path.join(template_dir, f"{name}.png")
            image.save(output_path)

            cert_id = self.certificate_model.create_certificate(
                request_id=request_id, name=name, image_url=output_path
            )

            self.certificate_request.add_certificate_to_list(request_id, cert_id)
            cert_ids.append(cert_id)

        # Save report
        report_path = os.path.join(template_dir, "names.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.writelines([n + "\n" for n in names])

        self.certificate_request.update_report_path(request_id, report_path)
        self.certificate_request.update_status(request_id, "completed")

        return jsonify({"status": "done", "certificate_ids": cert_ids}), 200

    def download_certificates(self, request_id):
        req = self.certificate_request.download_certificate(request_id)

        if not req or not req.get("certificates"):
            return jsonify({"error": "No certificates found"}), 404

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, "w") as zf:
            for cid in req["certificates"]:
                cert = self.certificate_model.get_certificate_by_id(str(cid))
                if cert and os.path.exists(cert["image_url"]):
                    zf.write(cert["image_url"], arcname=f"{cert['name']}.png")

            if req.get("report_path") and os.path.exists(req["report_path"]):
                zf.write(req["report_path"], arcname="names.txt")

        memory_file.seek(0)

        return send_file(
            memory_file,
            as_attachment=True,
            download_name=f"certificates_{request_id}.zip",
            mimetype="application/zip",
        )

    def list_certificates(self):
        certificates = self.certificate_model.get_certificates()

        result = []
        for cert in certificates:
            result.append(
                {
                    "_id": str(cert["_id"]),
                    "request_id": str(cert["request_id"]),
                    "name": cert["name"],
                    "image_url": cert["image_url"],
                    "created_at": (
                        cert["created_at"].isoformat()
                        if cert.get("created_at")
                        else None
                    ),
                }
            )

        return jsonify(result), 200

    def remove_certificate(self, certificate_id):
        deleted = self.certificate_model.remove_certificates(certificate_id)

        if not deleted:
            return jsonify({"error": f"Certificate {certificate_id} not found"}), 404

        return jsonify({"success": f"Certificate {certificate_id} deleted"}), 200
