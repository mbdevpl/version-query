"""Tool for querying current versions of Python packages."""

import argparse

from .version import Version
from .determine import determine_version_from_path


def main(args=None, namespace=None):
    parser = argparse.ArgumentParser(
        prog='version_query',
        description='''Tool for querying current versions of Python packages.''',
        epilog='''Copyright 2017 Mateusz Bysiek https://mbdevpl.github.io/ , Apache License 2.0''')
    parser.add_argument('path')
    args = parser.parse_args(args, namespace)
    version = determine_version_from_path(args.path)
    print(Version.generate_str(*version))


if __name__ == '__main__':
    main()
