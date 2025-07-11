""" This module contains custom logging classes for Grabbit. """

import logging
from copy import copy
from datetime import datetime
import os
from logging import StreamHandler
from typing import Protocol, Optional

class GrabbitStatsProvider(Protocol):
    def total_posts(self) -> int: ...
    def added_posts(self) -> int: ...

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
    _FORMAT_STATS = '%(asctime)s [T: %(total)d][A: %(added)d][%(levelname)s]: %(message)s'
    _FORMAT = '%(asctime)s [%(levelname)s]: %(message)s'

    _use_color: bool

    def __init__(self, use_color: bool = True, show_stats: bool = False):
        if show_stats:
            super().__init__(self._FORMAT_STATS)
        else:
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
    _stats_provider: Optional[GrabbitStatsProvider] = None
    _console_handler: StreamHandler

    def __init__(self, level=logging.INFO):
        super().__init__("GrabbitLogger", level)

        # Console handler
        self._console_handler = logging.StreamHandler()
        self._console_handler.setFormatter(GrabbitFormatter())
        self.addHandler(self._console_handler)

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

    def set_stats_provider(self, provider: GrabbitStatsProvider):
        """ Set the Grabbit instance to get extra info from """
        self._stats_provider = provider
        self._console_handler.setFormatter(GrabbitFormatter(show_stats=True))

    def _get_extra(self):
        if self._stats_provider is None:
            return {
                "total": 0,
                "added": 0
            }

        return {
            "total": self._stats_provider.total_posts(),
            "added": self._stats_provider.added_posts()
        }

    def _log(self, level, msg, *args, **kwargs):
        super()._log(level, msg, *args, extra=self._get_extra(), **kwargs)

logger = GrabbitLogger()
