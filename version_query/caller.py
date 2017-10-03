"""Tools to inspect caller of currently executing code."""

import inspect
import logging
import pathlib
import typing as t
import warnings

_LOG = logging.getLogger(__name__)

warnings.warn('module deprecated', DeprecationWarning, stacklevel=2)


def get_caller_folder(inspect_level: int = 1) -> pathlib.Path:
    """Generate version string by querying all available information sources."""
    warnings.warn('function deprecated', DeprecationWarning, stacklevel=2)
    frame_info = inspect.getouterframes(inspect.currentframe())[inspect_level]
    caller_path = frame_info[1] # frame_info.filename

    here = pathlib.Path(caller_path).absolute().resolve()
    if not here.is_file():
        raise RuntimeError('path "{}" was expected to be a file'.format(here))
    here = here.parent
    if not here.is_dir():
        raise RuntimeError('path "{}" was expected to be a directory'.format(here))
    _LOG.debug('found directory "%s"', here)

    return here

def get_caller_module_name(inspect_level: int = 1) -> t.Optional[str]:
    """Retrieve the name of the caller module, if it exists."""
    warnings.warn('function deprecated', DeprecationWarning, stacklevel=2)
    frame_info = inspect.getouterframes(inspect.currentframe())[inspect_level]
    caller_path = frame_info[1] # frame_info.filename
    function_name = frame_info[3] # frame_info.function

    if function_name != '<module>':
        return None

    if caller_path.endswith('.py'):
        caller_path = caller_path[:-3]

    return caller_path
