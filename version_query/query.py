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
    assert here.is_file(), here
    here = here.parent
    assert here.is_dir(), here
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


def predict_folder(path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    priority_cutoff = 2
    paths = [path] + (list(path.parents)[:priority_cutoff] if search_parent_directories else [])
    for pth in paths:
        try:
            return predict_git_repo(pth, search_parent_directories=False)
        except git.InvalidGitRepositoryError:
            pass
    try:
        return query_package_folder(path, search_parent_directories=False)
    except ValueError:
        pass
    try:
        return predict_git_repo(path, search_parent_directories=search_parent_directories)
    except git.InvalidGitRepositoryError:
        pass
    return query_folder(path, search_parent_directories=search_parent_directories)


def predict_caller(stack_level: int = 1) -> Version:
    """Predict the version of code associated with the caller of this function."""
    here = _caller_folder(stack_level + 1)
    return predict_folder(here, True)


def predict_version_str() -> str:
    return predict_caller(2).to_str()


def main(args=None) -> None:
    """Entry point of the command-line interface."""
    from ._logging import setup_basic_logging
    setup_basic_logging()
    parser = argparse.ArgumentParser(
        prog='version_query',
        description='''Tool for querying current versions of Python packages. Use LOGGING_LEVEL
        environment variable to adjust logging level.''',
        epilog='Copyright 2017-2018 Mateusz Bysiek https://mbdevpl.github.io/ , Apache License 2.0',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    from ._version import VERSION
    parser.version = VERSION
    parser.add_argument('-i', '--increment', action='store_true', help='''output version string for
                        next patch release, i.e. if version is 1.0.3, output 1.0.4''')
    parser.add_argument('-p', '--predict', action='store_true', help='''operate in prediction mode,
                        i.e. assume existence of git repository and infer current version from
                        its tags, history and working tree status''')
    parser.add_argument('path', type=pathlib.Path)
    parser.add_argument('--version', action='version')
    args = parser.parse_args(args)
    if args.predict and args.increment:
        raise ValueError(
            'choose one: either increment current version, or predict upcoming version')
    if args.predict:
        version = predict_folder(args.path)
    else:
        version = query_folder(args.path)
    if args.increment:
        version.increment(VersionComponent.Patch)
    print(version)
