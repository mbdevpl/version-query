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


def _pick_metadata_json_path(*metadata_json_paths: pathlib.Path) -> pathlib.Path | None:
    if not metadata_json_paths:
        return None
    if len(metadata_json_paths) == 1:
        return metadata_json_paths[0]
    versions = []
    for path in metadata_json_paths:
        versions.append(query_metadata_json(path))
    if all(v == versions[0] for v in versions[1:]):
        return metadata_json_paths[0]
    _LOG.warning(
        'found differing versions in provided JSON metadata files %s: %s',
        metadata_json_paths, versions)
    return None


def _pick_pkg_info_path(*pkg_info_paths: pathlib.Path) -> pathlib.Path | None:
    if not pkg_info_paths:
        return None
    if len(pkg_info_paths) == 1:
        return pkg_info_paths[0]
    versions = []
    for path in pkg_info_paths:
        versions.append(query_pkg_info(path))
    if all(v == versions[0] for v in versions[1:]):
        return pkg_info_paths[0]
    _LOG.warning(
        'found differing versions in provided PKG-INFO files %s: %s',
        pkg_info_paths, versions)
    return None


def query_package_folder(path: pathlib.Path, search_parent_directories: bool = False) -> Version:
    """Get version from Python package folder."""
    global_metadata_json_paths, global_pkg_info_paths = [], []
    if path.joinpath('pyproject.toml').exists() or path.joinpath('setup.py').exists():
        metadata_json_paths = [*path.glob('metadata.json'), *path.glob('*.dist-info/metadata.json')]
        metadata_json_path = _pick_metadata_json_path(*metadata_json_paths)
        pkg_info_paths = [
            *path.glob('PKG-INFO'), *path.glob('*.egg-info/PKG-INFO'),
            *path.glob('METADATA'), *path.glob('*.dist-info/METADATA')]
        pkg_info_path = _pick_pkg_info_path(*pkg_info_paths)
        if metadata_json_path is not None and pkg_info_path is None:
            return query_metadata_json(metadata_json_path)
        if metadata_json_path is None and pkg_info_path is not None:
            return query_pkg_info(pkg_info_path)
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
        metadata_json_paths = [*pth.parent.glob(f'{pth.name}*.dist-info/metadata.json')]
        metadata_json_path = _pick_metadata_json_path(*metadata_json_paths)
        pkg_info_paths = [
            *pth.parent.glob(f'{pth.name}*.egg-info/PKG-INFO'),
            *pth.parent.glob(f'{pth.name}*.dist-info/METADATA')]
        pkg_info_path = _pick_pkg_info_path(*pkg_info_paths)
        if metadata_json_path is not None and pkg_info_path is None:
            return query_metadata_json(metadata_json_path)
        if metadata_json_path is None and pkg_info_path is not None:
            return query_pkg_info(pkg_info_path)
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
