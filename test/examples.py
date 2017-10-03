
import pathlib
import platform
import sys

_HERE = pathlib.Path(__file__).resolve().parent

_PACKAGE_FOLDER = _HERE.parent

GIT_REPO_EXAMPLES = list(_ for _ in _PACKAGE_FOLDER.parent.parent.glob('**/.git')
                         if _.is_dir())


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
