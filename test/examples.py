"""Examples for tests."""

import pathlib
import platform
import sys

from version_query.version import VersionComponent

_HERE = pathlib.Path(__file__).resolve().parent

_PACKAGE_FOLDER = _HERE.parent

_GIT_REPOS_ROOT = _PACKAGE_FOLDER.parent
if platform.system() != 'Windows':
    _GIT_REPOS_ROOT = _GIT_REPOS_ROOT.parent

GIT_REPO_EXAMPLES = list(_ for _ in _GIT_REPOS_ROOT.glob('**/.git') if _.is_dir())


def python_lib_dir() -> pathlib.Path:
    lib_dir_parts = [getattr(sys, 'real_prefix', sys.prefix), 'lib']
    if platform.system() != 'Windows':
        lib_dir_parts.append('python{}.{}'.format(*sys.version_info[:2]))

    lib_dir = pathlib.Path(*lib_dir_parts)
    if not lib_dir.is_dir():
        raise ValueError(lib_dir)
    return lib_dir


METADATA_JSON_EXAMPLE_PATHS = list(python_lib_dir().glob('**/*.dist-info/metadata.json'))
PKG_INFO_EXAMPLE_PATHS = list(python_lib_dir().glob('**/*.egg-info/PKG-INFO'))

PACKAGE_FOLDER_EXAMPLES = list(_ for _ in _PACKAGE_FOLDER.parent.glob('*')
                               if list(_.glob('*.dist-info')) or list(_.glob('*.egg-info')))

KWARG_NAMES = ('major', 'minor', 'patch', 'pre_release', 'local')

COMPATIBLE_CASES = {
    '0': ((0, None, None), {}),
    '42': ((42, None, None), {}),
    '5+d2a610ba': ((5, None, None), {'local': 'd2a610ba'}),
    '0.1': ((0, 1, None), {}),
    '8.0': ((8, 0, None), {}),
    '16.4': ((16, 4, None), {}),
    '5.0+f753199e': ((5, 0, None), {'local': 'f753199e'}),
    '0.54.0': ((0, 54, 0), {}),
    '1.0.0': ((1, 0, 0), {}),
    '7.0.42+1d7b090a': ((7, 0, 42), {'local': '1d7b090a'}),
    '1.0.0.4': ((1, 0, 0, '.', None, 4), {}),
    '2.0.0.8+cc81cee': ((2, 0, 0, '.', None, 8, 'cc81cee'), {}),
    '4.5.0.dev1234': ((4, 5, 0, '.', 'dev', 1234), {}),
    '1.0.0.rc3': ((1, 0, 0, '.', 'rc', 3), {}),
    '1.0.1.dev0': ((1, 0, 1, '.', 'dev', 0), {}),
    '0.4.4.dev5+84e1d430': ((0, 4, 4, '.', 'dev', 5, '84e1d430'), {}),
    '0.4.4.dev5+20171003.84e1d430': ((0, 4, 4, '.', 'dev', 5, '20171003', '.', '84e1d430'), {})}

INCOMPATIBLE_CASES = {
    '1.0.0-2': ((1, 0, 0, '-', None, 2), {}),
    '1.0.0-0.2': ((1, 0, 0, '-', None, 0, '.', None, 2), {}),
    '4.5.0.dev': ((4, 5, 0, '.', 'dev', None), {})}


def case_to_version_tuple(args, kwargs):
    return args + tuple(
        v for _, v in sorted(kwargs.items(), key=lambda _: KWARG_NAMES.index(_[0])))


INCREMENT_CASES = {
    ('1.0', (VersionComponent.Minor,)): '1.1',
    ('1.5', (VersionComponent.Major,)): '2.0',
    ('0.3dev', (VersionComponent.DevPatch,)): '0.3dev1',
    ('0.3.5', (VersionComponent.DevPatch, 500)): '0.3.5.dev500',
    ('4.0.1-0.3', (VersionComponent.DevPatch, 2)): '4.0.1-0.3.dev2'}

COMPARISON_CASES_LESS = {
    '0.3dev': '0.3dev1',
    '0.3rc2': '0.3',
    '0.3': '0.3-2',
    '0.3-2rc5': '0.3-2',
    '0.3-2.dev5': '0.3-2',
    '0.3-2.dev42': '0.3-2',
    '0.3-4': '0.3-4.5',
    '1-1.2.3.4.5.dev4': '1-1.2.3.4.5',
    '1.0.0': '1.0.0+blahblah'}

COMPARISON_CASES_EQUAL = {
    '1.0.0': '1.0.0',
    '1': '1.0.0',
    '1.0': '1.0.0.0',
    '1.0.0-0.0.DEV42': '1.0.0.0.0.dev42'}
