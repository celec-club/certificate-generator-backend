from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from core.config import Config


class TemplateModel:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.template_collection = self.db[Config.TEMPLATE_COLLECTION_NAME]

    def temp_col(self):
        return self.template_collection

    def create_template(self, name: str, image_url: str, uploaded_by=None):
        doc = {
            "name": name,
            "image_url": image_url,
            "uploaded_by": uploaded_by if uploaded_by else None,
            "created_at": datetime.utcnow(),
        }

        result = self.template_collection.insert_one(doc)
        return str(result.inserted_id)

    def get_template_by_id(self, template_id: str):
        return self.temp_col().find_one({"_id": ObjectId(template_id)})

    def get_all_templates(self):
        return list(self.temp_col().find().sort("created_at", -1))

    def remove_template(self, template_id):
        try:
            res = self.temp_col().delete_one({"_id": ObjectId(template_id)})
            return res.deleted_count > 0
        except:
            return False
