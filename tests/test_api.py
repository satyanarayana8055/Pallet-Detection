import io
import pytest
from PIL import Image
from api.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_index_route(client):
    """Check if index.html loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE html" in response.data or b"<html" in response.data


def test_health_route(client):
    """Check if the health route works."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_detect_route_valid_image(client):
    """Test /detect with a dummy image."""
    img = Image.new("RGB", (640, 640), (255, 255, 255))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    data = {
        "file": (img_bytes, "test.png"),
    }

    response = client.post("/detect", content_type="multipart/form-data", data=data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "detections" in data
    assert "original_image" in data
    assert "processed_image" in data


def test_detect_route_no_file(client):
    """Test /detect with no file sent."""
    response = client.post("/detect", content_type="multipart/form-data", data={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_detect_route_invalid_file(client):
    """Test /detect with invalid file format."""
    fake_txt = io.BytesIO(b"This is not an image")
    data = {
        "file": (fake_txt, "not_image.txt"),
    }
    response = client.post("/detect", content_type="multipart/form-data", data=data)
    assert response.status_code == 400
    assert "error" in response.get_json()
