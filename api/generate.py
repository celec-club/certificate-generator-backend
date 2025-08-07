from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import tempfile
import base64


def handler(request):
    try:
        # Read uploaded files
        template_file = request.files["template"]
        names_file = request.files["names"]

        # Save to temp
        temp_dir = tempfile.mkdtemp()
        template_path = os.path.join(temp_dir, "template.png")
        template_file.save(template_path)

        # Read names depending on file extension
        names = [
            line.decode("utf-8").strip()
            for line in names_file.readlines()
            if line.strip()
        ]

        # Font path
        font = Image.font.truetype("arial.ttf", 100)

        # Output one certificate as test
        name = names[0] if names else "Default Name"
        with Image.open(template_path) as img:
            draw = ImageDraw.Draw(img)
            draw.text((500, 500), name, fill="black", font=font, align="center")
            output_path = os.path.join(temp_dir, f"{name}.png")
            img.save(output_path)

        # Return image as base64
        with open(output_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode("utf-8")

        return {
            "statusCode": 200,
            "body": encoded_string,
            "headers": {
                "Content-Type": "image/png",
                "Access-Control-Allow-Origin": "*",
            },
            "isBase64Encoded": True
        }
    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
