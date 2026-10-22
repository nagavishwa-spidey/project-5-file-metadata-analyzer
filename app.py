"""
Flask Web Application for Cloud File Metadata Analyzer.

Exposes RESTful endpoints for file metadata extraction, batch profiling,
cryptographic hashing, and security scanning, plus serves the frontend dashboard.
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from config import Config
from services.metadata_extractor import extract_metadata, detect_category, get_size_human
from services.hash_generator import generate_all_hashes
from utils.validators import validate_upload, validate_filename

sanitize_filename = validate_filename

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)


@app.route('/')
def index():
    """Render the dashboard interface."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Service health probe."""
    return jsonify({
        "status": "healthy",
        "service": "cloud-file-metadata-analyzer",
        "version": "1.0.0"
    }), 200


@app.route('/api/supported-types', methods=['GET'])
def supported_types():
    """Return dictionary of supported categories and file classifications."""
    return jsonify({
        "categories": ["image", "text", "document", "archive", "video", "audio", "other"],
        "max_size_bytes": Config.MAX_FILE_SIZE,
        "max_size_human": get_size_human(Config.MAX_FILE_SIZE)
    }), 200


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze a single uploaded file and return complete metadata."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    is_valid, err = validate_upload(file)
    if not is_valid:
        return jsonify({"error": err}), 400

    filename = sanitize_filename(file.filename)
    file_bytes = file.read()

    if len(file_bytes) > Config.MAX_FILE_SIZE:
        return jsonify({"error": f"File exceeds maximum allowed size of {get_size_human(Config.MAX_FILE_SIZE)}"}), 400

    metadata = extract_metadata(file_bytes, filename)
    return jsonify(metadata), 200


@app.route('/api/hash', methods=['POST'])
def get_hashes():
    """Calculate and return only cryptographic hashes for uploaded file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    is_valid, err = validate_upload(file)
    if not is_valid:
        return jsonify({"error": err}), 400

    filename = sanitize_filename(file.filename)
    file_bytes = file.read()
    hashes = generate_all_hashes(file_bytes)

    return jsonify({
        "filename": filename,
        "hashes": hashes
    }), 200


@app.route('/api/batch', methods=['POST'])
def batch_analyze():
    """Analyze multiple uploaded files simultaneously."""
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        return jsonify({"error": "No files uploaded for batch analysis"}), 400

    results = []
    for file in files:
        if not file or not file.filename:
            continue

        filename = sanitize_filename(file.filename)
        file_bytes = file.read()

        if len(file_bytes) > Config.MAX_FILE_SIZE:
            results.append({
                "filename": filename,
                "error": "File exceeds maximum allowed size"
            })
            continue

        meta = extract_metadata(file_bytes, filename)
        results.append(meta)

    return jsonify({
        "count": len(results),
        "results": results
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
