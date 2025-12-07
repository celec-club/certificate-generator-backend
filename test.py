import os
from pymongo import MongoClient
import cloudinary
from cloudinary.uploader import upload
from dotenv import load_dotenv

load_dotenv()

print("===== Environment Variables =====")
# Check if all expected .env variables exist
required_vars = [
    "MONGO_URI", "DB_NAME", 
    "REQUESTS_COLLECTION", "CERTIFICATES_COLLECTION", "TEMPLATE_COLLECTION",
    "CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"{var} = {value}")
    else:
        print(f"⚠️ {var} is missing!")

print("\n===== MongoDB Test =====")
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME")]
    print("Collections in DB:", db.list_collection_names())
    print("✅ MongoDB connection works")
except Exception as e:
    print("❌ MongoDB connection failed:", e)

print("\n===== Cloudinary Test =====")
try:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
    # Try a dummy upload (use small test image)
    # Make sure you have 'test.png' in the same folder
    result = upload(r"C:\Users\azfat\OneDrive\Documents\GitHub\certificate-generator-backend\drone.jpg", folder="test_folder")
    print("✅ Cloudinary upload works:", result["secure_url"])
except Exception as e:
    print("❌ Cloudinary test failed:", e)

print("\n===== Template POST Simulation =====")
try:
    # Simulate template insertion in MongoDB
    template_collection = db[os.getenv("TEMPLATE_COLLECTION")]
    sample_template = {"name": "Test Template", "file_url": "http://example.com/test.png"}
    inserted = template_collection.insert_one(sample_template)
    print("✅ Inserted template ID:", inserted.inserted_id)
except Exception as e:
    print("❌ Template insertion failed:", e)
