"""High-level utility functions for querying, manipulating and generating version information."""

import inspect
import logging
import pathlib

import git

from .version import Version
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
    """Determine the version of code associated with the caller of this function."""
    here = _caller_folder(stack_level + 1)
    return query_folder(here, True)


def query_version_str() -> str:
    """Determine the version of code that calls this function and get it as string.

    You can use this utility function like this:

    '''
    from version_query import query_version_str

    VERSION = query_version_str()
    '''
    """
    return query_caller(2).to_str()


def predict_folder(path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    """Predict version of code residing in a given folder."""
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
    """Predict version of the code that calls this function and get it as string.

    You can use this utility function like this:

    '''
    from version_query import predict_version_str

    VERSION = predict_version_str()
    '''
    """
    return predict_caller(2).to_str()
