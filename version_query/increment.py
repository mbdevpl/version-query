"""Increment the version number."""

import datetime
import logging
import pathlib
import sys
import typing as t

import git

from .config import DATETIME_FORMAT
from .caller import get_caller_folder, get_caller_module_name
from .version import VersionComponent
from .determine import get_latest_version_data

_LOG = logging.getLogger(__name__)


def increment_nonlocal_version_component(
        version_tuple: tuple, incremented_component: VersionComponent) -> tuple:
    assert isinstance(version_tuple, tuple)
    assert len(version_tuple) == 6
    assert isinstance(incremented_component, VersionComponent)
    assert incremented_component <= VersionComponent.Patch

    major, minor, release, suffix, patch, commit_sha = version_tuple

    if incremented_component <= VersionComponent.Release:

        if incremented_component <= VersionComponent.Minor:

            if incremented_component is VersionComponent.Major:
                assert major is not None
                major += 1
                if minor is not None:
                    minor = 0
            elif incremented_component is VersionComponent.Minor:
                assert minor is not None
                minor += 1

            if release is not None:
                release = 0

        elif incremented_component is VersionComponent.Release:
            assert release is not None
            release += 1

        suffix = None
        patch = None
        commit_sha = None

    if incremented_component is VersionComponent.Patch:
        if suffix is None:
            suffix = 'dev'
        if patch is None:
            patch = 1
        else:
            patch += 1

    return major, minor, release, suffix, patch, commit_sha


def increment_local_version_component(
        version_tuple: tuple, repo: git.Repo, latest_version_commit: git.Commit) -> tuple:
    assert isinstance(version_tuple, tuple)
    assert len(version_tuple) == 6

    major, minor, release, suffix, patch, commit_sha = version_tuple
    repo_is_dirty = repo.is_dirty(untracked_files=True)

    if repo.head.commit == latest_version_commit and not repo_is_dirty:
        return major, minor, release, suffix, patch, commit_sha

    commit_sha = repo.head.commit.hexsha[:8]

    patch_increment = 0
    for commit in repo.iter_commits():
        _LOG.log(logging.NOTSET, 'iterating over commit %s', commit)
        if commit == latest_version_commit:
            break
        patch_increment += 1
    if patch_increment > 0:
        if suffix == 'dev':
            if patch is None:
                release = (0 if release is None else release) + 1
                patch = patch_increment
            else:
                patch += patch_increment
        else:
            release = (0 if release is None else release) + 1
            suffix = 'dev'
            patch = patch_increment

    if repo_is_dirty:
        commit_sha += '.dirty{}'.format(
            datetime.datetime.strftime(datetime.datetime.now(), DATETIME_FORMAT))

    if not repo_is_dirty and get_caller_module_name(-1) == 'setup' \
            and any(_ in sys.argv for _ in ('bdist', 'bdist_wheel', 'sdist')):
        commit_sha = None

    return major, minor, release, suffix, patch, commit_sha


def increment_version_of_git_repo(
        repo_path: pathlib.Path, search_parent_directories: bool = True,
        incremented_component: t.Optional[VersionComponent] = None,
        only_if_changed: bool = True) -> tuple:
    _LOG.debug('looking for git repository in "%s"', repo_path)
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    _LOG.debug('found git repository in "%s"', repo.working_dir)

    latest_version_commit, latest_version = get_latest_version_data(repo)

    if incremented_component is None:
        #latest_version = increment_nonlocal_version_component(latest_version, incremented_component) 
        incremented_component = VersionComponent.Local

    if incremented_component is VersionComponent.Local:
        return increment_local_version_component(latest_version, repo, latest_version_commit)

    return increment_nonlocal_version_component(latest_version, incremented_component)


def increment_version_of_path(path: str):
    """Generate version tuple by querying information sources in the filesystem."""
    try:
        version_tuple = increment_version_of_git_repo(path)
    except git.exc.InvalidGitRepositoryError as err:
        _LOG.debug('no repository found in "%s"', path)
        raise ValueError('no repository found in "{}"'.format(path)) from err

    return version_tuple


def increment_caller_version(inspect_level: int = 1):
    """Generate version string by querying all available information sources."""
    here = get_caller_folder(inspect_level + 1)

    return increment_version_of_path(here)
