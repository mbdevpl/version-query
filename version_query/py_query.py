"""Python package version query tools."""

import logging
import json
import pathlib

from .version import Version

_LOG = logging.getLogger(__name__)


'''
def query_manifest(path_prefix: pathlib.Path) -> Version:
    """Determine version from found PKG-INFO file."""
    _LOG.debug('looking for manifest in %s', path_prefix)
    version = None
    for path in path_prefix.parent.glob(path_prefix.name + '*'):
        if path.suffix == '.dist-info':
            _LOG.debug('found distribution info directory %s', path)
            metadata_path = path.joinpath('metadata.json')
            version = query_metadata_json(metadata_path)
            _LOG.debug('version in metadata is: "%s"', version)
            break
        if path.suffix == '.egg-info':
            _LOG.debug('found egg info directory %s', path)
            pkginfo_path = path.joinpath('PKG-INFO')
            version = query_pkg_info(pkginfo_path)
            _LOG.debug('version in metadata is: "%s"', version)
            break
    if version is None:
        raise ValueError('version not found')
    return version
'''


def query_metadata_json(path: pathlib.Path) -> Version:
    with open(str(path), 'r') as metadata_file:
        metadata = json.load(metadata_file)
    version_str = metadata['version']
    return Version.from_str(version_str)


def query_pkg_info(path: pathlib.Path) -> Version:
    with open(str(path), 'r') as pkginfo_file:
        for line in pkginfo_file:
            if line.startswith('Version:'):
                version_str = line.replace('Version:', '').strip()
                return Version.from_str(version_str)
    raise ValueError(path)


def query_package_folder(path: pathlib.Path, search_parent_directories: bool = False) -> Version:
    paths = [path] + list(path.parents) if search_parent_directories else []
    metadata_json_paths, pkg_info_paths = None, None
    for path in paths:
        metadata_json_paths = list(path.glob('*.dist-info/metadata.json'))
        pkg_info_paths = list(path.glob('*.egg-info/PKG-INFO'))
        if len(metadata_json_paths) == 1 and len(pkg_info_paths) == 0:
            return query_metadata_json(metadata_json_paths[0])
        if len(metadata_json_paths) == 0 and len(pkg_info_paths) == 1:
            return query_pkg_info(pkg_info_paths[0])
    raise ValueError(metadata_json_paths, pkg_info_paths)
