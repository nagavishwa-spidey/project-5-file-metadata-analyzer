# Cloud File Metadata Analyzer

> A cloud-ready object inspection microservice extracting file metadata, cryptographic integrity digests, EXIF imagery attributes, and security risk indicators.

---

## 1. Project Overview

The **Cloud File Metadata Analyzer** is an asynchronous file profiling microservice modeled after object ingestion pipelines used in modern cloud storage ecosystems (such as Amazon S3, Google Cloud Storage, and Azure Blob Storage). Built with Python and Flask, it processes arbitrary file streams without saving them to persistent server disks, operating in-memory to preserve serverless and stateless design standards.

The service performs deep metadata discovery: byte counts, human-readable file sizes, MIME type sniffers, MD5 and SHA-256 cryptographic checksums, image resolution, color models, EXIF camera tags, and lexical text metrics. It also embeds a heuristic security analyzer detecting suspicious executables, double extensions, and embedded script injection. An amber-themed web dashboard and REST API endpoints provide immediate visibility for single or batch file uploads.

---

## 2. Problem Statement

Cloud storage buckets store billions of binary objects ingested via user uploads, automated backups, and cross-cloud synchronization. Ingesting untrusted files directly into cloud workflows introduces severe security and operational vulnerabilities: malicious payload uploads (e.g. ransomware or executable scripts disguised as media), corrupt object transfers, and lack of content classification.

Traditional object stores treat incoming files as opaque byte blobs unless explicit metadata extraction pipelines are executed upon ingress. Deploying a dedicated, stateless metadata analyzer microservice enables immediate payload sanitization, deduplication through content-addressable cryptographic hashing, and automated classification before objects reach persistent database layers.

---

## 3. Objectives

- Construct a decoupled Python microservice simulating cloud storage event triggers (e.g., S3 Event Notifications / Google Cloud Storage Triggers).
- Provide memory-efficient chunk-based hashing calculating MD5 and SHA-256 digests.
- Implement specialized sub-analyzers extracting image geometry and EXIF data (Pillow) and text metrics (character, line, word counts, and language heuristics).
- Provide a heuristic threat scanner flagging high-risk executable extensions, double extensions (`.pdf.exe`), and embedded scripts.
- Offer batch file ingestion via multipart HTTP form data allowing multi-file processing in a single API call.
- Provide an amber-themed web user interface with drag-and-drop file ingestion, single-click checksum copying, and JSON report downloads.
- Ensure 100% test pass rates across all analysis services and API endpoints using `pytest`.

---

## 4. Features

- **Object Profile Extraction:**
  - File name, extension, MIME type, raw byte size, and formatted units (B, KB, MB, GB).
  - High-level categorization: `image`, `text`, `document`, `archive`, `video`, `audio`, `other`.
- **Cryptographic Integrity & Content Addressability:**
  - Chunked MD5 and SHA-256 digests matching cloud ETag and hash verification patterns.
  - One-click clipboard copy buttons for checksum verification.
- **Domain-Specific Content Analysis:**
  - **Images:** Dimensions (width $\times$ height), color mode (RGB, RGBA, etc.), format, alpha transparency detection, and EXIF camera parameters.
  - **Text Files:** Line count, word count, character count, auto-detected character encoding (via `chardet`), and language detection heuristics.
- **Heuristic Threat Profiling:**
  - Real-time risk categorization (`SAFE`, `LOW`, `MEDIUM`, `HIGH`).
  - Detection of executable binaries (`.exe`, `.bat`, `.cmd`, `.sh`, `.msi`), double extensions, dangerous MIME types, and inline `<script>` tags.
- **Interactive Multi-File Dashboard:**
  - Drag-and-drop drop zone supporting single and multi-file batch uploads.
  - Real-time card-based visualization of each file's attributes.
  - Full analysis export to a single structured JSON file download.

---

## 5. Cloud Computing Concepts Demonstrated

| Concept | Implementation in this Project |
| :--- | :--- |
| **Object Metadata & ETags** | Calculates cryptographic hashes mimicking S3 ETags used for object verification and deduplication. |
| **Ingress Inspection Pipeline** | Simulates cloud storage bucket triggers (S3 Lambda triggers) that inspect and profile files prior to archiving. |
| **In-Memory Stateless Processing**| Streams and analyzes bytes strictly in RAM buffers; zero disk persistence prevents container state leakage. |
| **Container-Ready Microservice**| Accompanied by standard `Procfile` and 12-factor configuration for rapid deployment on cloud platforms. |
| **Batch Processing Optimization** | Parallel multi-part stream handling enabling batch metadata extraction across distributed assets. |

---

## 6. Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Runtime** | Python | >= 3.9 | Backend programming runtime |
| **Framework** | Flask | ^3.0.0 | Lightweight RESTful web microservice |
| **WSGI Server** | Gunicorn | ^21.2.0 | Production HTTP server |
| **Image Engine** | Pillow | ^10.1.0 | Image metadata and EXIF extraction |
| **Encoding Engine**| Chardet | ^5.2.0 | Byte-level character set detection |
| **CORS Support** | Flask-CORS | ^4.0.0 | Cross-Origin Resource Sharing handling |
| **Frontend** | HTML5 / CSS3 / ES6 | Native | Amber-themed drag-and-drop UI |
| **Testing** | Pytest | ^7.4.3 | Automated unit and integration testing suite |

---

## 7. Architecture & Workflow

```
+--------------------------------------------------------------------------+
|                               Client Layer                               |
|        Web Interface (Drag & Drop)   OR   Cloud S3 Ingress Trigger       |
+------------------------------------+-------------------------------------+
                                     |
                       HTTP POST (Multipart Upload)
                                     v
+--------------------------------------------------------------------------+
|                         Flask Application Router                         |
|                                (app.py)                                  |
+------------------------------------+-------------------------------------+
                                     |
                                     v
                       +-------------+-------------+
                       |   Upload Guards & Bounds  |
                       |   (utils/validators.py)   |
                       +-------------+-------------+
                                     | Valid bytes stream
                                     v
                       +---------------------------+
                       | Metadata Extractor Engine |
                       | (metadata_extractor.py)   |
                       +-------------+-------------+
                                     |
         +---------------------------+---------------------------+
         |                           |                           |
         v                           v                           v
+------------------+       +-------------------+       +-------------------+
|  hash_generator  |       |  image_analyzer   |       |  security_scanner |
| - MD5 / SHA-256  |       | - Pillow / EXIF   |       | - Risk scoring    |
| - Chunked stream |       | - Dims / Alpha    |       | - Script & Ext    |
+------------------+       +-------------------+       +-------------------+
         |                           |                           |
         +---------------------------+---------------------------+
                                     |
                               JSON Payload
                                     v
                           HTTP 200 OK Response
```

---

## 8. Folder Structure

```
project-5-file-metadata-analyzer/
├── .env.example              # Environment variables template
├── .gitignore                # Exclusions for Python caches, venv, and uploads
├── README.md                 # Complete project documentation
├── Procfile                  # Process file for cloud container deployment
├── requirements.txt          # Production and testing Python dependencies
├── config.py                 # Centralized 12-Factor application configuration
├── app.py                    # Flask application endpoints and lifecycle
├── services/
│   ├── __init__.py           # Package marker
│   ├── metadata_extractor.py # Central orchestrator collecting all file metrics
│   ├── hash_generator.py     # Chunked MD5 and SHA-256 generator
│   ├── image_analyzer.py     # Pillow-based image dimension and EXIF parser
│   ├── text_analyzer.py      # Lexical metrics and character encoding detector
│   └── security_scanner.py   # Heuristic threat and script detector
├── utils/
│   ├── __init__.py           # Package marker
│   ├── file_utils.py         # MIME sniffer and extension normalizer
│   └── validators.py         # File bounds and name sanitization
├── templates/
│   └── index.html            # User interface template
├── static/
│   ├── css/
│   │   └── styles.css        # Responsive amber-themed stylesheet
│   └── js/
│       └── app.js            # Drag-and-drop handling, batch logic, JSON export
└── tests/
    ├── __init__.py           # Test package marker
    ├── conftest.py           # Shared fixtures (PNG pixel, text, CSV)
    ├── test_api.py           # Integration tests for Flask endpoints
    ├── test_hash_generator.py# Unit tests for MD5/SHA256 calculations
    ├── test_image_analyzer.py# Unit tests for image dimensions and modes
    ├── test_metadata_extractor.py # Unit tests for comprehensive extraction
    ├── test_security_scanner.py # Unit tests for executable & script detection
    └── test_text_analyzer.py # Unit tests for word and line counts
```

---

## 9. Prerequisites

- **Python:** version `3.9` through `3.12`
- **pip:** Python package manager
- **Git:** version `2.x` or later

---

## 10. Installation & Local Setup

1. **Navigate to the project folder:**
   ```bash
   cd cloud-computing-projects/project-5-file-metadata-analyzer
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize environment settings:**
   ```bash
   cp .env.example .env
   ```

---

## 11. Environment Variable Configuration

| Variable | Description | Default Value | Required |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Runtime mode | `development` | No |
| `FLASK_DEBUG` | Enable debug logs | `1` | No |
| `PORT` | Listening port | `5000` | No |
| `MAX_FILE_SIZE`| Maximum upload byte size | `10485760` (10MB) | No |
| `SECRET_KEY` | Session encryption key | `dev-secret-key` | Production |

---

## 12. How to Run the Application

### Development Server:
```bash
python app.py
```

### Production WSGI Server (Gunicorn):
```bash
gunicorn app:app --bind 0.0.0.0:5000
```
*Expected Output:*
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000 (12345)
[INFO] Using worker: sync
```

Access the web interface at `http://localhost:5000`.

---

## 13. How to Test

Execute the automated test suite with `pytest`:

```bash
pytest -v
```

*Expected Verification Output:*
```
tests/test_api.py::test_index_route PASSED
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_supported_types PASSED
tests/test_api.py::test_api_analyze_single_file PASSED
tests/test_api.py::test_api_hash_endpoint PASSED
tests/test_api.py::test_api_batch_analyze PASSED
tests/test_hash_generator.py::test_hash_md5 PASSED
tests/test_hash_generator.py::test_hash_sha256 PASSED
tests/test_hash_generator.py::test_generate_all_hashes PASSED
tests/test_image_analyzer.py::test_analyze_valid_png PASSED
tests/test_image_analyzer.py::test_analyze_non_image PASSED
tests/test_metadata_extractor.py::test_get_size_human PASSED
tests/test_metadata_extractor.py::test_detect_category PASSED
tests/test_metadata_extractor.py::test_extract_metadata_text PASSED
tests/test_metadata_extractor.py::test_extract_metadata_image PASSED
tests/test_security_scanner.py::test_scan_safe_text_file PASSED
tests/test_security_scanner.py::test_scan_executable_extension PASSED
tests/test_security_scanner.py::test_scan_double_extension PASSED
tests/test_security_scanner.py::test_scan_embedded_script_tag PASSED
tests/test_text_analyzer.py::test_analyze_english_text PASSED
tests/test_text_analyzer.py::test_analyze_empty_file PASSED

======================== 21 passed in 0.52s ========================
```

---

## 14. API Documentation

### 1. Analyze Single File
- **Endpoint:** `POST /api/analyze`
- **Content-Type:** `multipart/form-data`
- **Form Field:** `file` (Binary File Stream)
- **Response (`200 OK`):**
  ```json
  {
    "filename": "cloud_architecture.png",
    "extension": ".png",
    "mime_type": "image/png",
    "size_bytes": 1048576,
    "size_human": "1.00 MB",
    "hashes": {
      "md5": "e99a18c428cb38d5f260853678922e03",
      "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    },
    "category": "image",
    "is_text": false,
    "security": {
      "risk_level": "safe",
      "warnings": [],
      "details": { "has_double_extension": false, "has_executable_extension": false }
    },
    "analysis": {
      "width": 1920,
      "height": 1080,
      "format": "PNG",
      "mode": "RGBA",
      "has_transparency": true
    }
  }
  ```

### 2. Fast Hash Extraction Only
- **Endpoint:** `POST /api/hash`
- **Content-Type:** `multipart/form-data`
- **Response (`200 OK`):**
  ```json
  {
    "filename": "backup.tar.gz",
    "hashes": {
      "md5": "7d793037a0760186574b0282f2f435e7",
      "sha256": "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d"
    }
  }
  ```

### 3. Batch Multi-File Profiling
- **Endpoint:** `POST /api/batch`
- **Content-Type:** `multipart/form-data`
- **Form Field:** `files` (Array of files)
- **Response (`200 OK`):**
  ```json
  {
    "count": 2,
    "results": [
      { "filename": "file1.txt", "category": "text", "size_human": "450 B" },
      { "filename": "file2.jpg", "category": "image", "size_human": "2.40 MB" }
    ]
  }
  ```

---

## 15. Cloud Deployment Instructions

### Deploy to Render (Web Service)
1. Push this repository to GitHub as `cloud-file-metadata-analyzer`.
2. On [Render Dashboard](https://dashboard.render.com), create a new **Web Service**.
3. Select your repository.
4. Specify:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Deploy to generate your public URL.

### Deploy to Railway
1. Create a **New Project** on [Railway.app](https://railway.app).
2. Choose **Deploy from GitHub** and connect `cloud-file-metadata-analyzer`.
3. Railway executes `requirements.txt` and starts the `Procfile` command automatically.

---

## 16. Verified Live Website URL

- **GitHub Repository:** https://github.com/nagavishwa-spidey/project-5-file-metadata-analyzer
- **Live Deployment URL:** _To be updated after cloud provider deployment verification_

---

## 17. Screenshots & Visual Captures

To record application performance:
1. Open the web interface.
2. Drag and drop sample files: an image (PNG/JPG), a text document, and an executable or test file.
3. Observe and document the resulting cards:
   - Image card showing resolution, format, and checksums.
   - Text card showing word/line metrics.
   - Security banner indicating risk assessment.
4. Click **Export All as JSON** to confirm report generation.
5. Save captures in `assets/screenshots/`:
   - `01-dropzone.png`: File drop target with amber branding.
   - `02-metadata-cards.png`: Card grid displaying image dimensions and checksums.
   - `03-security-warning.png`: Card highlighting risk indicator on flagged files.

---

## 18. Limitations & Future Improvements

- **Deep Antivirus Engine:** Uses heuristic file signature checks; integration with ClamAV or VirusTotal API would enable full binary malware analysis.
- **Audio/Video Tag Extraction:** Extend media analysis using `ffmpeg-python` or `mutagen` for bitrates, codecs, and durations.
- **Direct S3 Bucket Scanner:** Add a worker background queue that pulls objects directly from Amazon S3 buckets via EventBridge.

---

## 19. License

This project is open-source software licensed under the **MIT License**.

---

## 20. Author

Developed by **nagavishwa-spidey** for Cloud Computing Engineering.
