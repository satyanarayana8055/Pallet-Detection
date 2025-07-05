#!/usr/bin/env python3
"""
Inference script for Pallet Detection.
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
from src.config.config import Config
from src.utils.logger import get_logger

logger = get_logger("inference")

def run_inference():
    """Run inference on images in the input directory."""
    logger.info("Starting inference...")
    
    # Check if model exists
    if not os.path.exists(Config.MODEL_PATH):
        logger.error(f"Model file not found: {Config.MODEL_PATH}")
        return
    
    # Load model
    model = YOLO(Config.MODEL_PATH)
    
    # Check if input directory exists
    if not os.path.exists(Config.INPUT_DIR):
        logger.error(f"Input directory not found: {Config.INPUT_DIR}")
        return
    
    # Ensure output directory exists
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    try:
        # Run inference
        results = model.predict(
            source=Config.INPUT_DIR,
            save=True,
            save_txt=True,
            conf=Config.CONFIDENCE_THRESHOLD,
            device=Config.DEVICE,
            project=Config.OUTPUT_DIR
        )
        
        logger.info(f"Inference completed. Results saved to: {Config.OUTPUT_DIR}")
        
    except Exception as e:
        logger.error(f"Inference failed: {str(e)}")

if __name__ == "__main__":
    run_inference()