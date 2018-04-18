"""Basic logging setup."""

import logging
import os


def setup_basic_logging():
    if 'LOGGING_LEVEL' in os.environ:
        logging.basicConfig(level=getattr(logging, os.environ['LOGGING_LEVEL'].upper()))
