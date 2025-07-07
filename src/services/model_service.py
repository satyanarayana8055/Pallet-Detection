from PIL import ImageDraw, ImageFont
import torch
from ultralytics import YOLO
from config.config import Config
from utils.logger import get_logger
import numpy as np


class ModelService:
    def __init__(self):
        self.logger = get_logger("ModelService")
        self.device = Config.DEVICE if torch.cuda.is_available() else "cpu"
        self.model_path = Config.TRAINED_MODEL_DIR

        self.load_model()

    def load_model(self):
        try:
            self.model = YOLO(self.model_path)
            self.logger.info(f"Model loaded from: {self.model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise

    def detect_pallets(self, image):
        try:
            # Convert PIL image to numpy array for YOLO
            image_np = np.array(image.convert("RGB"))

            # Perform prediction
            results = self.model.predict(
                image_np, device=self.device, conf=0.25, verbose=False
            )[0]

            detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                width = x2 - x1
                height = y2 - y1

                detection = {
                    "bbox": [int(x1), int(y1), int(width), int(height)],
                    "confidence": confidence,
                    "class": self.get_class_name(class_id),
                    "class_id": class_id,
                }
                detections.append(detection)

            self.logger.info(f"Detected {len(detections)} objects")
            return detections

        except Exception as e:
            self.logger.error(f"Prediction error: {e}")
            raise

    def get_class_name(self, class_id):
        class_names = ["wooden_pallet", "plastic_pallet", "euro_pallet", "pallet"]
        return class_names[class_id] if class_id < len(class_names) else "unknown"

    def get_model_info(self):
        return {
            "model_path": self.model_path,
            "device": self.device,
            "model_type": "YOLOv5m",
            "input_size": 640,
            "classes": ["wooden_pallet", "plastic_pallet", "euro_pallet", "pallet"],
            "status": "loaded",
        }

    def draw_detections(self, image, detections):
        result_image = image.copy()
        draw = ImageDraw.Draw(result_image)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        colors = ["#FF6B6B", "#6BCB77", "#4D96FF", "#FFD93D"]

        for i, det in enumerate(detections):
            x, y, w, h = det["bbox"]
            class_name = det["class"]
            confidence = det["confidence"]
            color = colors[i % len(colors)]

            draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
            label = f"{class_name} {confidence:.2f}"
            draw.text((x, y - 10), label, fill="white", font=font)

        return result_image
