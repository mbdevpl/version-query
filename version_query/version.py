"""Version string parser and generator."""

import logging
import re

import packaging
import pkg_resources

_LOG = logging.getLogger(__name__)


class Version:

    """Version information parser and unparser."""

    _num = r'0|[123456789][0123456789]*'
    _major = r'(?P<major>{})'.format(_num)
    _minor = r'\.(?P<minor>{})'.format(_num)
    _release = r'\.(?P<release>{})'.format(_num)
    _patch = r'\.(?P<suffix>a|b|rc|dev)?(?P<patch>{})'.format(_num)
    _sha = r'\+(?P<sha>[0123456789\.abcdef]+)'
    _version = r'(v|ver)?{}({})?({})?({})?({})?'.format(_major, _minor, _release, _patch, _sha)
    version_pattern = re.compile(_version)

    version_tuple_checker = lambda version_tuple, flags: all([
        (_ is not None if flag else _ is None) for _, flag  in zip(version_tuple, flags)])

    @classmethod
    def parse_str(cls, version_str: str):
        """Parse given version string into actionable version information."""
        assert isinstance(version_str, str), (type(version_str), version_str)

        version = pkg_resources.parse_version(version_str) # type: packaging.version.Version
        _LOG.debug('preliminarily parsed version string into %s: %s', type(version), version)

        match = cls.version_pattern.match(version_str)

        if match is None:
            raise packaging.version.InvalidVersion(
                'version string "{}" is invalid'.format(version_str))

        major = int(match.group('major'))
        minor = None if match.group('minor') is None else int(match.group('minor'))
        release = None if match.group('release') is None else int(match.group('release'))
        suffix = match.group('suffix')
        patch = None if match.group('patch') is None else int(match.group('patch'))
        commit_sha = match.group('sha')

        version_tuple = major, minor, release, suffix, patch, commit_sha
        _LOG.debug('parsed version string into tuple: %s', version_tuple)
        return version_tuple

    @classmethod
    def generate_str(
            cls, major: int = None, minor: int = None, release: int = None,
            suffix: str = None, patch: int = None, commit_sha: str = None) -> str:
        """Convert given version information to version string."""
        version_tuple = major, minor, release, suffix, patch, commit_sha
        _LOG.debug('generating version string from tuple %s', version_tuple)

        assert major is None or isinstance(major, int), (type(major), major, version_tuple)
        assert minor is None or isinstance(minor, int), (type(minor), minor, version_tuple)
        assert release is None or isinstance(release, int), (type(release), release, version_tuple)
        assert suffix is None or isinstance(suffix, str), (type(suffix), suffix, version_tuple)
        assert patch is None or isinstance(patch, int), (type(patch), patch, version_tuple)
        assert commit_sha is None or isinstance(commit_sha, str), (type(commit_sha), commit_sha, version_tuple)

        version_str = None
        if cls.version_tuple_checker(version_tuple, (True, False, False, False, False, False)):
            version_str = '{}'.format(major)
        elif cls.version_tuple_checker(version_tuple, (True, True, False, False, False, False)):
            version_str = '{}.{}'.format(major, minor)
        elif cls.version_tuple_checker(version_tuple, (True, False, False, False, False, True)):
            version_str = '{}.+{}'.format(major, commit_sha)
        elif cls.version_tuple_checker(version_tuple, (True, True, True, False, False, False)):
            version_str = '{}.{}.{}'.format(major, minor, release)
        elif cls.version_tuple_checker(version_tuple, (True, True, False, False, False, True)):
            version_str = '{}.{}.+{}'.format(major, minor, commit_sha)
        elif cls.version_tuple_checker(version_tuple, (True, True, True, True, False, False)):
            version_str = '{}.{}.{}.{}'.format(major, minor, release, suffix)
        elif cls.version_tuple_checker(version_tuple, (True, True, True, False, True, False)):
            version_str = '{}.{}.{}.{}'.format(major, minor, release, patch)
        elif cls.version_tuple_checker(version_tuple, (True, True, True, False, False, True)):
            version_str = '{}.{}.{}+{}'.format(major, minor, release, commit_sha)
        elif cls.version_tuple_checker(version_tuple, (True, True, True, True, True, False)):
            version_str = '{}.{}.{}.{}{}'.format(major, minor, release, suffix, patch)
        elif cls.version_tuple_checker(version_tuple, (True, True, True, True, True, True)):
            version_str = '{}.{}.{}.{}{}+{}'.format(major, minor, release, suffix, patch, commit_sha)

        if version_str is None:
            raise NotImplementedError(*version_tuple)
        _LOG.debug('generated version string: "%s"', version_str)
        return version_str
