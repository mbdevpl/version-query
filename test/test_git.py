"""Tests of adversarial git repos."""

import itertools
import logging
import pathlib
import platform
import tempfile
import unittest

import git

from version_query.version import VersionComponent, Version
from version_query.git_query import query_git_repo, predict_git_repo

_LOG = logging.getLogger(__name__)


class Tests(unittest.TestCase):

    """Test suite for automated tests of generated git repositories.

    Each case is executed in a fresh empty repository.
    """

    repo = None  # type: git.Repo
    repo_path = None  # type: pathlib.Path

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo_path = pathlib.Path(self._tmpdir.name)
        self.assertTrue(self.repo_path.is_dir())
        self.repo = git.Repo.init(str(self.repo_path))
        self.assertIsInstance(self.repo, git.Repo)
        self._repo_files = []
        self.repo.git.config('user.email', 'you@example.com')
        self.repo.git.config('user.name', 'Your Name')

    def tearDown(self):
        for path in self._repo_files:
            if path.is_file():
                path.unlink()
        self.assertIsInstance(self.repo, git.Repo)
        self.repo.close()
        self.repo = None
        if platform.system() != 'Windows':
            self._tmpdir.cleanup()
            self._tmpdir = None

    @property
    def head_hexsha(self) -> str:
        return self.repo.head.commit.hexsha[:8]

    def _commit_new_file(self) -> pathlib.Path:
        self.assertIsInstance(self.repo, git.Repo)
        with tempfile.NamedTemporaryFile('w', dir=str(self.repo_path), delete=False) as repo_file:
            repo_file.write('spam spam lovely spam\n')
            path = pathlib.Path(repo_file.name)
        self.repo.index.add([path.name])
        self.repo.index.commit('created file {}'.format(path))
        _LOG.debug('commited file %s as %s', path, self.head_hexsha)
        self._repo_files.append(path)
        return path

    def _modify_file(self, path: pathlib.Path, add: bool = False, commit: bool = False) -> None:
        self.assertIsInstance(self.repo, git.Repo)
        self.assertIsInstance(path, pathlib.Path)
        self.assertTrue(path.is_file())
        with open(str(path), 'a') as repo_file:
            repo_file.write('spam eggs ham\n')
        if add or commit:
            self.repo.index.add([path.name])
        if commit:
            self.repo.index.commit('modified file {}'.format(path))

    def test_empty_repo(self):
        with self.assertRaises(ValueError):
            query_git_repo(self.repo_path)
        with self.assertRaises(ValueError):
            predict_git_repo(self.repo_path)

    def test_no_tags(self):
        for i in range(1, 5):
            self._commit_new_file()
            with self.assertRaises(ValueError):
                query_git_repo(self.repo_path)
            version = predict_git_repo(self.repo_path)
            self.assertEqual(version.to_str(), '0.1.0.dev{}+{}'.format(i, self.head_hexsha))

    def test_only_nonversion_tags(self):
        for i in range(1, 5):
            self._commit_new_file()
            self.repo.create_tag('commit_{}'.format(i))
            with self.assertRaises(ValueError):
                query_git_repo(self.repo_path)
            version = predict_git_repo(self.repo_path)
            self.assertEqual(version.to_str(), '0.1.0.dev{}+{}'.format(i, self.head_hexsha))

    def test_inconsistent_tag_prefix(self):
        version = Version.from_str('1.0')
        for _ in range(5):
            for version_tag_prefix in ('v', 'ver', ''):
                self._commit_new_file()
                version.increment(VersionComponent.Minor)
                self.repo.create_tag('{}{}'.format(version_tag_prefix, version))
                current_version = query_git_repo(self.repo_path)
                self.assertEqual(version, current_version)
                upcoming_version = predict_git_repo(self.repo_path)
                self.assertEqual(version, upcoming_version)

    def test_nonversion_tags(self):
        version = Version.from_str('0.1.0')
        self._commit_new_file()
        self.repo.create_tag('v{}'.format(version))
        path = self._commit_new_file()
        self._modify_file(path, commit=True)
        self.repo.create_tag('release1')
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(version, current_version)
        upcoming_version = predict_git_repo(self.repo_path)
        version.increment(VersionComponent.Patch, 1)
        version.increment(VersionComponent.DevPatch, 2)
        version.local = (self.head_hexsha,)
        self.assertEqual(version, upcoming_version)

    def test_too_long_no_tag(self):
        self._commit_new_file()
        self.repo.create_tag('v4.0.0')
        path = self._commit_new_file()
        for _ in range(1000):
            self._modify_file(path, commit=True)
        with self.assertRaises(ValueError):
            query_git_repo(self.repo_path)
        with self.assertRaises(ValueError):
            predict_git_repo(self.repo_path)

    def test_nonversion_merged_branches(self):
        self._commit_new_file()
        self._commit_new_file()
        self.repo.create_head('devel')
        self.repo.create_head('experimental')
        self._commit_new_file()
        self.repo.create_tag('trial')
        self.repo.git.checkout('experimental')
        self._commit_new_file()
        self.repo.git.checkout('devel')
        self._commit_new_file()
        self.repo.create_tag('error')
        self.repo.git.checkout('master')
        self.repo.git.merge('devel')
        self.repo.git.merge('experimental')
        self._commit_new_file()
        with self.assertRaises(ValueError):
            query_git_repo(self.repo_path)
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), '0.1.0.dev6+{}'.format(self.head_hexsha))

    def test_invalid_version_tags(self):
        for i in range(1, 3):
            self._commit_new_file()
            self.repo.create_tag('v{}.0.0'.format(i))
            self._commit_new_file()
            self.repo.create_tag('version_{}.0.0'.format(i + 1))

            current_version = query_git_repo(self.repo_path)
            self.assertEqual(current_version.to_str(), '{}.0.0'.format(i))
            upcoming_version = predict_git_repo(self.repo_path)
            current_version.devel_increment(1)
            current_version.local = (self.head_hexsha,)
            self.assertEqual(current_version, upcoming_version)

    def test_dirty_repo(self):
        version = Version.from_str('0.9.0')
        for new_commit, add in itertools.product((False, True), (False, True)):
            path = self._commit_new_file()
            self.repo.create_tag('v{}'.format(version))
            if new_commit:
                self._commit_new_file()
            self._modify_file(path, add=add)
            current_version = query_git_repo(self.repo_path)
            self.assertEqual(version, current_version)
            upcoming_version = predict_git_repo(self.repo_path)
            self.assertLess(version, upcoming_version)
            if new_commit:
                current_version.devel_increment(1)
                current_version.local = (self.head_hexsha,)
                self.assertTupleEqual(current_version.local, upcoming_version.local[:1])
                local_prefix = '+{}.dirty'.format(self.head_hexsha)
            else:
                local_prefix = '+dirty'
            self.assertTrue(upcoming_version.local_to_str().startswith(local_prefix),
                            msg=upcoming_version.local_to_str())
            self.assertLess(current_version, upcoming_version)
            version.increment(VersionComponent.Patch)
            self.assertLess(upcoming_version, version)

    def test_nonlatest_commit(self):
        self._commit_new_file()
        self.repo.create_tag('v0.1.0')
        self._commit_new_file()
        self.repo.create_head('devel')
        self.repo.git.checkout('devel')
        self._commit_new_file()
        self.repo.create_tag('v0.2.0')
        self._commit_new_file()
        self.repo.git.checkout('master')
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.1.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), '0.1.1.dev1+{}'.format(self.head_hexsha))
        self.repo.git.checkout('devel')
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.2.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), '0.2.1.dev1+{}'.format(self.head_hexsha))

    def test_tags_on_merged_branches(self):
        self._commit_new_file()
        self.repo.create_head('devel')
        self._commit_new_file()
        self.repo.create_tag('v0.2.0')
        self._commit_new_file()
        self._commit_new_file()
        self._commit_new_file()
        self.repo.git.checkout('devel')
        self._commit_new_file()
        self.repo.create_tag('v0.1.0')
        self._commit_new_file()
        self.repo.git.checkout('master')
        self.repo.git.merge('devel')
        self._commit_new_file()
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.2.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), '0.2.1.dev5+{}'.format(self.head_hexsha))

    def test_version_decreased(self):
        self._commit_new_file()
        self.repo.create_tag('v0.2.0')
        self._commit_new_file()
        self.repo.create_tag('v0.1.0')
        self._commit_new_file()
        hexsha = self.head_hexsha
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.1.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), '0.1.1.dev1+{}'.format(hexsha))
