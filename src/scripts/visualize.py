#!/usr/bin/env python3
"""
Visualization script for Pallet Detection.
"""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import cv2
import numpy as np
from src.config.config import Config
from src.utils.logger import get_logger

logger = get_logger("visualize")

def visualize_predictions():
    """Visualize predictions on images."""
    logger.info("Starting visualization...")
    
    # Check if output directory exists
    if not os.path.exists(Config.OUTPUT_DIR):
        logger.error(f"Output directory not found: {Config.OUTPUT_DIR}")
        return
    
    # Find prediction images
    pred_images = []
    for root, dirs, files in os.walk(Config.OUTPUT_DIR):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png')):
                pred_images.append(os.path.join(root, file))
    
    if not pred_images:
        logger.warning("No prediction images found in output directory")
        return
    
    logger.info(f"Found {len(pred_images)} prediction images")
    
    # Display first few images
    for i, img_path in enumerate(pred_images[:5]):
        img = cv2.imread(img_path)
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(10, 8))
            plt.imshow(img_rgb)
            plt.title(f"Prediction {i+1}: {os.path.basename(img_path)}")
            plt.axis('off')
            plt.show()
            logger.info(f"Displayed: {img_path}")

def plot_training_metrics():
    """Plot training metrics if available."""
    logger.info("Looking for training metrics...")
    
    # Look for training results in runs directory
    runs_dir = "runs"
    if os.path.exists(runs_dir):
        for root, dirs, files in os.walk(runs_dir):
            for file in files:
                if file.endswith('results.png'):
                    img_path = os.path.join(root, file)
                    logger.info(f"Found training results: {img_path}")
                    img = cv2.imread(img_path)
                    if img is not None:
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        plt.figure(figsize=(12, 8))
                        plt.imshow(img_rgb)
                        plt.title("Training Results")
                        plt.axis('off')
                        plt.show()

if __name__ == "__main__":
    visualize_predictions()
    plot_training_metrics()