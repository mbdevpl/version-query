"""Git repository version query tools."""

import datetime
import logging
import pathlib
import typing as t

import git

from .version import Version

_LOG = logging.getLogger(__name__)


def preprocess_git_version_tag(tag: str):
    """Remove a prefix from a version tag."""
    if tag.startswith('ver'):
        return tag[3:]
    if tag.startswith('v'):
        return tag[1:]
    if tag and tag[0] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        return tag
    raise ValueError(f'given tag "{tag}" does not appear to be a version tag')


def _git_version_tags(repo: git.Repo) -> t.Mapping[git.Tag, Version]:
    versions = {}
    for tag in repo.tags:
        try:
            tag_str = preprocess_git_version_tag(str(tag))
        except ValueError:
            _LOG.debug('%s: ignoring non-version tag %s', repo, tag)
            continue
        try:
            versions[tag] = Version.from_str(tag_str)
        except ValueError:
            # except packaging.version.InvalidVersion:
            _LOG.warning('%s: failed to convert %s to version', repo, tag_str)
            continue
    return versions


def _latest_git_version_tag_on_branches(
        repo: git.Repo, assume_if_none: bool, commit: git.objects.Commit, commit_distance: int,
        skip_commits: t.Set[git.objects.Commit]) -> t.Union[int, t.Tuple[
            t.Optional[git.objects.Commit], t.Optional[git.TagReference], t.Optional[Version],
            int]]:
    _LOG.log(logging.NOTSET, 'entering %i branches...', len(commit.parents))
    results = []
    main_commit_distance = None
    for parent in commit.parents:
        try:
            result = _latest_git_version_tag(
                repo, assume_if_none, parent, commit_distance, skip_commits)
        except ValueError:
            continue
        if main_commit_distance is None:
            main_commit_distance = result[3]
        if result[2] is not None:
            results.append(result)
    if not results:
        if main_commit_distance is None:
            raise ValueError(f'reached max commit distance {MAX_COMMIT_DISTANCE}'
                             f' with no version tags in repo {repo}')
        return main_commit_distance
    final_result = sorted(results, key=lambda _: _[2])[-1]
    _LOG.log(logging.NOTSET, 'result from %i branches is %s and %s',
             len(commit.parents), *final_result[1:3])
    return final_result


MAX_COMMIT_DISTANCE = 999


def _latest_git_version_tag(
        repo: git.Repo, assume_if_none: bool = False, base_commit: git.objects.Commit = None,
        commit_distance: int = 0, skip_commits: t.Set[git.objects.Commit] = None) -> t.Tuple[
            t.Optional[git.objects.Commit], t.Optional[git.TagReference], t.Optional[Version], int]:
    """Return (commit, tag at that commit if any, latest version, distance from the version)."""
    version_tags = _git_version_tags(repo)
    version_tag_commits: t.Dict[git.objects.Commit, set] = {}
    for tag, version in version_tags.items():
        _commit = tag.commit
        if _commit not in version_tag_commits:
            version_tag_commits[_commit] = set()
        version_tag_commits[_commit].add(tag)
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
            raise ValueError(f'reached max commit distance {MAX_COMMIT_DISTANCE}'
                             f' with no version tags in repo {repo}')
        commit_distance += 1
        if len(commit.parents) <= 1:
            continue
        result = _latest_git_version_tag_on_branches(
            repo, assume_if_none, commit, commit_distance, skip_commits)
        if not isinstance(result, tuple):
            commit_distance = result  # main_commit_distance
            break
        return result
    if not current_version_tags:
        if assume_if_none:
            return commit, None, Version.from_str('0.1.0.dev0'), commit_distance
        raise ValueError(f'the given repo {repo} has no version tags')
    tag, version = sorted(current_version_tags.items(), key=lambda _: _[1])[-1]
    _LOG.log(logging.NOTSET, 'result is %s and %s', tag, version)
    return commit, tag, version, commit_distance


def _upcoming_git_version_tag(repo: git.Repo, ignore_untracked_files: bool = True) -> t.Tuple[
        t.Optional[git.objects.Commit], t.Optional[git.TagReference], t.Optional[Version], int,
        bool]:
    commit, tag, version, commit_distance = _latest_git_version_tag(repo, True)
    is_repo_dirty = repo.is_dirty(untracked_files=not ignore_untracked_files)
    return commit, tag, version, commit_distance, is_repo_dirty


def query_git_repo(repo_path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    """Determine version from tags of a git repository."""
    _LOG.debug('looking for git repository in "%s"', repo_path)
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    _LOG.debug('found git repository in "%s"', repo.working_dir)
    version = _latest_git_version_tag(repo)[2]
    assert isinstance(version, Version), version
    return version


def predict_git_repo(repo_path: pathlib.Path, search_parent_directories: bool = True) -> Version:
    """Predict version from tags, commit history and index status of git repository."""
    repo = git.Repo(str(repo_path), search_parent_directories=search_parent_directories)
    version, commit_distance, is_repo_dirty = _upcoming_git_version_tag(repo)[2:]
    assert isinstance(version, Version), version
    if commit_distance > 0:
        version.devel_increment(commit_distance)
        version.local = (f'git{repo.head.commit.hexsha[:8]}',)
    if is_repo_dirty:
        dt_ = f'dirty{datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S")}'
        if version.has_local:
            assert version.local is not None  # mypy needs this
            version.local = (*version.local, '.', dt_)
        else:
            version.local = (dt_,)
    return version
