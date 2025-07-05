"""Centralized logging with rotation for PalletDetector"""

import logging
import os
from logging.handlers import RotatingFileHandler
from utils.helper import ensure_directory  


def get_logger(name: str) -> logging.Logger:
    """
    Create a logger with rotation.
    Args:
        name (str): Logger name, used as log file name too.
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)  
        
        log_dir = "logs"
        ensure_directory(log_dir)

        log_file = os.path.join(log_dir, f"{name}.log")

        handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,            # Keep last 3 logs
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
