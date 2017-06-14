"""Tests for parser_wrapper module."""

import contextlib
import io
import logging
import runpy
import sys
import unittest

from version_query.determine import determine_caller_version
from version_query.version import Version

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

    def run_module(self, module, *args, run_name: str = '__main__'):
        sys.argv = [module] + list(args)
        runpy.run_module(module, run_name=run_name)

    def test_not_as_main(self):
        self.run_module('version_query', run_name=None)

    def test_help(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            with self.assertRaises(SystemExit):
                self.run_module('version_query')
        _LOG.info('%s', f.getvalue())

    def test_here(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            self.run_module('version_query', '.')
        self.assertEqual(f.getvalue().rstrip(), Version.generate_str(*determine_caller_version(1)))
