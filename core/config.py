import os
from dotenv import load_dotenv
import cloudinary

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    COLLECTION_NAME_REQUESTS = os.getenv("COLLECTION_NAME_REQUESTS")
    COLLECTION_NAME_CERTIFICATES = os.getenv("COLLECTION_NAME_CERTIFICATES")
    COLLECTION_NAME_TEMPLATE = os.getenv("COLLECTION_NAME_TEMPLATES")


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)
