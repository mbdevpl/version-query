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
    global_metadata_json_paths, global_pkg_info_paths = [], []
    if path.joinpath('pyproject.toml').exists() or path.joinpath('setup.py').exists():
        metadata_json_paths = list(path.glob('*.dist-info/metadata.json'))
        pkg_info_paths = list(path.glob('*.egg-info/PKG-INFO'))
        pkg_info_paths += list(path.glob('*.dist-info/METADATA'))
        if len(metadata_json_paths) == 1 and not pkg_info_paths:
            return query_metadata_json(metadata_json_paths[0])
        if not metadata_json_paths and len(pkg_info_paths) == 1:
            return query_pkg_info(pkg_info_paths[0])
        _LOG.debug(
            'in %s found pyproject.toml or setup.py, as well as'
            ' %i JSON metadata: %s and %i PKG-INFO metadata: %s'
            ' - unable to infer package metadata, continuing search',
            path, len(metadata_json_paths), metadata_json_paths, len(pkg_info_paths),
            pkg_info_paths)
        global_metadata_json_paths.extend(metadata_json_paths)
        global_pkg_info_paths.extend(pkg_info_paths)
    paths = [path]
    if search_parent_directories:
        paths += path.parents
    for pth in paths:
        metadata_json_paths = list(pth.parent.glob(f'{pth.name}*.dist-info/metadata.json'))
        pkg_info_paths = list(pth.parent.glob(f'{pth.name}*.egg-info/PKG-INFO'))
        pkg_info_paths += list(pth.parent.glob(f'{pth.name}*.dist-info/METADATA'))
        if len(metadata_json_paths) == 1 and not pkg_info_paths:
            return query_metadata_json(metadata_json_paths[0])
        if not metadata_json_paths and len(pkg_info_paths) == 1:
            return query_pkg_info(pkg_info_paths[0])
        _LOG.debug(
            'in %s found %i JSON metadata: %s and %i PKG-INFO metadata: %s'
            ' - unable to infer package metadata, continuing search',
            pth, len(metadata_json_paths), metadata_json_paths, len(pkg_info_paths), pkg_info_paths)
        global_metadata_json_paths.extend(metadata_json_paths)
        global_pkg_info_paths.extend(pkg_info_paths)
    raise ValueError(
        f'unable to infer package metadata from the following paths {paths} '
        f'- found {len(global_metadata_json_paths)} JSON metadata: {global_metadata_json_paths}'
        f' and {len(global_pkg_info_paths)} PKG-INFO metadata: {global_pkg_info_paths}')
