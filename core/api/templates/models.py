from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from config import Config


class TemplateModel:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.template_collection = self.db[Config.TEMPLATE_COLLECTION_NAME]

    def get_collection(self):
        return self.template_collection

    def create_template(self, name: str, image_url: str, uploaded_by=None):
        doc = {
            "name": name,
            "image_url": image_url,
            "uploaded_by": ObjectId(uploaded_by) if uploaded_by else None,
            "created_at": datetime.utcnow,
        }

        result = self.template_collection.insert_one(doc)
        return str(result.inserted_id)

    def get_template_by_id(self, template_id: str):
        return self.get_collection().find_one({"_id": ObjectId(template_id)})

    def get_certificates(self):
        return list(self.get_collection().find().sort("created_at", -1))

    def remove_certificates(self, template_id):
        try:
            res = self.get_collection().delete_one({"_id": ObjectId(template_id)})
            return res.deleted_count > 0
        except Exception as e:
            print(f"Error deleting template {template_id}: {e}")
            return False
