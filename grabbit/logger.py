import logging
from copy import copy
from datetime import datetime
import os

from grabbit.grabbit import Grabbit

class GrabbitFormatter(logging.Formatter):
    _red = "\x1b[31m"
    _yellow = "\x1b[33m"
    _green = "\x1b[32m"
    _blue = "\x1b[34m"
    _reset = "\x1b[0m"
    _format = '%(asctime)s [T: %(total)d][F: %(failed)d][A: %(added)d][%(levelname)s]: %(message)s'

    COLORS = {
        logging.DEBUG: _blue,
        logging.INFO: _green,
        logging.WARNING: _yellow,
        logging.ERROR: _red,
        logging.CRITICAL: _red
    }

    _use_color: bool

    def __init__(self, use_color: bool = True):
        super().__init__(self._format)
        self._use_color = use_color

    def format(self, record: logging.LogRecord):
        record_copy = copy(record)
        if self._use_color:
            color = self.COLORS.get(record.levelno)
            record_copy.levelname = f"{color}{record.levelname}{self._reset}"
        return super().format(record_copy)


class GrabbitLogger(logging.Logger):
    geddit: Grabbit

    def __init__(self, level = logging.INFO):
        super().__init__("GrabbitLogger", level)
        self.extra_info = None

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(GrabbitFormatter())
        self.addHandler(console_handler)

        # Ensure the logs directory exists
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File handler
        log_filename = f"{log_dir}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(GrabbitFormatter(use_color=False))
        file_handler.setLevel(logging.DEBUG)
        self.addHandler(file_handler)

    def set_grabbit(self, geddit: Grabbit):
        self.geddit = geddit

    def _get_extra(self):
        return {
            "total": len(self.geddit.downloaded_posts),
            "failed": len(self.geddit.failed_downloads),
            "added": self.geddit.added_count
        }

    def critical(self, msg, *args, **kwargs):
        super().log(logging.CRITICAL, msg, *args, extra=self._get_extra(), **kwargs)

    def error(self, msg, *args, **kwargs):
        super().log(logging.ERROR, msg, *args, extra=self._get_extra(), **kwargs)

    def warning(self, msg, *args, **kwargs):
        super().log(logging.WARN, msg, *args, extra=self._get_extra(), **kwargs)

    def info(self, msg, *args, **kwargs):
        super().log(logging.INFO, msg, *args, extra=self._get_extra(), **kwargs)

    def debug(self, msg, *args, **kwargs):
        super().log(logging.DEBUG, msg, *args, extra=self._get_extra(), **kwargs)
