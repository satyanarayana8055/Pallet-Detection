import os
from pathlib import Path

yolo_structure = {
    "src/app": [
        "app.py",
        "routes.py",
        "templates/index.html",
        "static/css/style.css",
        "static/js/script.js",
    ],
    "src/services": [
        "__init__.py",
        "model_service.py",
        "image_service.py",
        "video_service.py",
    ],
    "src/config": ["__init__.py", "config.py"],
    "data": ["input/.gitkeep", "output/.gitkeep", "labels/.gitkeep", "models/.gitkeep"],
    "docker": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
    "src/scripts": [
        "__init__.py",
        "train.py",
        "inference.py",
        "visualize.py",
    ],
    "src/utils": ["__init__.py", "logger.py", "helper.py"],
    "testing": ["test_model.py", "test_inference.py"],
    ".github": ["workflows/ci-cd.yml"],
    ".": [
        ".env",
        "Makefile",
        "main.py",
        "requirements.txt",
        "README.md",
    ],
}


def create_folders(base_path, structure):
    print("Creating folders...")
    for folder in structure:
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Folder created: {folder_path}")


def create_files(base_path, structure):
    for folder, files in structure.items():
        for file in files:
            file_path = os.path.join(base_path, folder, file)
            file_dir = os.path.dirname(file_path)
            os.makedirs(file_dir, exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    if not file.endswith(".gitkeep"):
                        f.write(f"# {file}")


def create_project_structure():
    base_path = Path(__file__).resolve().parent
    create_folders(base_path, yolo_structure)
    create_files(base_path, yolo_structure)
    print(f"YOLO-AI Project structure created at: '{base_path}'")


if __name__ == "__main__":
    create_project_structure()
