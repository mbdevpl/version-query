"""Determine current version of a package."""

import datetime
import inspect
import json
import logging
import pathlib
import typing as t

import git
import packaging
#import packaging.version.Version
#import pkg_resources

from .version import Version

_LOG = logging.getLogger(__name__)

DATETIME_FORMAT = '%Y%m%d%H%M%S'


def determine_version_from_git_repo(
        repo_path: pathlib.Path, search_parent_directories=True) -> tuple:
    """Determine package version from tags and index status of a git repository."""
    _LOG.debug('looking for git repository in "%s"', repo_path)
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    _LOG.debug('found git repository in "%s"', repo.working_dir)

    version_tags = {} # type: t.Mapping[str, t.Tuple[int, int, int, int]]
    for tag in repo.tags:
        try:
            version_tags[tag] = Version.parse_str(str(tag))
        except packaging.version.InvalidVersion:
            continue
    if version_tags:
        _LOG.debug('found version tags: %s', version_tags)
        version_tags = sorted(version_tags.items(), key=lambda _: version_tags[_[0]])
        latest_version_tag, latest_version = version_tags[-1]
        latest_version_commit = latest_version_tag.commit
        _LOG.debug(
            'latest version is: %s, sha %s, tuple %s',
            latest_version_tag, latest_version_commit, latest_version)
    else:
        for commit in repo.iter_commits(reverse=True):
            latest_version_commit = commit
            break
        latest_version = (0, 0, 0, None, None, None)
        _LOG.debug(
            'no version tags in the repository "%s", assuming: %s',
            repo.working_dir, latest_version)
    major, minor, release, suffix, patch, commit_sha = latest_version

    if repo.head.commit != latest_version_commit or repo.is_dirty(untracked_files=True):
        if minor is None:
            minor = 0
        if release is None:
            release = 0
        release += 1
        suffix = 'dev'
        patch = 0
        commit_sha = repo.head.commit.hexsha[:8]

        for commit in repo.iter_commits():
            _LOG.log(logging.NOTSET, 'iterating over commit %s', commit)
            if commit == latest_version_commit:
                break
            patch += 1

        if repo.is_dirty(untracked_files=True):
            commit_sha += '.dirty{}'.format(
                datetime.datetime.strftime(datetime.datetime.now(), DATETIME_FORMAT))

    return major, minor, release, suffix, patch, commit_sha


def determine_version_from_manifest(path_prefix: pathlib.Path) -> tuple:
    """Determine version from found PKG-INFO file."""
    _LOG.debug('looking for manifest in %s', path_prefix)
    version_tuple = None, None, None, None, None, None
    version = None
    for path in path_prefix.parent.glob(path_prefix.name + '*'):
        if path.suffix == '.dist-info':
            _LOG.debug('found distribution info directory %s', path)
            metadata_path = path.joinpath('metadata.json')
            with open(metadata_path, 'r') as metadata_file:
                metadata = json.load(metadata_file)
            version = metadata['version']
            _LOG.debug('version in metadata is: "%s"', version)
            break
        if path.suffix == '.egg-info':
            _LOG.debug('found egg info directory %s', path)
            pkginfo_path = path.joinpath('PKG-INFO')
            with open(pkginfo_path, 'r') as pkginfo_file:
                for line in pkginfo_file:
                    if line.startswith('Version:'):
                        version = line.replace('Version:', '').strip()
                        break
            _LOG.debug('version in metadata is: "%s"', version)
            break
    if version is None:
        return version_tuple

    return Version.parse_str(version)


def determine_version_from_path(path: str):
    """Generate version tuple by querying information sources in the filesystem."""
    try:
        version_tuple = determine_version_from_git_repo(path)
    except git.exc.InvalidGitRepositoryError:
        _LOG.debug('no repository found in "%s"', path)
        version_tuple = determine_version_from_manifest(path)

    return version_tuple


def determine_caller_version(inspect_level: int):
    """Generate version string by querying all available information sources."""
    frame_info = inspect.getouterframes(inspect.currentframe())[inspect_level]
    caller_path = frame_info[1] # frame_info.filename

    here = pathlib.Path(caller_path).absolute().resolve()
    if not here.is_file():
        raise RuntimeError('path "{}" was expected to be a file'.format(here))
    here = here.parent
    if not here.is_dir():
        raise RuntimeError('path "{}" was expected to be a directory'.format(here))
    _LOG.debug('found directory "%s"', here)

    return determine_version_from_path(here)


def determine_version() -> tuple:
    return determine_caller_version(1)
