"""helper.py is used reusable codes"""

from pathlib import Path


def ensure_directory(path: str | Path):
    """Create directory if it doesn't exist."""
    try:
        dir_path = Path(path) if not isinstance(path, Path) else path
        print(f"Ensuring directory: {dir_path}")
        if not dir_path.exists():
            print(f"Creating directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Directory already exists: {dir_path}")
    except Exception:
        print(f"Error creating directory {dir_path}")
        raise
