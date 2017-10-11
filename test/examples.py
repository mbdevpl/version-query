"""Examples for tests."""

import itertools
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
    """Get root folder of currently running Python libraries.

    Currently works only for CPython.
    """
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

INIT_CASES = {
    '1': ((1,), {}),
    '1.0': ((1, 0), {}),
    '1.0.0': ((1, 0, 0), {}),
    '1.0.0.rc2': ((1, 0, 0, '.', 'rc', 2), {}),
    '1.0.0.rc3': ((1, 0, 0, ('.', 'rc', 3)), {}),
    '1.0.0.rc2+local': ((1, 0, 0, '.', 'rc', 2, 'local'), {}),
    '1.0.0.rc3+local': ((1, 0, 0, ('.', 'rc', 3), 'local'), {}),
    '1.0.0.rc4+local': ((1, 0, 0, ('.', 'rc', 4), ('local',)), {})}

BAD_INIT_CASES = {
    (('spam',), ()): TypeError,
    ((-1,), ()): ValueError,
    ((1, 'ham'), ()): TypeError,
    ((1, -2), ()): ValueError,
    ((1,), (('patch', 13),)): ValueError,
    ((1, 0, 'eggs'), ()): TypeError,
    ((1, 0, -3), ()): ValueError,
    ((1, 0, 0, 0), ()): TypeError,
    ((1, 0, 0, '.', 'dev'), ()): ValueError,
    ((1, 0, 0, '.'), ()): ValueError,
    ((1, 0, 0, '.', 1), ()): ValueError,
    ((1, 0, 0, ('.', None, 1), ('.', 'dev'), ('local',)), ()): ValueError,
    ((1, 0, 0, 0, ), (('pre_release', ((None, 'dev', 0),)), ('local', 'bad'))): ValueError,
    ((5,), (('pre_release', 1),)): TypeError,
    ((5,), (('pre_release', ()),)): ValueError,
    ((5,), (('pre_release', (0,)),)): TypeError,
    ((5,), (('pre_release', ('dev',)),)): TypeError,
    ((5,), (('pre_release', ((None, 'dev'),)),)): ValueError,
    ((6,), (('pre_release', ((42, 'dev', 0),)),)): TypeError,
    ((6,), (('pre_release', (('spam', 'dev', 0),)),)): ValueError,
    ((6,), (('pre_release', ((None, 42, 0),)),)): TypeError,
    ((6,), (('pre_release', ((None, 'd-v', 0),)),)): ValueError,
    ((6,), (('pre_release', ((None, 'dev', 'eggs'),)),)): TypeError,
    ((6,), (('pre_release', ((None, 'dev', -1),)),)): ValueError,
    ((6,), (('pre_release', ((None, None, 1),)),)): ValueError,
    ((6,), (('pre_release', (('.', None, None),)),)): ValueError,
    ((7,), (('local', 0),)): TypeError,
    ((7,), (('local', ('abc', '.')),)): ValueError,
    ((7,), (('local', (0,)),)): TypeError,
    ((7,), (('local', ('a.c',)),)): ValueError,
    ((7,), (('local', ('abc', 1, 'def')),)): TypeError,
    ((7,), (('local', ('abc', 'def')),)): ValueError,
    ((7,), (('local', ('abc', '.', 9)),)): TypeError}

COMPATIBLE_STR_CASES = {
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

INCOMPATIBLE_STR_CASES = {
    '1.0.0-2': ((1, 0, 0, '-', None, 2), {}),
    '1.0.0-0.2': ((1, 0, 0, '-', None, 0, '.', None, 2), {}),
    '4.5.0.dev': ((4, 5, 0, '.', 'dev', None), {})}

STR_CASES = dict(itertools.chain(COMPATIBLE_STR_CASES.items(),
                                 INCOMPATIBLE_STR_CASES.items()))

BAD_STR_CASES = {
    '-1.0.0': ValueError,
    '1.0.0.ekhm_what': ValueError}


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
    '1.0.0': '1.0.0+blahblah',
    '1.0.0+aa': '1.0.0+aaa'}

COMPARISON_CASES_EQUAL = {
    '1.0.0': '1.0.0',
    '1': '1.0.0',
    '1.0': '1.0.0.0',
    '1.0.0-0.0.DEV42': '1.0.0.0.0.dev42'}
