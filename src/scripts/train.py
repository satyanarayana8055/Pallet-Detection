import os
import sys
import mlflow
import pandas as pd
from ultralytics import YOLO
from config.config import Config
from utils.logger import get_logger
from utils.helper import ensure_directory

logger = get_logger("train")


def train_model():
    logger.info("Starting training...")
    ensure_directory(Config.MODEL_PATH)

    if not Config.MODEL_PATH.exists():
        logger.error(f"Model file path does not exist: {Config.MODEL_PATH}")
        return

    model_path = os.path.join(Config.MODEL_PATH, 'yolov8s.pt')
    model = YOLO(model_path)

    with mlflow.start_run(run_name="YOLOv8_Pallet_Train"):
        # Log hyperparameters
        mlflow.log_param("epochs", Config.EPOCHS)
        mlflow.log_param("batch_size", Config.BATCH_SIZE)
        mlflow.log_param("image_size", Config.IMAGE_SIZE)
        mlflow.log_param("device", Config.DEVICE)
        mlflow.log_param("model", model_path)
        mlflow.log_param("data", Config.TRAIN_DATA_PATH)

        # Train the model
        results = model.train(
            data=Config.TRAIN_DATA_PATH,
            epochs=Config.EPOCHS,
            batch=Config.BATCH_SIZE,
            imgsz=Config.IMAGE_SIZE,
            device=Config.DEVICE,
            name="pallet_model"
        )

        logger.info("Training completed.")

        # Define weight paths
        best_model_path = os.path.join(results.save_dir, "weights", "best.pt")
        last_model_path = os.path.join(results.save_dir, "weights", "last.pt")

        # Log model artifacts
        mlflow.log_artifact(best_model_path, artifact_path="models")
        mlflow.log_artifact(last_model_path, artifact_path="models")

        # Log results visualization
        result_plot_path = os.path.join(results.save_dir, "results.png")
        if os.path.exists(result_plot_path):
            mlflow.log_artifact(result_plot_path, artifact_path="results")

        # 🛠 FIX: Parse metrics from results.csv (last epoch)
        csv_path = os.path.join(results.save_dir, "results.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if not df.empty:
                last_row = df.iloc[-1]
                mlflow.log_metrics({
                    "metrics/precision": float(last_row.get("metrics/precision(B)", 0)),
                    "metrics/recall": float(last_row.get("metrics/recall(B)", 0)),
                    "metrics/mAP50": float(last_row.get("metrics/mAP50(B)", 0)),
                    "metrics/mAP50-95": float(last_row.get("metrics/mAP50-95(B)", 0)),
                })
                logger.info("Metrics logged to MLflow.")
            else:
                logger.warning("results.csv found but it's empty.")
        else:
            logger.warning("results.csv not found — metrics not logged.")

        logger.info(f"Best model saved at: {best_model_path}")
        logger.info(f"MLflow run logged. Run ID: {mlflow.active_run().info.run_id}")


if __name__ == "__main__":
    train_model()
