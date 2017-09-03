"""Creator of git tag with current or upcoming version of a package."""

import pathlib


def create_version_tag_in_git_repo(repo_path: pathlib.Path, search_parent_directories: bool = True):
    raise NotImplementedError()


def create_git_tag_for_caller(inspect_level: int = 1):
    raise NotImplementedError()
