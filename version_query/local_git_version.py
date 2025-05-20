"""Use this module when reading the version from an attribute is needed without Python code.

For example, when using setuptools in pyproject.toml,
one can set the version dynamically as follows:

[project]
dynamic = ["version"]
...

[tool.setuptools.dynamic]
version = {attr = "version_query.local_git_version.PREDICTED"}
"""

import os
import pathlib

from .git_query import query_git_repo, predict_git_repo

_CURRENT_FOLDER: pathlib.Path = pathlib.Path()
_PROJECT_FOLDER: pathlib.Path = pathlib.Path(os.environ.get('PROJECT_FOLDER', _CURRENT_FOLDER))
QUERIED: str = query_git_repo(_PROJECT_FOLDER).to_str()
PREDICTED: str = predict_git_repo(_PROJECT_FOLDER).to_str()
