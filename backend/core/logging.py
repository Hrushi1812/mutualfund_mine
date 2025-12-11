import logging
import sys
from logging.handlers import RotatingFileHandler
import os

# Create logs directory
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logging():
    """Configures the application logger."""
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 1. Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File Handler (Rotating)
    # 5 MB per file, max 3 backups
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Silence noisy libraries
    logging.getLogger("uvicorn.access").handlers = [] # Let uvicorn handle its own or merge?
    # Usually we want to keep uvicorn logs but maybe redirect them?
    # For now, let's just ensure our app logs are captured.

    logger.info("Logging initialized successfully.")

def get_logger(name: str):
    return logging.getLogger(name)
