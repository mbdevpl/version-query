"""Git repository version query tools."""

import logging
import pathlib
import typing as t

import git
#import packaging

from .version import Version

_LOG = logging.getLogger(__name__)


def _all_git_tag_versions(repo: git.Repo) -> t.Mapping[git.Tag, Version]:
    versions = {}
    for tag in repo.tags:
        tag_str = str(tag)
        if tag_str.startswith('v'):
            tag_str = tag_str[1:]
        else:
            continue
        try:
            versions[tag] = Version.from_str(tag_str)
        except ValueError:
        #except packaging.version.InvalidVersion:
            _LOG.warning('failed to convert %s to version', tag_str)
            continue
    return versions


def _latest_git_tag_version(repo: git.Repo) -> t.Tuple[git.Tag, Version]:
    versions = sorted(_all_git_tag_versions(repo).items(), key=lambda _: _[1])
    if not versions:
        raise ValueError('no versions in this repository')
    return versions[-1]


'''
def get_latest_version_data(repo: git.Repo) -> t.Tuple[git.Commit, tuple]:
    """Retrieve the commit and version tuple for the latest tagged version in a git repository."""
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

    return latest_version_commit, latest_version
'''


def query_git_repo(
        repo_path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    """Determine version from tags of a git repository."""
    _LOG.debug('looking for git repository in "%s"', repo_path)
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    _LOG.debug('found git repository in "%s"', repo.working_dir)
    return _latest_git_tag_version(repo)
