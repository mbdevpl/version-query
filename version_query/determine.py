"""Determine current version of a package."""

import datetime
import inspect
import json
import logging
import pathlib

import git
import packaging
#import packaging.version.Version
#import pkg_resources

from .version import Version

_LOG = logging.getLogger(__name__)

DATETIME_FORMAT = '%Y%m%d.%H%M%S'


def determine_version_from_repo(repo_path: pathlib.Path, search_parent_directories=True) -> tuple:
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    _LOG.debug('found repository in "%s"', repo.working_dir)

    version_tags = {} # type: t.Mapping[str, t.Tuple[int, int, int, int]]
    for tag in repo.tags:
        try:
            version_tags[tag] = Version.parse_str(str(tag))
        except packaging.version.InvalidVersion:
            continue
    _LOG.debug('found version tags: %s', version_tags)
    version_tags = sorted(version_tags, key=lambda _: version_tags[_])
    try:
        latest_version_tag = version_tags[-1]
        latest_version = version_tags[latest_version_tag]
        _LOG.debug(
            'latest version is: %s, sha %s, tuple %s',
            latest_version_tag, latest_version_tag.commit, latest_version)
    except IndexError:
        latest_version_tag = repo.head
        latest_version = (0, 1, 0, 0, None, None)
        _LOG.warning(
            'no version tags in the repository "%s", assuming: %s',
            repo.working_dir, latest_version)
    major, minor, release, patch, suffix, commit_sha = latest_version

    if repo.head.commit != latest_version_tag.commit or repo.is_dirty(untracked_files=True):
        release += 1
        suffix = 'dev'
        patch = 0
        commit_sha = repo.head.commit.hexsha[:8]

        for commit in repo.iter_commits():
            _LOG.debug('iterating over commit %s', commit)
            if commit == latest_version_tag.commit:
                break
            patch += 1

        if repo.is_dirty(untracked_files=True):
            commit_sha += '.dirty.{}'.format(
                datetime.datetime.strftime(datetime.datetime.now(), DATETIME_FORMAT))

    return major, minor, release, suffix, patch, commit_sha


def determine_version_from_manifest(path_prefix: pathlib.Path) -> tuple:

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


def determine_version():
    """Generate version string by querying various available information sources."""

    _LOG.debug('detecting applicable version from commit history')

    frame_info = inspect.getouterframes(inspect.currentframe())[1]
    caller_path = frame_info[1] # frame_info.filename

    here = pathlib.Path(caller_path).absolute().resolve()
    if not here.is_file():
        raise RuntimeError('path "{}" was expected to be a file'.format(here))
    here = here.parent
    if not here.is_dir():
        raise RuntimeError('path "{}" was expected to be a directory'.format(here))
    _LOG.debug('found directory "%s"', here)

    try:
        version_tuple = determine_version_from_repo(here)
    except git.exc.InvalidGitRepositoryError:
        _LOG.debug('no repository found in "%s"', here)
        version_tuple = determine_version_from_manifest(here)

    return version_tuple
