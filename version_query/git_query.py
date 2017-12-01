"""Git repository version query tools."""

import datetime
import logging
import pathlib
import typing as t

import git

from .version import Version

_LOG = logging.getLogger(__name__)


def _all_git_tag_versions(repo: git.Repo) -> t.Mapping[git.Tag, Version]:
    versions = {}
    for tag in repo.tags:
        tag_str = str(tag)
        if tag_str.startswith('ver'):
            tag_str = tag_str[3:]
        elif tag_str.startswith('v'):
            tag_str = tag_str[1:]
        else:
            continue
        try:
            versions[tag] = Version.from_str(tag_str)
        except ValueError:
            # except packaging.version.InvalidVersion:
            _LOG.warning('failed to convert %s to version', tag_str)
            continue
    return versions


def _latest_git_tag_version(repo: git.Repo) -> t.Tuple[git.Tag, Version]:
    versions = sorted(_all_git_tag_versions(repo).items(), key=lambda _: _[1])
    if not versions:
        raise ValueError('the given repo {} has no version tags'.format(repo))
    return versions[-1]


def _upcoming_git_tag_version(repo: git.Repo, ignore_untracked_files: bool = True) -> Version:
    try:
        tag, version = _latest_git_tag_version(repo)
        tag_commit = tag.commit
    except ValueError:
        version = Version.from_str('0.1.0.dev0')
        tag_commit = next(repo.iter_commits(reverse=True))

    repo_is_dirty = repo.is_dirty(untracked_files=not ignore_untracked_files)
    repo_has_new_commits = repo.head.commit != tag_commit

    if not repo_has_new_commits and not repo_is_dirty:
        return version

    new_commits = 0
    if repo_has_new_commits:
        for commit in repo.iter_commits():
            _LOG.log(logging.NOTSET, 'iterating over commit %s', commit)
            if commit == tag_commit:
                break
            new_commits += 1
        _LOG.debug('there are %i new commits since %s', new_commits, version)

        version.devel_increment(new_commits)

        commit_sha = repo.head.commit.hexsha[:8]
        version.local = (commit_sha,)

    if repo_is_dirty:
        dt_ = 'dirty{}'.format(datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S'))
        if version.has_local:
            version.local += ('.', dt_)
        else:
            version.local = (dt_,)

    return version


def query_git_repo(
        repo_path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    """Determine version from tags of a git repository."""
    _LOG.debug('looking for git repository in "%s"', repo_path)
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    _LOG.debug('found git repository in "%s"', repo.working_dir)
    return _latest_git_tag_version(repo)[-1]


def predict_git_repo(repo_path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    return _upcoming_git_tag_version(repo)
