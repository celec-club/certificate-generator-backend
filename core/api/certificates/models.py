from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from config import Config


class CertificateModel:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.certificates_collection = self.db[Config.CERTIFICATES_COLLECTION_NAME]

    def get_collection(self):
        return self.certificates_collection

    def create_certificate(self, request_id: str, name: str, image_url: str):
        cert = {
            "name": name,
            "request_id": ObjectId(request_id),
            "image_url": image_url,
            "created_at": datetime.utcnow(),
        }

        result = self.get_collection().insert_one(cert)
        return str(result.inserted_id)

    def get_certificate_by_id(self, certificate_id: str):
        return self.get_collection().find_one({"_id": ObjectId(certificate_id)})

    def get_certificates(self):
        return self.get_collection().find()

    def remove_certificates(self, certificate_id: str):
        try:
            res = self.get_collection().delete_one({"_id": ObjectId(certificate_id)})
            return res.deleted_count > 0
        except Exception as e:
            print(f"Error deleting certificate with id {certificate_id}: {e}")
            return False
