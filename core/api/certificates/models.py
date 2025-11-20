from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from core.config import Config

class CertificateModel:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.certificates_collection = self.db[Config.CERTIFICATES_COLLECTION_NAME]

    def cert_col(self):
        return self.certificates_collection

    def create_certificate(self, request_id: str, name: str, image_url: str):
        cert = {
            "name": name,
            "request_id": ObjectId(request_id),
            "image_url": image_url,
            "created_at": datetime.utcnow(),
        }

        result = self.cert_col().insert_one(cert)
        return str(result.inserted_id)

    def get_certificate_by_id(self, certificate_id: str):
        return self.cert_col().find_one({"_id": ObjectId(certificate_id)})

    def get_certificates(self):
        return list(self.cert_col().find())

    def remove_certificates(self, certificate_id: str):
        try:
            res = self.cert_col().delete_one({"_id": ObjectId(certificate_id)})
            return res.deleted_count > 0
        except:
            return False
