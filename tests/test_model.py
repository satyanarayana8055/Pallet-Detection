import pytest
from services.model_service import ModelService
from PIL import Image
import numpy as np


def test_model_loads():
    model = ModelService()
    assert model.model is not None


def test_model_inference_sample_image():
    model = ModelService()
    dummy_image = Image.fromarray(np.zeros((640, 640, 3), dtype=np.uint8))
    results = model.detect_pallets(dummy_image)
    assert isinstance(results, list)
