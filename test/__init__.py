"""Initialization of tests of version_query package."""

import logging
import os

import colorlog

_HANDLER = logging.StreamHandler()
_HANDLER.setFormatter(colorlog.ColoredFormatter(
    '{name} [{log_color}{levelname}{reset}] {message}', style='{'))

logging.basicConfig(level=logging.DEBUG, handlers=[_HANDLER])
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger('version_query').setLevel(
    getattr(logging, os.environ.get('LOGGING_LEVEL', 'debug').upper()))
logging.getLogger('test').setLevel(logging.DEBUG)

if 'EXAMPLE_PROJECTS_PATH' not in os.environ:
    os.environ['EXAMPLE_PROJECTS_PATH'] = '..'
