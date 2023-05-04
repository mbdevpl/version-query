"""Examples for tests."""

import itertools
import os
import pathlib
import platform
import sys
import typing as t

from version_query.version import VersionComponent

_HERE = pathlib.Path(__file__).resolve().parent

_GIT_REPOS_ROOT = pathlib.Path(os.environ['EXAMPLE_PROJECTS_PATH']).absolute()

GIT_REPO_EXAMPLES = list(_ for _ in _GIT_REPOS_ROOT.glob('**/.git') if _.is_dir())


def python_lib_dir() -> pathlib.Path:
    """Get root folder of currently running Python libraries.

    Currently works only for CPython and PyPy.
    """
    lib_dir_parts = [getattr(sys, 'real_prefix', sys.prefix)]
    if platform.python_implementation() == 'CPython':
        lib_dir_parts.append('lib')
        if platform.system() != 'Windows':
            lib_dir_parts.append('python{}.{}'.format(*sys.version_info[:2]))
    else:
        assert platform.python_implementation() == 'PyPy'
        lib_dir_parts += ['lib-python', '{}'.format(*sys.version_info[:1])]

    lib_dir = pathlib.Path(*lib_dir_parts)
    assert lib_dir.is_dir(), lib_dir
    return lib_dir


PY_LIB_DIR = python_lib_dir()

_SYS_DIST_INFOS = list(PY_LIB_DIR.glob('**/*.dist-info'))
_SYS_EGG_INFOS = list(PY_LIB_DIR.glob('**/*.egg-info'))
_USER_DIST_INFOS = [pth for _ in _GIT_REPOS_ROOT.glob('*') for pth in _.glob('*.dist-info')]
_USER_EGG_INFOS = [pth for _ in _GIT_REPOS_ROOT.glob('*') for pth in _.glob('*.egg-info')]
# print(_SYS_DIST_INFOS, _SYS_EGG_INFOS, _USER_DIST_INFOS, _USER_EGG_INFOS)

METADATA_JSON_EXAMPLE_PATHS = list(itertools.chain.from_iterable(
    _.glob('metadata.json') for _ in itertools.chain(_SYS_DIST_INFOS, _USER_DIST_INFOS)))
PKG_INFO_EXAMPLE_PATHS = list(itertools.chain.from_iterable(
    _.glob('PKG-INFO') for _ in itertools.chain(_SYS_EGG_INFOS, _USER_EGG_INFOS)))


def _remove_version_suffixes(path: pathlib.Path) -> t.Optional[pathlib.Path]:
    name = path.with_suffix('').name
    i = name.rfind('-')
    if i > 0:
        name = name[:i]
    path = path.with_name(name)
    return path if path.is_dir() else None


PACKAGE_FOLDER_EXAMPLES = [pth for pth in [
    _remove_version_suffixes(_)
    for _ in itertools.chain(_SYS_DIST_INFOS, _SYS_EGG_INFOS, _USER_DIST_INFOS, _USER_EGG_INFOS)]
                           if pth is not None]
# print(PACKAGE_FOLDER_EXAMPLES)

KWARG_NAMES = ('major', 'minor', 'patch', 'pre_release', 'local')

INIT_CASES: t.Dict[str, t.Tuple[tuple, dict]] = {
    '1': ((1,), {}),
    '1.0': ((1, 0), {}),
    '1.0.0': ((1, 0, 0), {}),
    '1.0.0rc1': ((1, 0, 0, None, 'rc', 1), {}),
    '1.0.0rc2': ((1, 0, 0, None, 'rc', 2), {}),
    '1.0.0.rc2': ((1, 0, 0, '.', 'rc', 2), {}),
    '1.0.0rc3': ((1, 0, 0, None, 'rc', 3), {}),
    '1.0.0.rc3': ((1, 0, 0, ('.', 'rc', 3)), {}),
    '1.0.0.rc2+local': ((1, 0, 0, '.', 'rc', 2, 'local'), {}),
    '1.0.0.rc3+local': ((1, 0, 0, ('.', 'rc', 3), 'local'), {}),
    '1.0.0.rc4+local': ((1, 0, 0, ('.', 'rc', 4), ('local',)), {})}

BAD_INIT_CASES: t.Dict[t.Tuple[tuple, tuple], t.Type[Exception]] = {
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
    ((1, 0, 0, 0, ), (('pre_release', None), ('local', 'abc'))): ValueError,
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
    '1.0.0rc1': ((1, 0, 0, None, 'rc', 1), {}),
    '1.0.0rc3': ((1, 0, 0, None, 'rc', 3), {}),
    '1.0.1.dev0': ((1, 0, 1, '.', 'dev', 0), {}),
    '0.4.4.dev5+84e1d430': ((0, 4, 4, '.', 'dev', 5, '84e1d430'), {}),
    '0.4.4.dev5+20171003.84e1d430': ((0, 4, 4, '.', 'dev', 5, '20171003', '.', '84e1d430'), {})}

INCOMPATIBLE_STR_CASES: t.Dict[str, t.Tuple[tuple, dict]] = {
    '1.0.0-2': ((1, 0, 0, '-', None, 2), {}),
    # '1.0.0-0.2': ((1, 0, 0, '-', None, 0, '.', None, 2), {}),
    '1.0.0.rc3': ((1, 0, 0, '.', 'rc', 3), {}),
    '4.5.0.dev': ((4, 5, 0, '.', 'dev', None), {})}

STR_CASES = dict(itertools.chain(COMPATIBLE_STR_CASES.items(),
                                 INCOMPATIBLE_STR_CASES.items()))

BAD_STR_CASES = {
    '-1.0.0': ValueError,
    '1.0.0.ekhm_what': ValueError}


def case_to_version_tuple(args, kwargs):
    """Convert parameters of a given test case to a version tuple.

    To be converted are args and kwargs meant for Version.__init__().
    """
    return args + tuple(
        v for _, v in sorted(kwargs.items(), key=lambda _: KWARG_NAMES.index(_[0])))


INCREMENT_CASES = {
    ('1', (VersionComponent.Major,)): '2',
    ('1', (VersionComponent.Minor,)): '1.1',
    ('1', (VersionComponent.Patch, 8)): '1.0.8',
    ('1', (VersionComponent.PrePatch,)): '1-1',
    ('1', (VersionComponent.DevPatch,)): '1.dev1',
    ('1.5', (VersionComponent.Major,)): '2.0',
    ('1.5', (VersionComponent.Minor, 3)): '1.8',
    ('1.5', (VersionComponent.Patch,)): '1.5.1',
    ('1.5', (VersionComponent.PrePatch, 2)): '1.5-2',
    ('1.5', (VersionComponent.DevPatch,)): '1.5.dev1',
    ('1.5.1', (VersionComponent.Major, 3)): '4.0.0',
    ('1.5.1', (VersionComponent.Minor,)): '1.6.0',
    ('1.5.1', (VersionComponent.Patch,)): '1.5.2',
    ('1.5.1', (VersionComponent.PrePatch,)): '1.5.1-1',
    ('1.5.1', (VersionComponent.DevPatch,)): '1.5.1.dev1',
    ('1.5.1-2.4', (VersionComponent.Major,)): '2.0.0',
    ('1.5.1-2.4', (VersionComponent.Minor,)): '1.6',
    ('1.5.1-2.4', (VersionComponent.Patch,)): '1.5.2',
    ('1.5.1-0', (VersionComponent.PrePatch, 5)): '1.5.1-5',
    ('1.5.1-2.4', (VersionComponent.PrePatch,)): '1.5.1-3',
    ('1.5.1-2.4', (VersionComponent.DevPatch,)): '1.5.1-2.4.dev1',
    ('1.5-2.dev', (VersionComponent.PrePatch,)): '1.5-3',
    ('1.5-2.4.dev', (VersionComponent.DevPatch,)): '1.5-2.4.dev1',
    ('1.5-2.dev4', (VersionComponent.PrePatch,)): '1.5-3',
    ('1.5-2.4.dev4', (VersionComponent.DevPatch,)): '1.5-2.4.dev5',
    ('1.5.1-rc', (VersionComponent.PrePatch,)): '1.5.1-1',
    ('1.5.1-rc4', (VersionComponent.PrePatch, 2)): '1.5.1-2',
    ('0.dev', (VersionComponent.DevPatch,)): '0.dev1',
    ('0.dev2', (VersionComponent.DevPatch,)): '0.dev3',
    ('0.3dev', (VersionComponent.DevPatch,)): '0.3dev1',
    ('0.3dev2', (VersionComponent.DevPatch,)): '0.3dev3',
    ('0.3.5dev', (VersionComponent.DevPatch,)): '0.3.5dev1',
    ('0.3.5dev2', (VersionComponent.DevPatch,)): '0.3.5dev3'}

DEVEL_INCREMENT_CASES = {
    ('1', ()): '1.0.1.dev1',
    ('1', (3,)): '1.0.1.dev3',
    ('1.5', ()): '1.5.1.dev1',
    ('1.5', (3,)): '1.5.1.dev3',
    ('1.5.1', ()): '1.5.2.dev1',
    ('1.5.1', (3,)): '1.5.2.dev3',
    ('1.5.1-2.4', ()): '1.5.2.dev1',
    ('1.5.1-2.4', (3,)): '1.5.2.dev3',
    ('0.dev2', ()): '0.dev3',
    ('0.dev2', (3,)): '0.dev5',
    ('0.3.dev2', ()): '0.3.dev3',
    ('0.3.dev2', (3,)): '0.3.dev5',
    ('0.3.5dev2', ()): '0.3.5dev3',
    ('0.3.5dev2', (3,)): '0.3.5dev5',
    ('0.3.5-2.4.dev2', ()): '0.3.5-2.4.dev3',
    ('0.3.5-2.4.dev2', (3,)): '0.3.5-2.4.dev5'}

COMPARISON_CASES_LESS = {
    '0.3-4.4-2.9': '0.3-4.4-2.10',
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
