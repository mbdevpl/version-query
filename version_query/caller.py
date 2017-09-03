""""""

import inspect
import logging
import pathlib

_LOG = logging.getLogger(__name__)


def get_caller_folder(inspect_level: int = 1):
    """Generate version string by querying all available information sources."""
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
