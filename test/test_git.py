"""Tests of adversarial git repos."""

import logging
import pathlib
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

    def tearDown(self):
        for path in self._repo_files:
            path.unlink()
        self.assertIsInstance(self.repo, git.Repo)
        self.repo.close()
        self._tmpdir.cleanup()
        self._tmpdir = None

    def _commit_new_file(self) -> pathlib.Path:
        self.assertIsInstance(self.repo, git.Repo)
        with tempfile.NamedTemporaryFile('w', dir=str(self.repo_path), delete=False) as repo_file:
            repo_file.write('spam spam lovely spam\n')
            path = pathlib.Path(repo_file.name)
        # _LOG.warning('adding path %s', path)
        self.repo.index.add([path.name])
        self.repo.index.commit('created file {}'.format(path))
        self._repo_files.append(path)
        return path

    def _modify_file(self, repo: git.Repo, path: pathlib.Path,
                     add: bool = False, commit: bool = False) -> None:
        self.assertIsInstance(repo, git.Repo)
        self.assertIsInstance(path, pathlib.Path)
        self.assertTrue(path.is_file())
        with open(str(path), 'a') as repo_file:
            repo_file.write('spam eggs ham\n')
        if add or commit:
            repo.index.add([path.name])
        if commit:
            repo.index.commit('modified file {}'.format(path))

    def test_empty_repo(self):
        with self.assertRaises(ValueError):
            query_git_repo(self.repo_path)
        with self.assertRaises(ValueError):
            predict_git_repo(self.repo_path)

    def test_no_tags(self):
        for i in range(5):
            self._commit_new_file()
            with self.assertRaises(ValueError):
                query_git_repo(self.repo_path)
            version = predict_git_repo(self.repo_path)
            self.assertEqual(version.to_str(),
                             '0.1.0.dev{}+{}'.format(i, self.repo.head.commit.hexsha[:8]))

    def test_only_nonversion_tags(self):
        for i in range(5):
            self._commit_new_file()
            self.repo.create_tag('commit_{}'.format(i))
            with self.assertRaises(ValueError):
                query_git_repo(self.repo_path)
            version = predict_git_repo(self.repo_path)
            self.assertEqual(version.to_str(),
                             '0.1.0.dev{}+{}'.format(i, self.repo.head.commit.hexsha[:8]))

    def test_inconsistent_tag_prefix(self):
        version = Version.from_str('1.0')
        for _ in range(5):
            for version_tag_prefix in ('v', 'ver'):
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
        self._commit_new_file()
        self._commit_new_file()
        self.repo.create_tag('release1')
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(version, current_version)
        upcoming_version = predict_git_repo(self.repo_path)
        version.increment(VersionComponent.Patch, 1)
        version.increment(VersionComponent.DevPatch, 2)
        version.local = (self.repo.head.commit.hexsha[:8],)
        self.assertEqual(version, upcoming_version)

    @unittest.skip('legacy')
    def test_generated_git_repo(self):
        version_tag_prefix = 'v'
        repo = self.repo
        repo_path = self.repo_path
        repo_file_path = self._commit_new_file()

        with self.assertRaises(ValueError):
            query_git_repo(repo_path)
        upcoming_version = predict_git_repo(repo_path)
        self.assertEqual(upcoming_version, Version.from_str('0.1.0.dev0'))

        repo.create_tag('{}1.0.0'.format(version_tag_prefix))

        version = query_git_repo(repo_path)
        upcoming_version = predict_git_repo(repo_path)
        self.assertEqual(version, Version.from_str('1.0.0'))
        self.assertEqual(version, upcoming_version)

        self._modify_file(repo, repo_file_path, commit=True)

        version = query_git_repo(repo_path)
        self.assertEqual(version, Version.from_str('1.0.0'))
        upcoming_version = predict_git_repo(repo_path)
        self.assertGreater(upcoming_version, Version.from_str('1.0.1.dev1'))
        upcoming_version_str = str(upcoming_version)
        self.assertTrue(upcoming_version_str.startswith('1.0.1.dev1+'))

        self._modify_file(repo, repo_file_path)

        version = query_git_repo(repo_path)
        self.assertEqual(version, Version.from_str('1.0.0'))
        upcoming_version = predict_git_repo(repo_path)
        self.assertGreater(upcoming_version, Version.from_str('1.0.1.dev1'))
        upcoming_version_str = str(upcoming_version)
        self.assertTrue(upcoming_version_str.startswith('1.0.1.dev1+'))
        self.assertIn('.dirty', upcoming_version_str)

        repo.create_tag('milestone15')
        repo.create_tag('wide_char_support')

        version = query_git_repo(repo_path)
        self.assertEqual(version, Version.from_str('1.0.0'))

        repo.create_tag('version_1.1.0')

        version = query_git_repo(repo_path)
        self.assertEqual(version, Version.from_str('1.0.0'))
        new_upcoming_version = predict_git_repo(repo_path)
        self.assertEqual(new_upcoming_version.release, upcoming_version.release)
        self.assertEqual(new_upcoming_version.pre_release, upcoming_version.pre_release)

        repo.create_tag('{}1.1.0'.format(version_tag_prefix))

        version = query_git_repo(repo_path)
        self.assertEqual(version, Version.from_str('1.1.0'))
        upcoming_version = predict_git_repo(repo_path)
        self.assertGreater(upcoming_version, Version.from_str('1.1.0'))
        upcoming_version_str = str(upcoming_version)
        self.assertTrue(upcoming_version_str.startswith('1.1.0+dirty'),
                        upcoming_version_str)

    def test_nonlatest_commit(self):
        pass
