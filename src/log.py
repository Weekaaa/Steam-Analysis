import sys
from pathlib import Path
import logging



# Boilerplate function to Configure logging
def setup_logging(log_dir):
        # Logger Usage
        # logger = setup_logging()
        # logger.error("This is an error message")
        ## logger.warning("This is a warning")
        # logger.info("This is informational")

    if not log_dir.exists():
        log_dir.mkdir(parents=True)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
    )
    
    # Console (stderr) handler
    console_handler = logging.StreamHandler(sys.stderr)
    # console_handler.setLevel(logging.WARNING)  # We won't need warnings
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler(f"{log_dir}/steam_api.log")
    file_handler.setLevel(logging.DEBUG)  # All levels to file
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
