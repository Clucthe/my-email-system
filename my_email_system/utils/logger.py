import logging
import os
from logging.handlers import RotatingFileHandler
from my_email_system import config

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(config.LOG_LEVEL)

        fh = RotatingFileHandler(
            'app.log',
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=2
        )
        fh.setLevel(config.LOG_LEVEL)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger
