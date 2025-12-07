import os, tempfile, requests, io, zipfile
from PIL import Image, ImageDraw, ImageFont
from flask import jsonify, send_file


from core.api.certificates.models import CertificateModel
from core.api.requests.models import CertificateRequestModel
from core.api.templates.models import TemplateModel

import cv2
import numpy as np
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
            pil_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        except Exception as e:
            return jsonify({"error": f"Failed to fetch template image: {e}"}), 500

        img_width, img_height = pil_img.size

        for name in names:
########################################################################################################################################################""            
                        #pil to cv2
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGR)
            line_y = 300  
            color = (29, 36, 68) 
            max_font_scale = 0.8  
            thickness = 1
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            (text_w, text_h), baseline = cv2.getTextSize(name, font, font_scale, thickness)
            #limit
            if text_w > 0 and text_h > 0:
                font_scale = min(font_scale * (img_width * 0.5 / text_w), max_font_scale)
            (text_w, text_h), baseline = cv2.getTextSize(name, font, font_scale, thickness)
            #center H V
            x = (img_width - text_w) // 2
            y = line_y
            #name
            cv2.putText(cv_img, name, (x, y), font, font_scale, color, thickness, lineType=cv2.LINE_AA)
            output_path = os.path.join(template_dir, f"{name}.png")
            cv2.imwrite(output_path, cv_img)
#########################################################################################################################################################################
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
            return jsonify({"error": f"Certificate with id '{certificate_id}' not found"}), 404

        return jsonify({"success": f"Certificate with id '{certificate_id}' deleted successfully"}), 200
