"""Command-line interface of version_query package."""

import argparse
import pathlib

from boilerplates.cli import make_copyright_notice, add_version_option

from ._version import VERSION
from .version import VersionComponent
from .query import query_folder, predict_folder


def main(args=None, namespace=None) -> None:
    """Run the command-line interface.

    Either query or predict version in a given folder according to the arguments.
    """
    parser = argparse.ArgumentParser(
        prog='version_query',
        description='''Tool for querying current versions of Python packages. Use LOGGING_LEVEL
        environment variable to adjust logging level.''',
        epilog=make_copyright_notice(
            2017, 2025, author='the contributors', url='https://github.com/mbdevpl/version-query'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_version_option(parser, VERSION)

    parser.add_argument('-i', '--increment', action='store_true', help='''output version string for
                        next patch release, i.e. if version is 1.0.3, output 1.0.4''')
    parser.add_argument('-p', '--predict', action='store_true', help='''operate in prediction mode,
                        i.e. assume existence of git repository and infer current version from
                        its tags, history and working tree status''')
    parser.add_argument('path', type=pathlib.Path)
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
