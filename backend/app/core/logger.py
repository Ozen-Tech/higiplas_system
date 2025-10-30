import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)

def setup_logger(name: str, log_file: str, level=logging.INFO):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = RotatingFileHandler(
        os.path.join(logs_dir, log_file),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

stock_automation_logger = setup_logger("stock_automation", "stock_automation.log")
stock_operations_logger = setup_logger("stock_operations", "stock_operations.log")
sales_logger = setup_logger("sales", "sales.log")
