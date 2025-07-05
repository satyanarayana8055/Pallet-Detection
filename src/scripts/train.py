import os
import sys
import mlflow
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

    model_path = os.path.join(Config.MODEL_PATH, 'yolov5s.pt')
    model = YOLO(model_path)

    # Start MLflow tracking
    with mlflow.start_run(run_name="YOLOv5_Pallet_Train"):

        # Log hyperparameters
        mlflow.log_param("epochs", Config.EPOCHS)
        mlflow.log_param("batch_size", Config.BATCH_SIZE)
        mlflow.log_param("image_size", Config.IMAGE_SIZE)
        mlflow.log_param("device", Config.DEVICE)
        mlflow.log_param("model", model_path)
        mlflow.log_param("data", Config.TRAIN_DATA_PATH)

        # Train
        results = model.train(
            data=Config.TRAIN_DATA_PATH,
            epochs=Config.EPOCHS,
            batch=Config.BATCH_SIZE,
            imgsz=Config.IMAGE_SIZE,
            device=Config.DEVICE,
            name="pallet_model"
        )

        logger.info("Training completed.")

        # Log model weights
        best_model_path = os.path.join(results.save_dir, "weights", "best.pt")
        last_model_path = os.path.join(results.save_dir, "weights", "last.pt")
        mlflow.log_artifact(best_model_path, artifact_path="models")
        mlflow.log_artifact(last_model_path, artifact_path="models")

        # Log training visualization
        result_plot_path = os.path.join(results.save_dir, "results.png")
        if os.path.exists(result_plot_path):
            mlflow.log_artifact(result_plot_path, artifact_path="results")

        # Log metrics from YOLO results object
        # NOTE: YOLO returns metrics in `results.metrics` after `.train()` (in v8+)
        if hasattr(results, "metrics"):
            metrics = results.metrics
            mlflow.log_metrics({
                "metrics/precision": metrics.get("precision", 0),
                "metrics/recall": metrics.get("recall", 0),
                "metrics/mAP50": metrics.get("mAP50", 0),
                "metrics/mAP50-95": metrics.get("mAP50-95", 0)
            })

        logger.info(f"Best model saved at: {best_model_path}")
        logger.info(f"MLflow run logged. Run ID: {mlflow.active_run().info.run_id}")

if __name__ == "__main__":
    train_model()
