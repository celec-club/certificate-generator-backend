# models.py

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from core.config import Config


class CertificateRequestModel:
    @classmethod
    def get_collection(cls):
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.DB_NAME]
        return db[Config.COLLECTION_NAME_REQUESTS]

    @classmethod
    def create(cls, user_id, template_id, names):
        doc = {
            "user_id": ObjectId(user_id) if user_id else None,
            "template_id": ObjectId(template_id) if template_id else None,
            "names": names,
            "timestamp": datetime.utcnow(),
            "status": "pending",
            "certificates": [],
        }
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_report_path(cls, request_id, path):
        cls.get_collection().update_one(
            {"_id": ObjectId(request_id)}, {"$set": {"report_path": path}}
        )

    @classmethod
    def update_status(cls, request_id, status):
        cls.get_collection().update_one(
            {"_id": ObjectId(request_id)}, {"$set": {"status": status}}
        )

    @classmethod
    def add_certificate(cls, request_id, certificate_id):
        cls.get_collection().update_one(
            {"_id": ObjectId(request_id)},
            {"$push": {"certificates": ObjectId(certificate_id)}},
        )

    @classmethod
    def remove_requests(cls, request_ids):
        cls.get_collection().delete_many(
            {"_id": {"$in": [ObjectId(rid) for rid in request_ids]}}
        )


class CertificateModel:
    @classmethod
    def get_collection(cls):
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.DB_NAME]
        return db[Config.COLLECTION_NAME_CERTIFICATES]

    @classmethod
    def create(cls, request_id, name, image_url):
        doc = {
            "request_id": ObjectId(request_id),
            "name": name,
            "image_url": image_url,
            "created_at": datetime.utcnow(),
        }
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def get(cls, certificate_id):
        return cls.get_collection().find_one({"_id": ObjectId(certificate_id)})

    @classmethod
    def remove_certificates(cls, cert_ids):
        return cls.get_collection().delete_many(
            {"_id": {"$in": [ObjectId(cid) for cid in cert_ids]}}
        )


class TemplateModel:
    @classmethod
    def get_collection(cls):
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.DB_NAME]
        return db[Config.COLLECTION_NAME_TEMPLATE]

    @classmethod
    def create(cls, name, image_url, uploaded_by=None):
        doc = {
            "name": name,
            "image_url": image_url,
            "uploaded_by": ObjectId(uploaded_by) if uploaded_by else None,
            "created_at": datetime.utcnow(),
        }
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def get(cls, template_id):
        return cls.get_collection().find_one({"_id": ObjectId(template_id)})

    @classmethod
    def get_all(cls):
        return list(cls.get_collection().find().sort("created_at", -1))

    @classmethod
    def remove_templates(cls, template_ids):
        return cls.get_collection().delete_many(
            {"_id": {"_in": [ObjectId(tid) for tid in template_ids]}}
        )
