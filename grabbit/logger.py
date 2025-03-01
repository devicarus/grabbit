""" This module contains custom logging classes for Grabbit. """

import logging
from copy import copy
from datetime import datetime
import os

from grabbit.grabbit import Grabbit


class GrabbitFormatter(logging.Formatter):
    """ Custom formatter for GrabbitLogger """
    _COLORS = {
        logging.DEBUG: "\x1b[34m",  # Blue
        logging.INFO: "\x1b[32m",  # Green
        logging.WARNING: "\x1b[33m",  # Yellow
        logging.ERROR: "\x1b[31m",  # Red
        logging.CRITICAL: "\x1b[31m"  # Red
    }
    _RESET = "\x1b[0m"
    _FORMAT = '%(asctime)s [T: %(total)d][A: %(added)d][%(levelname)s]: %(message)s'

    _use_color: bool

    def __init__(self, use_color: bool = True):
        super().__init__(self._FORMAT)
        self._use_color = use_color

    def format(self, record: logging.LogRecord):
        record_copy = copy(record)
        if self._use_color:
            color = self._COLORS.get(record.levelno)
            record_copy.levelname = f"{color}{record.levelname}{self._RESET}"
        return super().format(record_copy)


class GrabbitLogger(logging.Logger):
    """ Custom logger for Grabbit """
    _geddit: Grabbit = None

    def __init__(self, level=logging.INFO):
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
        """ Set the Grabbit instance to get extra info from """
        self._geddit = geddit

    def _get_extra(self):
        if self._geddit is None:
            return {
                "total": 0,
                "added": 0
            }

        return {
            "total": self._geddit.total_posts(),
            "added": self._geddit.added_posts()
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
