from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    COLLECTION_NAME_REQUESTS = os.getenv("COLLECTION_NAME_REQUESTS")
    COLLECTION_NAME_CERTIFICATES = os.getenv("COLLECTION_NAME_CERTIFICATES")
    COLLECTION_NAME_TEMPLATE = os.getenv("COLLECTION_NAME_TEMPLATES")