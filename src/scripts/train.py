import os
import mlflow
import pandas as pd
from ultralytics import YOLO

from config.config import Config
from utils.logger import get_logger
from utils.helper import ensure_directory

logger = get_logger("train")


def train_model():
    logger.info("Starting YOLOv8 training...")
    ensure_directory(Config.MODEL_PATH)

    if not Config.MODEL_PATH.exists():
        logger.error(f"Model directory not found: {Config.MODEL_PATH}")
        return

    base_model_path = os.path.join(Config.MODEL_PATH, "yolov5m.pt")
    if not os.path.exists(base_model_path):
        logger.error(f"Pretrained model yolov8s.pt not found at: {base_model_path}")
        return

    model = YOLO(base_model_path)

    # Set or create experiment
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("YOLOv8_Pallet_Detection")

    with mlflow.start_run(run_name="YOLOv8_Pallet_Train"):
        # Log hyperparameters
        mlflow.log_params(
            {
                "epochs": Config.EPOCHS,
                "batch_size": Config.BATCH_SIZE,
                "image_size": Config.IMAGE_SIZE,
                "device": Config.DEVICE,
                "data_yaml": str(Config.TRAIN_DATA_PATH),
                "base_model": base_model_path,
            }
        )

        # Train the model
        results = model.train(
            data=str(Config.TRAIN_DATA_PATH),
            epochs=Config.EPOCHS,
            batch=Config.BATCH_SIZE,
            imgsz=Config.IMAGE_SIZE,
            device=Config.DEVICE,
            name="pallet_model",
        )

        logger.info("Training complete.")

        # Save artifacts
        best_model_path = os.path.join(results.save_dir, "weights", "best.pt")
        last_model_path = os.path.join(results.save_dir, "weights", "last.pt")
        result_plot_path = os.path.join(results.save_dir, "results.png")
        csv_path = os.path.join(results.save_dir, "results.csv")

        mlflow.log_artifacts(results.save_dir, artifact_path="training_artifacts")
        if os.path.exists(best_model_path):
            mlflow.log_artifact(best_model_path, artifact_path="models")
        if os.path.exists(last_model_path):
            mlflow.log_artifact(last_model_path, artifact_path="models")
        if os.path.exists(result_plot_path):
            mlflow.log_artifact(result_plot_path, artifact_path="visuals")

        # Log metrics from results.csv (last epoch)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if not df.empty:
                last_row = df.iloc[-1]
                mlflow.log_metrics(
                    {
                        "precision": float(last_row.get("metrics/precision(B)", 0)),
                        "recall": float(last_row.get("metrics/recall(B)", 0)),
                        "mAP50": float(last_row.get("metrics/mAP50(B)", 0)),
                        "mAP50_95": float(last_row.get("metrics/mAP50-95(B)", 0)),
                    }
                )
                logger.info("Metrics logged to MLflow.")
            else:
                logger.warning("results.csv is empty. No metrics logged.")
        else:
            logger.warning("results.csv not found.")

        logger.info(f"Best model saved at: {best_model_path}")
        logger.info(f"MLflow run ID: {mlflow.active_run().info.run_id}")


if __name__ == "__main__":
    train_model()
