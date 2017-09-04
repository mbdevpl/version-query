"""Tests for parser_wrapper module."""

import contextlib
import io
import logging
import sys
import unittest

from version_query.determine import determine_caller_version
from version_query.version import Version
from .test_setup import run_module

_LOG = logging.getLogger(__name__)


if sys.version_info < (3, 5):

    class _RedirectStream:

        _stream = None

        def __init__(self, new_target):
            self._new_target = new_target
            self._old_targets = []

        def __enter__(self):
            self._old_targets.append(getattr(sys, self._stream))
            setattr(sys, self._stream, self._new_target)
            return self._new_target

        def __exit__(self, exctype, excinst, exctb):
            setattr(sys, self._stream, self._old_targets.pop())

    if sys.version_info < (3, 4):

        class _redirect_stdout(_RedirectStream):

            _stream = "stdout"

        contextlib.redirect_stdout = _redirect_stdout

    class _redirect_stderr(_RedirectStream):

        _stream = "stderr"

    contextlib.redirect_stderr = _redirect_stderr


class Tests(unittest.TestCase):

    def test_not_as_main(self):
        run_module('version_query', run_name=None)

    def test_help(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            with self.assertRaises(SystemExit):
                run_module('version_query')
        _LOG.info('%s', f.getvalue())

    def test_here(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            run_module('version_query', '.')
        self.assertEqual(f.getvalue().rstrip(), Version.generate_str(*determine_caller_version(1)))
