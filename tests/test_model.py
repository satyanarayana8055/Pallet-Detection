from config.config import Config
from pathlib import Path


def test_model_path_exists():
    assert Config.MODEL_PATH.exists(), f"Model path does not exist: {Config.MODEL_PATH}"


def test_base_model_exists():
    base_model = Path(Config.MODEL_PATH) / "yolov5m.pt"
    assert base_model.exists(), f"Pretrained model not found: {base_model}"


def test_train_data_yaml_exists():
    assert (
        Config.TRAIN_DATA_PATH.exists()
    ), f"Train data YAML not found: {Config.TRAIN_DATA_PATH}"
