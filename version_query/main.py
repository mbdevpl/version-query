"""Command-line interface of version_query package."""

import argparse
import logging
import os
import pathlib
import sys

from ._version import VERSION
from .version import VersionComponent
from .query import query_folder, predict_folder


def main(args=None, namespace=None) -> None:
    """Run the command-line interface.

    Either query or predict version in a given folder according to the arguments.
    """
    logging_level = getattr(logging, os.environ.get('LOGGING_LEVEL', 'warning').upper())
    logging.basicConfig(level=min(logging_level, logging.WARNING))
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger('version_query').setLevel(logging_level)
    parser = argparse.ArgumentParser(
        prog='version_query',
        description='''Tool for querying current versions of Python packages. Use LOGGING_LEVEL
        environment variable to adjust logging level.''',
        epilog='''Copyright 2017-2023 by the contributors, Apache License 2.0,
        https://github.com/mbdevpl/version-query''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--increment', action='store_true', help='''output version string for
                        next patch release, i.e. if version is 1.0.3, output 1.0.4''')
    parser.add_argument('-p', '--predict', action='store_true', help='''operate in prediction mode,
                        i.e. assume existence of git repository and infer current version from
                        its tags, history and working tree status''')
    parser.add_argument('path', type=pathlib.Path)
    parser.add_argument('--version', action='version',
                        version=f'{parser.prog} {VERSION},\nPython {sys.version}')
    parsed_args = parser.parse_args(args=args, namespace=namespace)
    if parsed_args.predict and parsed_args.increment:
        raise ValueError(
            'choose one: either increment current version, or predict upcoming version')
    if parsed_args.predict:
        version = predict_folder(parsed_args.path)
    else:
        version = query_folder(parsed_args.path)
    if parsed_args.increment:
        version.increment(VersionComponent.Patch)
    print(version)
