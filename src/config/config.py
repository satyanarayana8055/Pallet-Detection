"""This script is used to project clean and modular"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load variables from .env file
# It is the base folder to get access from outside the src folder
BASE_DIR = Path(__file__).resolve().parents[2]

# Load variables from .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Config:
    # Model
    MODEL_PATH = BASE_DIR / "data" / "models"
    IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", 640))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.4))
    DEVICE = os.getenv("DEVICE", "cpu")

    # Inference
    INPUT_DIR = BASE_DIR / "data" / "input"
    OUTPUT_DIR = BASE_DIR / "data" / "output"
    UPLOAD_DIR = BASE_DIR / "data" / "upload"

    # Training (if applicable)
    TRAIN_DATA_PATH = BASE_DIR / "data" / "labels" / "data.yaml"
    EPOCHS = int(os.getenv("EPOCHS", 50))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 16))

    # API
    CONTENT_LEN = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
    TRAINED_MODEL_DIR = (
        BASE_DIR / "runs" / "detect" / "pallet_model2" / "weights" / "best.pt"
    )
