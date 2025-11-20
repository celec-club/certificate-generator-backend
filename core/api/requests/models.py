from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from core.config import Config


class CertificateRequestModel:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.certificate_request = self.db[Config.REQUESTS_COLLECTION_NAME]

    def requests(self):
        return self.certificate_request

    def create_req(self, user_id: str, template_id: str, names):
        doc = {
            "user_id": ObjectId(user_id) if user_id else None,
            "template_id": ObjectId(template_id) if template_id else None,
            "names": names or [],
            "timestamp": datetime.utcnow(),
            "status": "pending",
            "certificates": [],
            "report_path": None,
        }

        result = self.requests().insert_one(doc)
        return str(result.inserted_id)

    def update_report_path(self, req_id, path):
        r = self.requests().update_one(
            {"_id": ObjectId(req_id)}, {"$set": {"report_path": path}}
        )
        return r.modified_count > 0

    def update_status(self, req_id, status):
        r = self.requests().update_one(
            {"_id": ObjectId(req_id)}, {"$set": {"status": status}}
        )
        return r.modified_count > 0

    def add_certificate_to_list(self, req_id, cert_id):
        r = self.certificate_request.update_one(
            {"_id": ObjectId(req_id)}, {"$push": {"certificates": ObjectId(cert_id)}}
        )
        return cert_id if r.modified_count > 0 else None

    def download_certificate(self, request_id):
        return self.certificate_request.find_one({"_id": ObjectId(request_id)})

    def get_request_by_id(self, request_id):
        return self.certificate_request.find_one({"_id": ObjectId(request_id)})

    def get_all_requests(self):
        return list(self.certificate_request.find().sort("timestamp", -1))

    def remove_certificate_request(self, req_id):
        try:
            res = self.requests().delete_one({"_id": ObjectId(req_id)})
            return res.deleted_count > 0
        except:
            return False
