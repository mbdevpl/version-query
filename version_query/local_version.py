"""Use this module when reading the version from an attribute is needed without Python code.

For example, when using setuptools in pyproject.toml,
one can set the version dynamically as follows:

[project]
dynamic = ["version"]
...

[tool.setuptools.dynamic]
version = {attr = "version_query.local_version.PREDICTED"}
"""

import pathlib

from .query import query_folder, predict_folder

_CURRENT_FOLDER: pathlib.Path = pathlib.Path()
QUERIED: str = query_folder(_CURRENT_FOLDER).to_str()
PREDICTED: str = predict_folder(_CURRENT_FOLDER).to_str()
