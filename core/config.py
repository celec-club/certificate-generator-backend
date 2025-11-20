import os
from dotenv import load_dotenv
import cloudinary

load_dotenv()


class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    REQUESTS_COLLECTION_NAME = os.getenv("REQUESTS_COLLECTION")
    CERTIFICATES_COLLECTION_NAME = os.getenv("CERTIFICATES_COLLECTION")
    TEMPLATE_COLLECTION_NAME = os.getenv("TEMPLATE_COLLECTION")


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)
