import io
from PIL import Image
import numpy as np
from src.api.app import app

def test_detect_endpoint():
    # Generate a dummy black image (640x640)
    dummy_image = Image.fromarray(np.zeros((640, 640, 3), dtype=np.uint8))
    buffer = io.BytesIO()
    dummy_image.save(buffer, format="JPEG")
    buffer.seek(0)

    client = app.test_client()
    response = client.post(
        "/detect",
        content_type='multipart/form-data',
        data={
            'file': (buffer, 'dummy.jpg')
        }
    )

    assert response.status_code == 200
    json_data = response.get_json()

    assert 'success' in json_data and json_data['success'] is True
    assert 'detections' in json_data
    assert 'original_image' in json_data
    assert 'processed_image' in json_data
    assert 'total_pallets' in json_data
