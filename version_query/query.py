
import argparse
import pathlib

from .git_query import query_git_repo
from .py_query import query_package_folder


def query(path: pathlib.Path, search_parent_directories: bool = False):
    try:
        return query_git_repo(path, search_parent_directories=search_parent_directories)
    except ValueError:
        pass
    return query_package_folder(path, search_parent_directories=search_parent_directories)


def main(args=None, namespace=None):
    parser = argparse.ArgumentParser(
        prog='version_query',
        description='''Tool for querying current versions of Python packages.''',
        epilog='''Copyright 2017 Mateusz Bysiek https://mbdevpl.github.io/ , Apache License 2.0''')
    parser.add_argument('-i', '--increment', action='store_true')
    parser.add_argument('path')
    args = parser.parse_args(args, namespace)
    version = query(args.path)
    if args.increment:
        version.increment()
    print(version)
