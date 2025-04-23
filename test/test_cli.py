"""Tests of the CLI."""

import contextlib
import io
import logging
import runpy
import sys
import unittest

from version_query.version import VersionComponent
from version_query.query import \
    query_caller, query_version_str, predict_caller, predict_version_str

_LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def temporarily_set_logger_level(logger_name: str, level: int):
    """Change logger level on enter and restore on exit of this context."""
    logger = logging.getLogger(logger_name)
    level_ = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(level_)


def preserve_logger_level(logger_name: str):
    return temporarily_set_logger_level(logger_name, logging.getLogger(logger_name).level)


def run_module(name: str, *args, run_name: str = '__main__') -> None:
    backup_sys_argv = sys.argv
    sys.argv = [name + '.py'] + list(args)
    runpy.run_module(name, run_name=run_name, alter_sys=True)
    sys.argv = backup_sys_argv


class Tests(unittest.TestCase):

    def test_not_as_main(self):  # pylint: disable = no-self-use
        run_module('version_query', run_name='__not_main__')

    def test_help(self):
        sio = io.StringIO()
        with contextlib.redirect_stderr(sio), preserve_logger_level('version_query'), \
                self.assertRaises(SystemExit):
            run_module('version_query')
        _LOG.info('%s', sio.getvalue())

    def test_bad_usage(self):
        sio = io.StringIO()
        with contextlib.redirect_stderr(sio), preserve_logger_level('version_query'), \
                self.assertRaises(ValueError):
            run_module('version_query', '-p', '-i', '.')
        _LOG.info('%s', sio.getvalue())

    def test_here(self):
        sio = io.StringIO()
        with temporarily_set_logger_level('version_query', logging.ERROR), \
                contextlib.redirect_stdout(sio):
            run_module('version_query', '.')
        self.assertEqual(sio.getvalue().rstrip(), query_caller().to_str())
        self.assertEqual(sio.getvalue().rstrip(), query_version_str())

    def test_increment_here(self):
        sio = io.StringIO()
        with temporarily_set_logger_level('version_query', logging.ERROR), \
                contextlib.redirect_stdout(sio):
            run_module('version_query', '-i', '.')
        self.assertEqual(sio.getvalue().rstrip(),
                         query_caller().increment(VersionComponent.Patch).to_str())

    def test_predict_here(self):
        sio = io.StringIO()
        with temporarily_set_logger_level('version_query', logging.ERROR), \
                contextlib.redirect_stdout(sio):
            run_module('version_query', '-p', '.')
        self.assertEqual(sio.getvalue().rstrip(), predict_caller().to_str())
        self.assertEqual(sio.getvalue().rstrip(), predict_version_str())
