from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from core.routes.requests import requests_bp
from core.routes.templates import templates_bp
from core.routes.certificates import certificates_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(requests_bp, )
app.register_blueprint(certificates_bp)
app.register_blueprint(templates_bp)


@app.route("/", methods=["GET"])
def index():
    return jsonify({"service": "Certificate Generator Backend", "status": "online"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
