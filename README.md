# Celec Certificates Generator - Backend System README

## Main Goal

The **Certificate Generator Backend** is a Flask-based API system designed to automate the creation of personalized certificates. It takes a template image and a list of participant names, generates individual certificates, stores the results, and packages them for download.

---

## System Architecture

**1. Input**

* Template image (stored in **Cloudinary**)
* List of names (TXT / XLS input)

**2. Processing**

* Backend (Flask) fetches template from Cloudinary
* Dynamically writes participant names at a calculated position (centered, size adjusted)
* Saves certificates locally for zipping & reporting

**3. Output**

* ZIP archive containing:

  * All generated certificates (.png)
  * `names.txt` report listing recipients

**4. Storage**

* **Cloudinary**: Stores templates
* Local temp storage: For generated certificates before download

**Diagram:**

<img width="970" height="492" alt="Image" src="https://github.com/user-attachments/assets/8c814a22-fa1a-4256-9f83-a54562424140" />

---

## Implemented Functionalities

* **Template Upload** → Uploads certificate templates to Cloudinary with metadata in MongoDB
* **Certificate Request** → Accepts participant list & template ID
* **Dynamic Certificate Generation** → Handles different template sizes, adjusts font automatically
* **Report Generation** → Creates a TXT file with participant names
* **Download as ZIP** → Bundles certificates and report into a downloadable file
* **API Endpoints**:

  * `POST /api/templates/` – Upload template
  * `POST /api/certificates/generate/<string:request_id>` – Generate certificates
  * `GET /api/certificates/download/<string:request_id>` – Download generated files

---

## Results

* Certificates generated dynamically for **any template dimension**
* Automatic text centering and scaling for consistent layout
* Cloud-based template storage for easier management and scalability
* Simplified bulk download of all generated assets

---

## Installation & Deployment

### **1. Clone Repository**

```bash
git clone https://github.com/celec-club/certificate-generator-backend.git
cd certificate-generator-backend
```

### **2. Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Environment Variables**

Create `.env` file:

```
MONGO_URI="" # MongoDB connection URI
DB_NAME="" # Database name
COLLECTION_NAME_CERTIFICATES="" # Collection name for certificates
COLLECTION_NAME_TEMPLATES="" # Collection name for templates
COLLECTION_NAME_REQUESTS="" # Collection name for requests

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME="" # Cloudinary cloud name
CLOUDINARY_API_KEY="" # Cloudinary API key
CLOUDINARY_API_SECRET="" # Cloudinary API secret
```

Or edit `.env.example` file

### **5. Run the Server**

```bash
flask run
# Or
python main.py
```

---

## Conclusion

This backend enables **automated, scalable, and cloud-integrated certificate generation**. By leveraging **Cloudinary** for template storage and **PIL** for text rendering, the system is flexible enough to handle templates of any size. It is API-driven, making it ready for integration with **React.js, mobile apps, or other client interfaces**.
