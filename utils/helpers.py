import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

from utils.logger import logger


def file_cleanup():
    """Cleans up club data files, if older than a week"""
    for root, dirs, files in os.walk("../data"):
        for file in files:
            if files == "test":
                continue
            file_path = os.path.join(root, file)
            file_time = datetime.datetime.fromtimestamp(
                os.path.getctime(file_path))  # Convert timestamp to datetime
            if file_time < datetime.datetime.now() - relativedelta(weeks=1):
                logger.info(f"Removing old file: {file_path}")
                os.remove(file_path)

