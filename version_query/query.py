"""High-level utility functions for querying, manipulating and generating version information."""

import argparse
import inspect
import logging
import pathlib

import git

from .version import VersionComponent, Version
from .git_query import query_git_repo, predict_git_repo
from .py_query import query_package_folder

_LOG = logging.getLogger(__name__)


def _caller_folder(stack_level: int = 1) -> pathlib.Path:
    """Determine folder in which the caller module of a function is located."""
    frame_info = inspect.getouterframes(inspect.currentframe())[stack_level]
    caller_path = frame_info[1]  # frame_info.filename

    here = pathlib.Path(caller_path).absolute().resolve()
    if not here.is_file():
        raise RuntimeError('path "{}" was expected to be a file'.format(here))
    here = here.parent
    if not here.is_dir():
        raise RuntimeError('path "{}" was expected to be a directory'.format(here))
    _LOG.debug('found directory "%s"', here)

    return here


def query_folder(path: pathlib.Path, search_parent_directories: bool = False) -> Version:
    """Determine version of code in a given folder."""
    try:
        return query_git_repo(path, search_parent_directories=search_parent_directories)
    except git.InvalidGitRepositoryError:
        pass
    return query_package_folder(path, search_parent_directories=search_parent_directories)


def query_caller(stack_level: int = 1) -> Version:
    here = _caller_folder(stack_level + 1)
    return query_folder(here, True)


def query_version_str() -> str:
    return query_caller(2).to_str()


def predict_caller(stack_level: int = 1) -> Version:
    """Predict the version of code associated with the caller of this function."""
    here = _caller_folder(stack_level + 1)
    try:
        return predict_git_repo(here, True)
    except git.InvalidGitRepositoryError:
        pass
    return query_folder(here, True)


def predict_version_str() -> str:
    return predict_caller(2).to_str()


def main(args=None, namespace=None) -> None:
    """Entry point of the command-line interface."""
    parser = argparse.ArgumentParser(
        prog='version_query',
        description='Tool for querying current versions of Python packages.',
        epilog='Copyright 2017 Mateusz Bysiek https://mbdevpl.github.io/ , Apache License 2.0')
    parser.add_argument('-i', '--increment', action='store_true')
    parser.add_argument('-p', '--predict', action='store_true')
    parser.add_argument('path')
    args = parser.parse_args(args, namespace)
    version = query_folder(args.path)
    if args.predict and args.increment:
        raise ValueError()
    if args.predict:
        version = predict_git_repo(args.path)
    if args.increment:
        version.increment(VersionComponent.Patch)
    print(version)
