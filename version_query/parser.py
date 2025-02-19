"""Functions for parsing version strings into their components and verifying the format."""

import logging
import typing as t

from . import patterns

_LOG = logging.getLogger(__name__)


def parse_release_str(release: str) -> tuple:
    """Parse a release string into major, minor, and patch version numbers."""
    match = patterns.RELEASE.fullmatch(release)
    assert match is not None
    major_match = match.group('major')
    assert major_match is not None
    major = int(major_match)
    minor_match = match.group('minor')
    if minor_match is not None:
        minor = int(minor_match)
    else:
        minor = None
    patch_match = match.group('patch')
    if patch_match is not None:
        patch = int(patch_match)
    else:
        patch = None
    return major, minor, patch


def parse_pre_release_str(pre_release: str) -> t.Sequence[
        t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]]:
    """Parse a pre-release string into a sequence of tuples."""
    parts = patterns.PRE_RELEASE.findall(pre_release)
    _LOG.debug('parsed pre-release string %s into %s', repr(pre_release), parts)
    tuples = []
    for part in parts:
        match = patterns.PRE_RELEASE_PART.fullmatch(part)
        assert match is not None
        pre_patch_match = match.group('prepatch')
        if pre_patch_match is not None:
            pre_patch = int(pre_patch_match)
        else:
            pre_patch = None
        tuples.append((match.group('preseparator'), match.group('pretype'), pre_patch))
    return tuples


def parse_local_str(local: str) -> tuple:
    """Parse a local version suffix string into a sequence."""
    match = patterns.LOCAL.fullmatch(local)
    assert match is not None
    return tuple(_ for _ in match.groups() if _ is not None)
