from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
from zipfile import ZipFile
import uuid

app = Flask(__name__)
OUTPUT_FOLDER = "static/certificates"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate():
    template = request.files['template']
    names_file = request.files['names']

    # Read names depending on file extension
    ext = names_file.filename.rsplit('.', 1)[-1].lower()
    
    if ext == 'txt':
        names = [line.strip() for line in names_file.readlines() if line.strip()]
        names = [name.decode('utf-8') if isinstance(name, bytes) else name for name in names]
    elif ext in ['xls', 'xlsx']:
        df = pd.read_excel(names_file)
        if 'name' in df.columns:
            names = df['name'].dropna().tolist()
        else:
            return "Error: Excel file must contain a 'name' column."
    else:
        return "Unsupported file format. Upload a .txt or .xls/.xlsx file."

    # Save template temporarily
    template_path = os.path.join(OUTPUT_FOLDER, "template.png")
    template.save(template_path)

    # Create unique output directory
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(OUTPUT_FOLDER, session_id)
    os.makedirs(session_dir, exist_ok=True)

    # Load font (you must have arial.ttf or use an available one)
    font = ImageFont.truetype("arial.ttf", 100)
    text_align = "center"

    # Generate certificates
    for name in names:
        with Image.open(template_path) as img:
            draw = ImageDraw.Draw(img)
            draw.text((500, 500), name, fill="black", font=font, align=text_align)
            output_path = os.path.join(session_dir, f"{name}.png")
            img.save(output_path)

    # Zip the output
    zip_path = os.path.join(OUTPUT_FOLDER, f"{session_id}.zip")
    with ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(session_dir):
            file_path = os.path.join(session_dir, filename)
            zipf.write(file_path, arcname=filename)

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
