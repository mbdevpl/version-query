"""Initialization of version_query package."""

__all__ = ['VersionComponent', 'Version',
           'query_folder', 'query_caller', 'query_version_str', 'predict_git_repo',
           'predict_caller', 'predict_version_str']

from .version import VersionComponent, Version
from .query import query_folder, query_caller, query_version_str
from .git_query import predict_git_repo
from .query import predict_caller, predict_version_str
