"""Version string parser and generator."""

import collections.abc
import enum
import itertools
import logging
import re
import typing as t

import packaging.version
import semver

_LOG = logging.getLogger(__name__)

PY_PRE_RELEASE_INDICATORS = {'a', 'b', 'c', 'rc'}


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


class Version(collections.abc.Hashable):  # pylint: disable = too-many-public-methods
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

    _re_release_parts = \
        r'(?P<major>{n})(?:\.(?P<minor>{n}))?(?:\.(?P<patch>{n}))?'.format(n=_re_number)
    _pattern_release = re.compile(_re_release_parts)

    @classmethod
    def _parse_release_str(cls, release: str) -> tuple:
        match = cls._pattern_release.fullmatch(release)
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

    _re_pre_separator = rf'(?P<preseparator>{_re_sep})'
    _re_pre_type = rf'(?P<pretype>{_re_letters})'
    _re_pre_patch = rf'(?P<prepatch>{_re_number})'
    _re_pre_release_part = rf'{_re_pre_separator}?{_re_pre_type}?{_re_pre_patch}?'
    _pattern_pre_release_part = re.compile(_re_pre_release_part)
    _re_pre_release_parts = r'(?:{0}{2})|(?:{0}?{1}{2}?)'.format(_re_sep, _re_letters, _re_number)
    _pattern_pre_release = re.compile(_re_pre_release_parts)
    _pattern_pre_release_check = re.compile(rf'(?:{_re_pre_release_parts})+')

    @classmethod
    def _parse_pre_release_str(cls, pre_release: str) -> t.Sequence[
            t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]]:
        parts = cls._pattern_pre_release.findall(pre_release)
        _LOG.debug('parsed pre-release string %s into %s',
                   repr(pre_release), parts)
        tuples = []
        for part in parts:
            match = cls._pattern_pre_release_part.fullmatch(part)
            assert match is not None
            pre_patch_match = match.group('prepatch')
            if pre_patch_match is not None:
                pre_patch = int(pre_patch_match)
            else:
                pre_patch = None
            tuples.append((match.group('preseparator'), match.group('pretype'), pre_patch))
        return tuples

    _re_local_separator = rf'({_re_sep})'
    _re_local_part = rf'({_re_alphanumeric})'
    _re_local_parts = rf'\+{_re_local_part}(?:{_re_local_separator}{_re_local_part})*'
    _pattern_local = re.compile(_re_local_parts)

    @classmethod
    def _parse_local_str(cls, local: str) -> tuple:
        match = cls._pattern_local.fullmatch(local)
        assert match is not None
        return tuple([_ for _ in match.groups() if _ is not None])

    _re_release = r'(?P<release>{n}(?:\.{n})?(?:\.{n})?)'.format(n=_re_number)
    _re_pre_release = r'(?P<prerelease>(?:(?:{0}{2})|(?:{0}?{1}{2}?))+)'.format(
        _re_sep, _re_letters, _re_number)
    _re_local = r'(?P<local>\+{0}([\.-]{0})*)'.format(_re_alphanumeric)
    # _re_named_parts_count = 3 + 3
    _re_version = rf'{_re_release}{_re_pre_release}?{_re_local}?'
    _pattern_version = re.compile(_re_version)

    @classmethod
    def from_str(cls, version_str: str):
        """Create version from string."""
        match = cls._pattern_version.fullmatch(version_str)  # type: t.Optional[t.Match[str]]
        if match is None:
            raise ValueError(f'version string {repr(version_str)} is invalid')
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
        pre_release: t.Optional[t.Sequence[
            t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]]] = None
        local = None
        pre_ver: t.Optional[t.Tuple[None, int]]
        if len(ver.release) == 4:
            pre_ver = (None, ver.release[3])
        elif len(ver.release) > 4:
            raise NotImplementedError(py_version)
        else:
            pre_ver = None
        pre_ver_present = sum(1 for _ in (ver.post, ver.dev, ver.pre) if _)
        if pre_ver and pre_ver_present:
            raise NotImplementedError(py_version)
        if pre_ver_present > 1:
            raise NotImplementedError(py_version)
        if ver.dev:
            pre_ver = ver.dev
        elif ver.pre:
            pre_ver = ver.pre
        if pre_ver:
            prefix_dot = None if pre_ver[0] in PY_PRE_RELEASE_INDICATORS else '.'
            pre_release = [(prefix_dot, pre_ver[0], pre_ver[1] if len(pre_ver) > 1 else None)]
        if ver.local:
            local = tuple(itertools.chain.from_iterable(
                (dot, str(_)) for dot, _ in zip('.' * len(ver.local), ver.local)))[1:]
        _LOG.debug('parsing %s %s', type(py_version), py_version)
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
            local = cls._parse_local_str(f'+{local}')
        return cls(major, minor, patch, pre_release=pre_release, local=local)

    @classmethod
    def from_version(cls, version: 'Version'):
        return cls.from_dict(version.to_dict())

    def __init__(
            self, major: int, minor: t.Optional[int] = None, patch: t.Optional[int] = None, *args,
            pre_release: t.Sequence[
                t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]] = None,
            local: t.Union[str, tuple] = None):
        self._major: t.Optional[int] = None
        self._minor: t.Optional[int] = None
        self._patch: t.Optional[int] = None
        self._pre_release: t.Optional[
            t.List[t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]]] = None
        self._local: t.Optional[t.Sequence[str]] = None

        self.release = major, minor, patch

        if args and pre_release is not None and local is not None:
            raise ValueError(f'args={args}, pre_release={pre_release} and local={local}'
                             f' are all present in {repr(self)}')

        if pre_release is None:
            pre_release, consumed_args = self._get_pre_release_from_args(args)
            if consumed_args > 0:
                args = args[consumed_args:]
            else:
                pre_release = None
        self.pre_release = pre_release

        if args and local is not None:
            raise ValueError(f'args={args} and local={local} are present at the same time'
                             f' in {repr(self)}')

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

    def _get_pre_release_from_args(self, args) -> t.Tuple[
            t.Sequence[t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]], int]:
        pre_release: t.List[t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]] = []
        consumed_args = 0
        if args and isinstance(args[0], tuple):
            for i, arg in enumerate(args):
                if not isinstance(arg, tuple):
                    break
                if len(arg) == 3 and arg[0] in (None, '.', '-'):
                    pre_release.append(arg)
                    consumed_args += 1
                    continue
                if i == len(args) - 1:
                    break
                raise ValueError(f'pre-release segment arg={arg} (index {i} in args={args}'
                                 f' in {repr(self)}) must be a 3-tuple')
        else:
            accumulated: t.List[t.Union[int, str]] = []
            for i, arg in enumerate(args):
                if not accumulated:
                    if arg in (None, '.', '-'):
                        if len(args) < i + 3:
                            raise ValueError(f'expected 3 consecutive values from index {i}'
                                             f' in args={args} in {repr(self)}')
                    else:
                        break
                accumulated.append(arg)
                consumed_args += 1
                if len(accumulated) == 3:
                    pre_release.append(tuple(accumulated))
                    accumulated = []
        return pre_release, consumed_args

    @property
    def release(self) -> t.Tuple[int, t.Optional[int], t.Optional[int]]:
        assert self._major is not None
        return self._major, self._minor, self._patch

    @release.setter
    def release(self, release: t.Tuple[int, t.Optional[int], t.Optional[int]]):
        # major: int, minor: t.Optional[int] = None, patch: t.Optional[int] = None):
        if not isinstance(release, tuple):
            raise TypeError(
                f'release={repr(release)} is of wrong type {type(release)} in {repr(self)}')
        if len(release) != 3:
            raise ValueError(
                f'release={repr(release)} has wrong length {len(release)} in {repr(self)}')

        major, minor, patch = release

        if not isinstance(major, int):
            raise TypeError(f'major={repr(major)} is of wrong type {type(major)} in {repr(self)}')
        if major < 0:
            raise ValueError(f'major={repr(major)} has wrong value in {repr(self)}')
        if minor is not None and not isinstance(minor, int):
            raise TypeError(f'minor={repr(minor)} is of wrong type {type(minor)} in {repr(self)}')
        if minor is not None and minor < 0:
            raise ValueError(f'minor={repr(minor)} has wrong value in {repr(self)}')
        if patch is not None and not isinstance(patch, int):
            raise TypeError(f'patch={repr(patch)} is of wrong type {type(patch)} in {repr(self)}')
        if patch is not None and patch < 0:
            raise ValueError(f'patch={repr(patch)} has wrong value in {repr(self)}')
        if minor is None and patch is not None:
            raise ValueError(f'patch={repr(patch)} is present but not minor in {repr(self)}')

        self._major = major
        self._minor = minor
        self._patch = patch

    @property
    def pre_release(self) -> t.Optional[
            t.Sequence[t.Tuple[t.Optional[str], t.Optional[str], t.Optional[int]]]]:
        """Pre-release version component."""
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
            raise TypeError(f'pre_release={repr(pre_release)} is of wrong type {type(pre_release)}'
                            f' in {repr(self)}')
        if len(pre_release) == 0:
            raise ValueError(f'pre_release has no elements although it is set in {repr(self)}')

        for pre in pre_release:
            if not isinstance(pre, tuple):
                raise TypeError(
                    f'pre-release part {repr(pre)} is of wrong type {type(pre)} in {repr(self)}')
            if len(pre) != 3:
                raise ValueError(
                    f'pre-release part={repr(pre)} has wrong length {len(pre)} in {repr(self)}')
            pre_separator, pre_type, pre_patch = pre
            self._check_pre_release_parts(pre_separator, pre_type, pre_patch)

        self._pre_release = pre_release

    def _check_pre_release_parts(self, pre_separator, pre_type, pre_patch):
        """Verify that the given pre-release version identifier parts are valid."""
        if pre_separator is not None and not isinstance(pre_separator, str):
            raise TypeError(f'pre_separator={repr(pre_separator)} is of wrong type'
                            f' {type(pre_separator)} in {repr(self)}')
        if pre_separator is not None and pre_separator not in ('-', '.'):
            raise ValueError(f'pre_separator={repr(pre_separator)} has wrong value in {repr(self)}')
        if pre_type is not None and not isinstance(pre_type, str):
            raise TypeError(
                f'pre_type={repr(pre_type)} is of wrong type {type(pre_type)} in {repr(self)}')
        if pre_type is not None and type(self)._pattern_letters.fullmatch(pre_type) is None:
            raise ValueError(f'pre_type={repr(pre_type)} has wrong value in {repr(self)}')
        if pre_patch is not None and not isinstance(pre_patch, int):
            raise TypeError(
                f'pre_patch={repr(pre_patch)} is of wrong type {type(pre_patch)} in {repr(self)}')
        if pre_patch is not None and pre_patch < 0:
            raise ValueError(f'pre_patch={repr(pre_patch)} has wrong value in {repr(self)}')
        if pre_separator is None and pre_type is None and pre_patch is not None:
            raise ValueError(f'neither pre_separator nor pre_type is set'
                             f' but pre_patch={repr(pre_patch)} is in {repr(self)}')
        if pre_separator is not None and pre_type is None and pre_patch is None:
            raise ValueError(f'pre_separator={repr(pre_separator)} is present'
                             f' but neither pre_type nor pre_patch is in {repr(self)}')

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
            raise TypeError(f'local={repr(local)} is of wrong type {type(local)} in {repr(self)}')

        if len(local) % 2 != 1:
            raise ValueError(f'local={repr(local)} has wrong length {len(local)} in {repr(self)}')

        for i, part in enumerate(local):
            if not isinstance(part, str):
                raise TypeError(f'local_part or local_separator {repr(part)} is of wrong type'
                                f' {type(part)} in {repr(self)}')
            if i % 2 == 0:
                if type(self)._pattern_alphanumeric.fullmatch(part) is None:
                    raise ValueError(f'local_part={repr(part)} has wrong value in {repr(self)}')
            elif part not in ('-', '.'):
                raise ValueError(f'local_separator={repr(part)} has wrong value in {repr(self)}')

        self._local = tuple(local)

    @property
    def has_local(self):
        return self._local is not None

    def increment(self, component: VersionComponent, amount: int = 1) -> 'Version':
        """Increment a selected version component and return self."""
        if not isinstance(component, VersionComponent):
            raise TypeError(f'component={repr(component)} is of wrong type {type(component)}')
        if not isinstance(amount, int):
            raise TypeError(f'amount={repr(amount)} is of wrong type {type(amount)}')
        if amount < 1:
            raise ValueError(f'amount={amount} has wrong value')

        if component in (VersionComponent.Major, VersionComponent.Minor, VersionComponent.Patch):
            self._increment_release(component, amount)

        elif component is VersionComponent.PrePatch:
            self._increment_pre_path(amount)

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
            raise ValueError(f'incrementing component={repr(component)} is not possible')

        return self

    def _increment_release(self, component: VersionComponent, amount: int):
        if component in (VersionComponent.Major, VersionComponent.Minor):
            if component is VersionComponent.Major:
                assert self._major is not None
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

    def _increment_pre_path(self, amount):
        if self._pre_release is None or self.pre_release_to_tuple(True)[0][1] != '':
            self._pre_release = [('-', None, amount)]
        else:
            pre_sep, pre_type, pre_patch = self._pre_release[0]
            assert isinstance(pre_patch, int), (type(pre_patch), pre_patch)
            pre_patch += amount
            self.pre_release = [(pre_sep, pre_type, pre_patch)]

    def devel_increment(self, new_commits: int = 1) -> 'Version':
        """Increment version depending on current version number and return self.

        If there's no dev patch, then increment release patch by one and increment dev patch
        by number of new commits.

        If there's a dev patch, then increment it by number of new commits.
        """
        if not self.has_pre_release or self.pre_release_to_tuple(True)[-1][1] != 'dev':
            self.increment(VersionComponent.Patch)
        self.increment(VersionComponent.DevPatch, new_commits)

        return self

    def release_to_str(self) -> str:
        """Get string representation of this version's release component."""
        version_tuple = self._major, self._minor, self._patch
        if _version_tuple_checker(version_tuple, (True, False, False)):
            return '.'.join(str(_) for _ in version_tuple[:1])
        if _version_tuple_checker(version_tuple, (True, True, False)):
            return '.'.join(str(_) for _ in version_tuple[:2])
        if _version_tuple_checker(version_tuple, (True, True, True)):
            return '.'.join(str(_) for _ in version_tuple[:3])
        raise ValueError(f'cannot generate valid version string from {repr(self)}')

    def _pre_release_segment_to_str(self, segment: int) -> str:
        assert self._pre_release is not None
        version_tuple = self._pre_release[segment]
        if _version_tuple_checker(version_tuple, (True, True, False)):
            return '{}{}'.format(*version_tuple[:2])
        if _version_tuple_checker(version_tuple, (True, False, True)):
            return f'{version_tuple[0]}{version_tuple[2]}'
        if _version_tuple_checker(version_tuple, (False, True, True)):
            return '{}{}'.format(*version_tuple[1:])
        if _version_tuple_checker(version_tuple, (True, True, True)):
            return '{}{}{}'.format(*version_tuple)
        raise ValueError(f'cannot generate valid version string from {repr(self)}')

    def pre_release_to_str(self) -> str:
        if self._pre_release is None:
            return ''
        return ''.join(self._pre_release_segment_to_str(i)
                       for i, _ in enumerate(self._pre_release))

    def local_to_str(self) -> str:
        if not self._local:
            return ''
        return f'+{"".join(self._local)}'

    def to_str(self) -> str:
        return f'{self.release_to_str()}{self.pre_release_to_str()}{self.local_to_str()}'

    def release_to_tuple(self, sort: bool = False) -> tuple:
        return (0 if sort else None) if self._major is None else self._major, \
            (0 if sort else None) if self._minor is None else self._minor, \
            (0 if sort else None) if self._patch is None else self._patch

    def pre_release_segment_to_tuple(self, segment: int, sort: bool = False) -> tuple:
        assert self._pre_release is not None
        pre_separator, pre_type, pre_patch = self._pre_release[segment]
        return (1 if pre_type is None else 0) if sort else pre_separator, \
            ('' if pre_type is None else pre_type.lower()) if sort else pre_type, \
            (0 if sort else None) if pre_patch is None else pre_patch

    def pre_release_to_tuple(self, sort: bool = False) -> tuple:
        """Create tuple from this version's pre-release component."""
        if self._pre_release is None:
            if sort:
                return ((1, '', 0),)
            return ()
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

    def to_sem_version(self) -> semver.VersionInfo:
        return semver.VersionInfo.parse(self.to_str())

    def __repr__(self):
        fields = ', '.join(f'{field[1:]}: {repr(value)}' for field, value in vars(self).items())
        return f'{type(self).__name__}({fields})'

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
            raise TypeError(f'cannot compare {type(self)} and {type(other)}')

        self_release = self.release_to_tuple(True)
        other_release = other.release_to_tuple(True)
        if self_release != other_release:
            return self_release < other_release

        self_pre_release = self.pre_release_to_tuple(True)
        other_pre_release = other.pre_release_to_tuple(True)
        for self_part, other_part in itertools.zip_longest(
                self_pre_release, other_pre_release, fillvalue=(1, '', 0)):
            if self_part != other_part:
                return self_part < other_part

        self_local = self.local_to_tuple(True)
        other_local = other.local_to_tuple(True)
        for self_part, other_part in zip(self_local, other_local):
            if self_part != other_part:
                return self_part < other_part
        if len(self_local) != len(other_local):
            return len(self_local) < len(other_local)

        return False

    def __le__(self, other):
        return not other < self
