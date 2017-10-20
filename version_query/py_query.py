"""Python package version query tools."""

import logging
import json
import pathlib

from .version import Version

_LOG = logging.getLogger(__name__)


def query_metadata_json(path: pathlib.Path) -> Version:
    """Get version from metadata.json file."""
    with open(str(path), 'r') as metadata_file:
        metadata = json.load(metadata_file)
    version_str = metadata['version']
    return Version.from_str(version_str)


def query_pkg_info(path: pathlib.Path) -> Version:
    """Get version from PKG-INFO file."""
    with open(str(path), 'r') as pkginfo_file:
        for line in pkginfo_file:
            if line.startswith('Version:'):
                version_str = line.replace('Version:', '').strip()
                return Version.from_str(version_str)
    raise ValueError(path)


def query_package_folder(path: pathlib.Path, search_parent_directories: bool = False) -> Version:
    """Get version from Python package folder."""
    paths = [path] + (list(path.parents) if search_parent_directories else [])
    metadata_json_paths, pkg_info_paths = None, None
    for pth in paths:
        metadata_json_paths = list(pth.parent.glob('{}*.dist-info/metadata.json'.format(pth.name)))
        pkg_info_paths = list(pth.parent.glob('{}*.egg-info/PKG-INFO'.format(pth.name)))
        if len(metadata_json_paths) == 1 and len(pkg_info_paths) == 0:
            return query_metadata_json(metadata_json_paths[0])
        if len(metadata_json_paths) == 0 and len(pkg_info_paths) == 1:
            return query_pkg_info(pkg_info_paths[0])
    raise ValueError(paths, metadata_json_paths, pkg_info_paths)
