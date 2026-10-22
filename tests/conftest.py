"""
Shared pytest fixtures for Project 5.
"""

import io
import pytest
from PIL import Image
from app import app


@pytest.fixture
def flask_client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_text_file():
    return b"Hello cloud computing world!\nThis is a second line of text.\n"


@pytest.fixture
def sample_image_file():
    # 2x2 red PNG image
    img = Image.new('RGB', (2, 2), color='red')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


@pytest.fixture
def sample_csv_file():
    return b"id,service,tier\n1,s3,standard\n2,lambda,serverless\n"
