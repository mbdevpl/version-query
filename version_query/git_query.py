"""Git repository version query tools."""

import datetime
import logging
import pathlib
import typing as t

import git

from .version import Version

_LOG = logging.getLogger(__name__)


def _git_version_tags(repo: git.Repo) -> t.Mapping[git.Tag, Version]:
    versions = {}
    for tag in repo.tags:
        tag_str = str(tag)
        if tag_str.startswith('ver'):
            tag_str = tag_str[3:]
        elif tag_str.startswith('v'):
            tag_str = tag_str[1:]
        elif tag_str and tag_str[0] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            pass
        else:
            _LOG.debug('%s: ignoring non-version tag %s', repo, tag_str)
            continue
        try:
            versions[tag] = Version.from_str(tag_str)
        except ValueError:
            # except packaging.version.InvalidVersion:
            _LOG.warning('%s: failed to convert %s to version', repo, tag_str)
            continue
    return versions


MAX_COMMIT_DISTANCE = 999


def _latest_git_version_tag(
        repo: git.Repo, assume_if_none: bool = False, base_commit: git.Commit = None,
        commit_distance: int = 0, skip_commits: t.Set[git.Commit] = None) -> t.Tuple[
            git.Commit, t.Optional[git.TagReference], Version, int]:
    """Retrun (commit, tag at that commit if any, latest version, distance from the version)."""
    version_tags = _git_version_tags(repo)
    version_tag_commits = {}
    for tag, version in version_tags.items():
        commit = tag.commit
        if commit not in version_tag_commits:
            version_tag_commits[commit] = set()
        version_tag_commits[commit].add(tag)
    current_version_tags = {}
    commit = None
    if skip_commits is None:
        skip_commits = set()
    for commit in repo.iter_commits(rev=base_commit):
        if commit in skip_commits:
            return None, None, None, -1
        _LOG.log(logging.NOTSET, 'iterating over commit %s', commit)
        skip_commits.add(commit)
        if commit in version_tag_commits:
            current_tags = version_tag_commits[commit]
            current_version_tags = {tag: version for tag, version in version_tags.items()
                                    if tag in current_tags}
            _LOG.log(logging.NOTSET, 'found version data %s', current_version_tags)
            break
        if commit_distance >= MAX_COMMIT_DISTANCE:
            raise ValueError('reached max commit distance {} with no version tags in repo {}'
                             .format(MAX_COMMIT_DISTANCE, repo))
        commit_distance += 1
        if len(commit.parents) <= 1:
            continue
        _LOG.log(logging.NOTSET, 'entering %i branches...', len(commit.parents))
        results = []
        main_commit_distance = None
        for parent in commit.parents:
            try:
                result = _latest_git_version_tag(
                    repo, assume_if_none, parent, commit_distance, skip_commits)
                if main_commit_distance is None:
                    main_commit_distance = result[3]
            except ValueError:
                continue
            if result[2] is not None:
                results.append(result)
        if not results:
            commit_distance = main_commit_distance
            break
        result = sorted(results, key=lambda _: _[2])[-1]
        _LOG.log(logging.NOTSET, 'result from %i branches is %s and %s',
                 len(commit.parents), *result[1:3])
        return result
    if not current_version_tags:
        if assume_if_none:
            return commit, None, Version.from_str('0.1.0.dev0'), commit_distance
        else:
            raise ValueError('the given repo {} has no version tags'.format(repo))
    tag, version = sorted(current_version_tags.items(), key=lambda _: _[1])[-1]
    _LOG.log(logging.NOTSET, 'result is %s and %s', tag, version)
    return commit, tag, version, commit_distance


def _upcoming_git_version_tag(repo: git.Repo, ignore_untracked_files: bool = True) -> t.Tuple[
        git.Commit, t.Optional[git.TagReference], Version, int, bool]:
    commit, tag, version, commit_distance = _latest_git_version_tag(repo, True)
    is_repo_dirty = repo.is_dirty(untracked_files=not ignore_untracked_files)
    return commit, tag, version, commit_distance, is_repo_dirty


def query_git_repo(repo_path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    """Determine version from tags of a git repository."""
    _LOG.debug('looking for git repository in "%s"', repo_path)
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    _LOG.debug('found git repository in "%s"', repo.working_dir)
    return _latest_git_version_tag(repo)[2]


def predict_git_repo(repo_path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    """Predict version from tags, commit history and index status of git repository."""
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    version, commit_distance, is_repo_dirty = _upcoming_git_version_tag(repo)[2:]
    if commit_distance > 0:
        version.devel_increment(commit_distance)
        version.local = (repo.head.commit.hexsha[:8],)
    if is_repo_dirty:
        dt_ = 'dirty{}'.format(datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S'))
        if version.has_local:
            version.local += ('.', dt_)
        else:
            version.local = (dt_,)
    return version
