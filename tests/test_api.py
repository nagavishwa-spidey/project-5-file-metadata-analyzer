"""
Integration tests for Flask File Metadata Analyzer API.
"""

import io


def test_index_route(flask_client):
    res = flask_client.get('/')
    assert res.status_code == 200
    assert b"File Metadata Analyzer" in res.data


def test_health_check(flask_client):
    res = flask_client.get('/api/health')
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"


def test_supported_types(flask_client):
    res = flask_client.get('/api/supported-types')
    assert res.status_code == 200
    assert "image" in res.get_json()["categories"]


def test_api_analyze_single_file(flask_client, sample_text_file):
    data = {
        'file': (io.BytesIO(sample_text_file), 'test_sample.txt')
    }
    res = flask_client.post('/api/analyze', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["filename"] == "test_sample.txt"
    assert json_data["category"] == "text"
    assert "md5" in json_data["hashes"]


def test_api_hash_endpoint(flask_client, sample_text_file):
    data = {
        'file': (io.BytesIO(sample_text_file), 'checksum.txt')
    }
    res = flask_client.post('/api/hash', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    json_data = res.get_json()
    assert "hashes" in json_data
    assert "sha256" in json_data["hashes"]


def test_api_batch_analyze(flask_client, sample_text_file, sample_csv_file):
    data = {
        'files': [
            (io.BytesIO(sample_text_file), 'doc1.txt'),
            (io.BytesIO(sample_csv_file), 'data.csv')
        ]
    }
    res = flask_client.post('/api/batch', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["count"] == 2
