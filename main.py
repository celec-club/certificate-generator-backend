import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from core.api.certificates.routes import CertificateRoutes
from core.api.requests.routes import CertificateRequestRoutes
from core.api.templates.routes import TemplateRoutes

app = Flask(__name__)

# -------------------------------
# Initialize CORS
# -------------------------------
CORS(
    app,
    origins=["http://localhost:5173"],
    supports_credentials=True,
)

# -------------------------------
# Register blueprints
# -------------------------------
certificates_routes = CertificateRoutes()
certificate_requests_routes = CertificateRequestRoutes()
template_routes = TemplateRoutes()

app.register_blueprint(certificates_routes.bp)
app.register_blueprint(certificate_requests_routes.bp)
app.register_blueprint(template_routes.bp)


# -------------------------------
# Browser Routes
# -------------------------------
@app.route("/")
def index():
    return jsonify({"service": "Certificate Generator Backend", "status": "online"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
