"""This script is used to project clean and modular"""

import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    # Model
    MODEL_PATH = os.getenv("MODEL_PATH", "data/models/best.pt")
    IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", 640))  # Default for YOLO
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.4))
    DEVICE = os.getenv("DEVICE", "cpu")  # Use "cuda" if GPU is available

    # Inference
    INPUT_DIR = os.getenv("INPUT_DIR", "data/input")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "data/output")

    # Training (if applicable)
    TRAIN_DATA_PATH = os.getenv("TRAIN_DATA_PATH", "data/labels")
    EPOCHS = int(os.getenv("EPOCHS", 50))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 16))
