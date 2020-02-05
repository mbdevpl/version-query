"""Python package version query tools."""

import logging
import json
import pathlib

from .version import Version

_LOG = logging.getLogger(__name__)


def query_metadata_json(path: pathlib.Path) -> Version:
    """Get version from metadata.json file."""
    with path.open('r') as metadata_file:
        metadata = json.load(metadata_file)
    version_str = metadata['version']
    return Version.from_str(version_str)


def query_pkg_info(path: pathlib.Path) -> Version:
    """Get version from PKG-INFO file."""
    with path.open('r') as pkginfo_file:
        for line in pkginfo_file:
            if line.startswith('Version:'):
                version_str = line.replace('Version:', '').strip()
                return Version.from_str(version_str)
    raise ValueError(path)


def query_package_folder(path: pathlib.Path, search_parent_directories: bool = False) -> Version:
    """Get version from Python package folder."""
    paths = [path]
    if search_parent_directories:
        paths += path.parents
    metadata_json_paths, pkg_info_paths = None, None
    for pth in paths:
        metadata_json_paths = list(pth.parent.glob(f'{pth.name}*.dist-info/metadata.json'))
        pkg_info_paths = list(pth.parent.glob(f'{pth.name}*.egg-info/PKG-INFO'))
        pkg_info_paths += list(pth.parent.glob(f'{pth.name}*.dist-info/METADATA'))
        if len(metadata_json_paths) == 1 and not pkg_info_paths:
            return query_metadata_json(metadata_json_paths[0])
        if not metadata_json_paths and len(pkg_info_paths) == 1:
            return query_pkg_info(pkg_info_paths[0])
    raise ValueError(paths, metadata_json_paths, pkg_info_paths)
