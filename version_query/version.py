"""Version string parser and generator."""

import collections.abc
import enum
import itertools
import logging
import re
import typing as t

import packaging.version
import pkg_resources
import semver

_LOG = logging.getLogger(__name__)


@enum.unique
class VersionComponent(enum.IntEnum):

    """Enumeration of standard version components."""

    Major = 1 << 1
    Minor = 1 << 2
    Patch = 1 << 3
    Release = Major | Minor | Patch
    PrePatch = 1 << 4
    DevPatch = 1 << 5
    Local = 1 << 6


def _version_tuple_checker(version_tuple, flags):
    return all([(_ is not None if flag else _ is None) for _, flag in zip(version_tuple, flags)])


class Version:

    """For storing and manipulating version information.

    Definitions of acceptable version formats are provided in readme.
    """

    _re_number = r'(?:0|[123456789][0123456789]*)'
    # _re_sha = r'[0123456789abcdef]+'
    _re_letters = r'(?:[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ]+)'
    _pattern_letters = re.compile(_re_letters)
    _re_alphanumeric = r'(?:[0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ]+)'
    _pattern_alphanumeric = re.compile(_re_alphanumeric)
    _re_sep = r'(?:[\.-])'

    _re_release_parts = r'(?P<major>{})(?:\.(?P<minor>{}))?(?:\.(?P<patch>{}))?'.format(
        _re_number, _re_number, _re_number)
    _pattern_release = re.compile(_re_release_parts)

    @classmethod
    def _parse_release_str(cls, release: str) -> tuple:
        match = cls._pattern_release.fullmatch(release)
        major = match.group('major')
        major = int(major)
        minor = match.group('minor')
        if minor is not None:
            minor = int(minor)
        patch = match.group('patch')
        if patch is not None:
            patch = int(patch)
        return major, minor, patch

    _re_pre_separator = r'(?P<preseparator>{})'.format(_re_sep)
    _re_pre_type = r'(?P<pretype>{})'.format(_re_letters)
    _re_pre_patch = r'(?P<prepatch>{})'.format(_re_number)
    _re_pre_release_part = r'{}?{}?{}?'.format(_re_pre_separator, _re_pre_type, _re_pre_patch)
    _pattern_pre_release_part = re.compile(_re_pre_release_part)
    _re_pre_release_parts = r'(?:{0}{2})|(?:{0}?{1}{2}?)'.format(_re_sep, _re_letters, _re_number)
    _pattern_pre_release = re.compile(_re_pre_release_parts)
    _pattern_pre_release_check = re.compile(r'(?:{})+'.format(_re_pre_release_parts))

    @classmethod
    def _parse_pre_release_str(cls, pre_release: str) -> tuple:
        # check_match = cls._pattern_pre_release_check.fullmatch(pre_release)
        # if check_match is None:
        #     raise ValueError('given pre-release string {} is invalid'.format(repr(pre_release)))
        parts = cls._pattern_pre_release.findall(pre_release)
        _LOG.debug('parsed pre-release string %s into %s',
                   repr(pre_release), parts)
        tuples = []
        for part in parts:
            match = cls._pattern_pre_release_part.fullmatch(part)
            pre_patch = match.group('prepatch')
            if pre_patch is not None:
                pre_patch = int(pre_patch)
            tuples.append((match.group('preseparator'), match.group('pretype'), pre_patch))
        return tuples

    _re_local_separator = r'({})'.format(_re_sep)
    _re_local_part = r'({})'.format(_re_alphanumeric)
    _re_local_parts = r'\+{}(?:{}{})*'.format(_re_local_part, _re_local_separator, _re_local_part)
    _pattern_local = re.compile(_re_local_parts)

    @classmethod
    def _parse_local_str(cls, local: str) -> tuple:
        match = cls._pattern_local.fullmatch(local)
        return tuple([_ for _ in match.groups() if _ is not None])

    _re_release = r'(?P<release>{0}(?:\.{0})?(?:\.{0})?)'.format(_re_number)
    _re_pre_release = r'(?P<prerelease>(?:(?:{0}{2})|(?:{0}?{1}{2}?))+)'.format(
        _re_sep, _re_letters, _re_number)
    _re_local = r'(?P<local>\+{0}([\.-]{0})*)'.format(_re_alphanumeric)
    # _re_named_parts_count = 3 + 3
    _re_version = r'{}{}?{}?'.format(_re_release, _re_pre_release, _re_local)
    _pattern_version = re.compile(_re_version)

    @classmethod
    def from_str(cls, version_str: str):
        """Create version from string."""
        py_version = pkg_resources.parse_version(version_str)  # type: packaging.version.Version
        _LOG.debug('packaging parsed version string %s into %s: %s',
                   repr(version_str), type(py_version), py_version)

        try:
            sem_version = semver.parse(version_str)  # type: dict
            _LOG.debug('semver parsed version string %s into %s: %s',
                       repr(version_str), type(sem_version), sem_version)
            sem_version_info = semver.parse_version_info(version_str)  # type: semver.VersionInfo
            _LOG.debug('semver parsed version string %s into %s: %s',
                       repr(version_str), type(sem_version_info), sem_version_info)
        except ValueError:
            _LOG.debug('semver could not parse version string %s', repr(version_str))

        match = cls._pattern_version.fullmatch(version_str)  # type: re.???
        if match is None:
            raise ValueError('version string {} is invalid'.format(repr(version_str)))
        _LOG.debug('version_query parsed version string %s into %s: %s %s',
                   repr(version_str), type(match), match.groupdict(), match.groups())

        _release = match.group('release')
        _pre_release = match.group('prerelease')
        _local = match.group('local')

        major, minor, patch = cls._parse_release_str(_release)
        pre_release = None if _pre_release is None else cls._parse_pre_release_str(_pre_release)
        local = None if _local is None else cls._parse_local_str(_local)

        return cls(major=major, minor=minor, patch=patch, pre_release=pre_release, local=local)

    @classmethod
    def from_tuple(cls, version_tuple: tuple):
        return cls(*version_tuple)

    @classmethod
    def from_dict(cls, version_dict: dict):
        return cls(**version_dict)

    @classmethod
    def from_py_version(cls, py_version: packaging.version.Version):
        """Create version from a standard Python version object."""
        if not isinstance(py_version, packaging.version.Version):
            _LOG.warning('attempting to parse %s as packaging.version.Version...', type(py_version))
        ver = py_version._version
        major, minor, patch = [ver.release[i] if len(ver.release) > i
                               else None for i in range(3)]
        pre_release = None
        local = None
        if len(ver.release) == 4:
            pre_ver = (None, ver.release[3])
        elif len(ver.release) > 4:
            raise NotImplementedError(ver)
        else:
            pre_ver = None
        pre_ver_present = sum(1 for _ in (ver.post, ver.dev, ver.pre) if _)
        if pre_ver and pre_ver_present:
            raise NotImplementedError(ver)
        if pre_ver_present > 1:
            raise NotImplementedError(ver)
        if ver.dev:
            pre_ver = ver.dev
        elif ver.pre:
            pre_ver = ver.pre
        if pre_ver:
            pre_release = [('.',) + tuple(pre_ver[i] if pre_ver and len(pre_ver) > i else None
                                          for i in range(2))]
        if ver.local:
            local = tuple(itertools.chain.from_iterable(
                (dot, str(_)) for dot, _ in zip('.' * len(ver.local), ver.local)))[1:]
        _LOG.debug('parsing %s %s', type(py_version), ver)
        return cls(major, minor, patch, pre_release=pre_release, local=local)

    @classmethod
    def from_sem_version(cls, sem_version: t.Union[dict, semver.VersionInfo]):
        """Create version from semantic version object."""
        _LOG.debug('parsing %s %s', type(sem_version), sem_version)
        if isinstance(sem_version, semver.VersionInfo):
            major, minor, patch = sem_version.major, sem_version.minor, sem_version.patch
            pre_release = sem_version.prerelease
            local = sem_version.build
        else:
            major, minor, patch = sem_version['major'], sem_version['minor'], sem_version['patch']
            pre_release = sem_version['prerelease']
            local = sem_version['build']
        if pre_release is not None:
            raise NotImplementedError(sem_version)
        if local is not None:
            local = cls._parse_local_str('+{}'.format(local))
        return cls(major, minor, patch, pre_release=pre_release, local=local)

    @classmethod
    def from_version(cls, version: 'Version'):
        return cls.from_dict(version.to_dict())

    def __init__(
            self, major: int, minor: t.Optional[int] = None, patch: t.Optional[int] = None, *args,
            pre_release: t.Sequence[
                t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]] = None,
            local: t.Union[str, tuple] = None):
        self._major = None
        self._minor = None
        self._patch = None
        self._pre_release = None
        self._local = None

        self.release = major, minor, patch

        if args and pre_release is not None and local is not None:
            raise ValueError('args={}, pre_release={} and local={} are all present in {}'
                             .format(args, pre_release, local, repr(self)))

        if pre_release is None:
            pre_release = []
            consumed_args = 0
            if len(args) > 0 and isinstance(args[0], tuple):
                for i, arg in enumerate(args):
                    if not isinstance(arg, tuple):
                        break
                    if len(arg) == 3 and arg[0] in (None, '.', '-'):
                        pre_release.append(arg)
                        consumed_args += 1
                        continue
                    if i == len(args) - 1:
                        break
                    raise ValueError('pre-release segment arg={} (index {} in args={} in {})'
                                     ' must be a 3-tuple'
                                     .format(arg, i, args, repr(self)))
            else:
                accumulated = []
                for i, arg in enumerate(args):
                    if len(accumulated) == 0:
                        if arg in (None, '.', '-'):
                            if len(args) < i + 3:
                                raise ValueError(
                                    'expected 3 consecutive values from index {} in args={} in {}'
                                    .format(i, args, repr(self)))
                        else:
                            break
                    accumulated.append(arg)
                    consumed_args += 1
                    if len(accumulated) == 3:
                        pre_release.append(tuple(accumulated))
                        accumulated = []
            if consumed_args > 0:
                args = args[consumed_args:]
            else:
                pre_release = None
        self.pre_release = pre_release

        if args and local is not None:
            raise ValueError('args={} and local={} are present at the same time in {}'
                             .format(args, local, repr(self)))

        if local is None:
            if len(args) == 1 and isinstance(args[0], tuple):
                local = args[0]
            elif not args:
                local = None
            else:
                local = args
        elif isinstance(local, str):
            local = (local,)
        self.local = local

    @property
    def release(self) -> t.Tuple[int, t.Optional[int], t.Optional[int]]:
        return self._major, self._minor, self._patch

    @release.setter
    def release(self, release: t.Tuple[int, t.Optional[int], t.Optional[int]]):
        # major: int, minor: t.Optional[int] = None, patch: t.Optional[int] = None):
        if not isinstance(release, tuple):
            raise TypeError('release={} is of wrong type {} in {}'
                            .format(repr(release), type(release), repr(self)))
        if len(release) != 3:
            raise ValueError('release={} has wrong length {} in {}'
                             .format(repr(release), len(release), repr(self)))

        major, minor, patch = release

        if not isinstance(major, int):
            raise TypeError('major={} is of wrong type {} in {}'
                            .format(repr(major), type(major), repr(self)))
        if major < 0:
            raise ValueError('major={} has wrong value in {}'.format(repr(major), repr(self)))
        if minor is not None and not isinstance(minor, int):
            raise TypeError('minor={} is of wrong type {} in {}'
                            .format(repr(minor), type(minor), repr(self)))
        if minor is not None and minor < 0:
            raise ValueError('minor={} has wrong value in {}'.format(repr(minor), repr(self)))
        if patch is not None and not isinstance(patch, int):
            raise TypeError('patch={} is of wrong type {} in {}'
                            .format(repr(patch), type(patch), repr(self)))
        if patch is not None and patch < 0:
            raise ValueError('patch={} has wrong value in {}'.format(repr(patch), repr(self)))
        if minor is None and patch is not None:
            raise ValueError(
                'patch={} is present but not minor in {}'
                .format(repr(patch), repr(self)))

        self._major = major
        self._minor = minor
        self._patch = patch

    @property
    def pre_release(self) -> t.Optional[
            t.List[t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]]]:
        if self._pre_release is None:
            return None
        return self._pre_release.copy()

    @pre_release.setter
    def pre_release(
            self, pre_release: t.Optional[
                t.List[t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]]]):
        if pre_release is None:
            self._pre_release = None
            return

        if not isinstance(pre_release, collections.abc.Sequence):
            raise TypeError('pre_release={} is of wrong type {} in {}'
                            .format(repr(pre_release), type(pre_release), repr(self)))
        if len(pre_release) == 0:
            raise ValueError('pre_release has no elements although it is set in {}'
                             .format(repr(self)))

        for pre in pre_release:
            if not isinstance(pre, tuple):
                raise TypeError('pre-release part {} is of wrong type {} in {}'
                                .format(repr(pre), type(pre), repr(self)))
            if len(pre) != 3:
                raise ValueError('pre-release part={} has wrong length {} in {}'
                                 .format(repr(pre), len(pre), repr(self)))
            pre_separator, pre_type, pre_patch = pre
            if pre_separator is not None and not isinstance(pre_separator, str):
                raise TypeError('pre_separator={} is of wrong type {} in {}'
                                .format(repr(pre_separator), type(pre_separator), repr(self)))
            if pre_separator is not None and pre_separator not in ('-', '.'):
                raise ValueError('pre_separator={} has wrong value in {}'
                                 .format(repr(pre_separator), repr(self)))
            if pre_type is not None and not isinstance(pre_type, str):
                raise TypeError('pre_type={} is of wrong type {} in {}'
                                .format(repr(pre_type), type(pre_type), repr(self)))
            if pre_type is not None and type(self)._pattern_letters.fullmatch(pre_type) is None:
                raise ValueError('pre_type={} has wrong value in {}'
                                 .format(repr(pre_type), repr(self)))
            if pre_patch is not None and not isinstance(pre_patch, int):
                raise TypeError('pre_patch={} is of wrong type {} in {}'
                                .format(repr(pre_patch), type(pre_patch), repr(self)))
            if pre_patch is not None and pre_patch < 0:
                raise ValueError('pre_patch={} has wrong value in {}'
                                 .format(repr(pre_patch), repr(self)))
            if pre_separator is None and pre_type is None and pre_patch is not None:
                raise ValueError(
                    'neither pre_separator nor pre_type is set but pre_patch={} is in {}'
                    .format(repr(pre_patch), repr(self)))
            if pre_separator is not None and pre_type is None and pre_patch is None:
                raise ValueError(
                    'pre_separator={} is present but neither pre_type nor pre_patch is in {}'
                    .format(repr(pre_separator), repr(self)))

        self._pre_release = pre_release

    @property
    def has_pre_release(self):
        return self._pre_release is not None

    @property
    def local(self) -> t.Optional[t.Sequence[str]]:
        return self._local

    @local.setter
    def local(self, local: t.Optional[t.Sequence[str]]):
        if local is None:
            self._local = None
            return

        if not isinstance(local, collections.abc.Sequence):
            raise TypeError('local={} is of wrong type {} in {}'
                            .format(repr(local), type(local), repr(self)))

        if len(local) % 2 != 1:
            raise ValueError('local={} has wrong length {} in {}'
                             .format(repr(local), len(local), repr(self)))

        for i, part in enumerate(local):
            if not isinstance(part, str):
                raise TypeError('local_part or local_separator {} is of wrong type {} in {}'
                                .format(repr(part), type(part), repr(self)))
            if i % 2 == 0 and type(self)._pattern_alphanumeric.fullmatch(part) is None:
                raise ValueError('local_part={} has wrong value in {}'
                                 .format(repr(part), repr(self)))
            if i % 2 == 1 and part not in ('-', '.'):
                raise ValueError('local_separator={} has wrong value in {}'
                                 .format(repr(part), repr(self)))

        self._local = tuple(local)

    @property
    def has_local(self):
        return self._local is not None

    def increment(self, component: VersionComponent, amount: int = 1) -> 'Version':
        """Increment a selected version component and return self."""
        if not isinstance(component, VersionComponent):
            raise TypeError('component={} is of wrong type {}'
                            .format(repr(component), type(component)))
        if not isinstance(amount, int):
            raise TypeError('amount={} is of wrong type {}'.format(repr(amount), type(amount)))
        if amount < 1:
            raise ValueError('amount={} has wrong value'.format(amount))

        if component in (VersionComponent.Major, VersionComponent.Minor, VersionComponent.Patch):

            if component in (VersionComponent.Major, VersionComponent.Minor):
                if component is VersionComponent.Major:
                    self._major += amount
                    if self._minor is not None:
                        self._minor = 0
                else:
                    if self._minor is None:
                        self._minor = amount
                    else:
                        self._minor += amount

                if self._patch is not None:
                    self._patch = 0

            else:
                if self._minor is None:
                    self._minor = 0
                if self._patch is None:
                    self._patch = amount
                else:
                    self._patch += amount

            self._pre_release = None
            self._local = None

        elif component is VersionComponent.PrePatch:
            if self._pre_release is None or self.pre_release_to_tuple(True)[0][1] != '':
                self._pre_release = [('-', None, amount)]
            else:
                pre_sep, pre_type, pre_patch = self._pre_release[0]
                assert isinstance(pre_patch, int), (type(pre_patch), pre_patch)
                pre_patch += amount
                self.pre_release = [(pre_sep, pre_type, pre_patch)]

        elif component is VersionComponent.DevPatch:
            if self._pre_release is None:
                self._pre_release = []
            if not self._pre_release or self.pre_release_to_tuple(True)[-1][1] != 'dev':
                self._pre_release.append(('.', 'dev', amount))
            else:
                pre_sep, pre_type, pre_patch = self._pre_release[-1]
                if pre_patch is None:
                    pre_patch = amount
                else:
                    pre_patch += amount
                self._pre_release[-1] = (pre_sep, pre_type, pre_patch)
        else:
            raise ValueError('incrementing component={} is not possible'.format(repr(component)))

        return self

    def devel_increment(self, new_commits: int = 1) -> 'Version':
        """Increment version depending on current version number and return self.

        If there's no dev patch, then increment release patch by one and increment dev patch
        by number of new commits.

        If there's a dev patch, then increment it by number of new commits."""

        if not self.has_pre_release or self.pre_release_to_tuple(True)[-1][1] != 'dev':
            self.increment(VersionComponent.Patch)
        self.increment(VersionComponent.DevPatch, new_commits)

        return self

    def release_to_str(self) -> str:
        """Get string representation of this version's release component."""
        version_tuple = self._major, self._minor, self._patch
        if _version_tuple_checker(version_tuple, (True, False, False)):
            return '.'.join(str(_) for _ in version_tuple[:1])
        elif _version_tuple_checker(version_tuple, (True, True, False)):
            return '.'.join(str(_) for _ in version_tuple[:2])
        elif _version_tuple_checker(version_tuple, (True, True, True)):
            return '.'.join(str(_) for _ in version_tuple[:3])
        raise ValueError('cannot generate valid version string from {}'.format(repr(self)))

    def _pre_release_segment_to_str(self, segment: int) -> str:
        version_tuple = self._pre_release[segment]
        if _version_tuple_checker(version_tuple, (True, True, False)):
            return '{}{}'.format(*version_tuple[:2])
        elif _version_tuple_checker(version_tuple, (True, False, True)):
            return '{}{}'.format(version_tuple[0], version_tuple[2])
        elif _version_tuple_checker(version_tuple, (True, True, True)):
            return '{}{}{}'.format(*version_tuple)
        raise ValueError('cannot generate valid version string from {}'.format(repr(self)))

    def pre_release_to_str(self) -> str:
        if self._pre_release is None:
            return ''
        return ''.join(self._pre_release_segment_to_str(i)
                       for i, _ in enumerate(self._pre_release))

    def local_to_str(self) -> str:
        if not self._local:
            return ''
        return '+{}'.format(''.join(self._local))

    def to_str(self) -> str:
        return '{}{}{}'.format(self.release_to_str(), self.pre_release_to_str(),
                               self.local_to_str())

    def release_to_tuple(self, sort: bool = False) -> tuple:
        return (0 if sort else None) if self._major is None else self._major, \
            (0 if sort else None) if self._minor is None else self._minor, \
            (0 if sort else None) if self._patch is None else self._patch

    def pre_release_segment_to_tuple(self, segment: int, sort: bool = False) -> tuple:
        pre_separator, pre_type, pre_patch = self._pre_release[segment]
        return (1 if pre_type is None else 0) if sort else pre_separator, \
            ('' if pre_type is None else pre_type.lower()) if sort else pre_type, \
            (0 if sort else None) if pre_patch is None else pre_patch

    def pre_release_to_tuple(self, sort: bool = False) -> tuple:
        """Create tuple from this version's pre-release component."""
        if self._pre_release is None:
            return ((1, '', 0),) if sort else ()
        parts = [self.pre_release_segment_to_tuple(i, sort)
                 for i, _ in enumerate(self._pre_release)]
        return tuple(parts) if sort else tuple(itertools.chain.from_iterable(parts))

    def local_to_tuple(self, sort: bool = False) -> tuple:
        if self._local is None:
            return ()
        return tuple(0 if _ in ('.', '-') else _.lower() for _ in self._local) \
            if sort else self._local

    def to_tuple(self, sort: bool = False) -> tuple:
        return self.release_to_tuple(sort) + self.pre_release_to_tuple(sort) \
            + self.local_to_tuple(sort)

    def to_dict(self) -> dict:
        return {field[1:]: value for field, value in vars(self).items()}

    def to_py_version(self) -> packaging.version.Version:
        return packaging.version.Version(self.to_str())

    def to_sem_version(self) -> dict:
        return semver.parse(self.to_str())

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, ', '.join(
            '{}: {}'.format(field[1:], repr(value)) for field, value in vars(self).items()))

    def __str__(self):
        return self.to_str()

    def __hash__(self):
        return hash(self.to_tuple(sort=True))

    def __eq__(self, other):
        return not self < other and not other < self

    def __ne__(self, other):
        return self < other or other < self

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return not self < other

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise TypeError('cannot compare {} and {}'.format(type(self), type(other)))

        self_release = self.release_to_tuple(True)
        other_release = other.release_to_tuple(True)
        if self_release != other_release:
            return self_release < other_release

        self_pre_release = self.pre_release_to_tuple(True)
        other_pre_release = other.pre_release_to_tuple(True)
        if self_pre_release != other_pre_release:
            for self_part, other_part in itertools.zip_longest(
                    self_pre_release, other_pre_release, fillvalue=(1, '', 0)):
                if self_part != other_part:
                    return self_part < other_part
            raise NotImplementedError(repr(self_pre_release) + ' != ' + repr(other_pre_release))

        self_local = self.local_to_tuple(True)
        other_local = other.local_to_tuple(True)
        if self_local != other_local:
            for self_part, other_part in zip(self_local, other_local):
                if self_part != other_part:
                    return self_part < other_part
            if len(self_local) != len(other_local):
                return len(self_local) < len(other_local)
            raise NotImplementedError(repr(self_local) + ' != ' + repr(other_local))

        return False

    def __le__(self, other):
        return not other < self
