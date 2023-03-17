"""Tests of adversarial git repos."""

import itertools
import logging
# import unittest

# import git

from version_query.version import VersionComponent, Version
from version_query.git_query import query_git_repo, predict_git_repo
from .test_with_git_repo import GitRepoTests

_LOG = logging.getLogger(__name__)


class Tests(GitRepoTests):
    """Test suite for automated tests of generated git repositories.

    Each case is executed in a fresh empty repository.
    """

    def setUp(self):
        super().setUp()
        self.git_init()

    def test_empty_repo(self):
        with self.assertRaises(ValueError):
            query_git_repo(self.repo_path)
        with self.assertRaises(ValueError):
            predict_git_repo(self.repo_path)

    def test_no_tags(self):
        for i in range(1, 5):
            self.git_commit_new_file()
            with self.assertRaises(ValueError):
                query_git_repo(self.repo_path)
            version = predict_git_repo(self.repo_path)
            self.assertEqual(version.to_str(), f'0.1.0.dev{i}+git{self.repo_head_hexsha}')

    def test_only_nonversion_tags(self):
        for i in range(1, 5):
            self.git_commit_new_file()
            self.repo.create_tag(f'commit_{i}')
            with self.assertRaises(ValueError):
                query_git_repo(self.repo_path)
            version = predict_git_repo(self.repo_path)
            self.assertEqual(version.to_str(), f'0.1.0.dev{i}+git{self.repo_head_hexsha}')

    def test_inconsistent_tag_prefix(self):
        version = Version.from_str('1.0')
        for _ in range(5):
            for version_tag_prefix in ('v', 'ver', ''):
                self.git_commit_new_file()
                version.increment(VersionComponent.Minor)
                self.repo.create_tag(f'{version_tag_prefix}{version}')
                current_version = query_git_repo(self.repo_path)
                self.assertEqual(version, current_version)
                upcoming_version = predict_git_repo(self.repo_path)
                self.assertEqual(version, upcoming_version)

    def test_nonversion_tags(self):
        version = Version.from_str('0.1.0')
        self.git_commit_new_file()
        self.repo.create_tag(f'v{version}')
        path = self.git_commit_new_file()
        self.git_modify_file(path, commit=True)
        self.repo.create_tag('release1')
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(version, current_version)
        upcoming_version = predict_git_repo(self.repo_path)
        version.increment(VersionComponent.Patch, 1)
        version.increment(VersionComponent.DevPatch, 2)
        version.local = (f'git{self.repo_head_hexsha}',)
        self.assertEqual(version, upcoming_version)

    def test_too_long_no_tag(self):
        self.git_commit_new_file()
        self.repo.create_tag('v4.0.0')
        path = self.git_commit_new_file()
        for _ in range(1000):
            self.git_modify_file(path, commit=True)
        with self.assertRaises(ValueError):
            query_git_repo(self.repo_path)
        with self.assertRaises(ValueError):
            predict_git_repo(self.repo_path)

    def test_nonversion_merged_branches(self):
        self.git_commit_new_file()
        self.git_commit_new_file()
        self.repo.create_head('devel')
        self.repo.create_head('experimental')
        self.git_commit_new_file()
        self.repo.create_tag('trial')
        self.repo.git.checkout('experimental')
        self.git_commit_new_file()
        self.repo.git.checkout('devel')
        self.git_commit_new_file()
        self.repo.create_tag('error')
        self.repo.git.checkout('master')
        self.repo.git.merge('devel')
        self.repo.git.merge('experimental')
        self.git_commit_new_file()
        with self.assertRaises(ValueError):
            query_git_repo(self.repo_path)
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), f'0.1.0.dev6+git{self.repo_head_hexsha}')

    def test_invalid_version_tags(self):
        for i in range(1, 3):
            self.git_commit_new_file()
            self.repo.create_tag(f'v{i}.0.0')
            self.git_commit_new_file()
            self.repo.create_tag(f'version_{i + 1}.0.0')

            current_version = query_git_repo(self.repo_path)
            self.assertEqual(current_version.to_str(), f'{i}.0.0')
            upcoming_version = predict_git_repo(self.repo_path)
            current_version.devel_increment(1)
            current_version.local = (f'git{self.repo_head_hexsha}',)
            self.assertEqual(current_version, upcoming_version)

    def test_dirty_repo(self):
        version = Version.from_str('0.9.0')
        for new_commit, add in itertools.product((False, True), (False, True)):
            path = self.git_commit_new_file()
            self.repo.create_tag(f'v{version}')
            if new_commit:
                self.git_commit_new_file()
            self.git_modify_file(path, add=add)
            current_version = query_git_repo(self.repo_path)
            self.assertEqual(version, current_version)
            upcoming_version = predict_git_repo(self.repo_path)
            self.assertLess(version, upcoming_version)
            if new_commit:
                current_version.devel_increment(1)
                current_version.local = (f'git{self.repo_head_hexsha}',)
                self.assertTupleEqual(current_version.local, upcoming_version.local[:1])
                local_prefix = f'+git{self.repo_head_hexsha}.dirty'
            else:
                local_prefix = '+dirty'
            self.assertTrue(upcoming_version.local_to_str().startswith(local_prefix),
                            msg=upcoming_version.local_to_str())
            self.assertLess(current_version, upcoming_version)
            version.increment(VersionComponent.Patch)
            self.assertLess(upcoming_version, version)

    def test_nonlatest_commit(self):
        self.git_commit_new_file()
        self.repo.create_tag('v0.1.0')
        self.git_commit_new_file()
        self.repo.create_head('devel')
        self.repo.git.checkout('devel')
        self.git_commit_new_file()
        self.repo.create_tag('v0.2.0')
        self.git_commit_new_file()
        self.repo.git.checkout('master')
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.1.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), f'0.1.1.dev1+git{self.repo_head_hexsha}')
        self.repo.git.checkout('devel')
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.2.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), f'0.2.1.dev1+git{self.repo_head_hexsha}')

    def test_tags_on_merged_branches(self):
        self.git_commit_new_file()
        self.repo.create_head('devel')
        self.git_commit_new_file()
        self.repo.create_tag('v0.2.0')
        self.git_commit_new_file()
        self.git_commit_new_file()
        self.git_commit_new_file()
        self.repo.git.checkout('devel')
        self.git_commit_new_file()
        self.repo.create_tag('v0.1.0')
        self.git_commit_new_file()
        self.repo.git.checkout('master')
        self.repo.git.merge('devel')
        self.git_commit_new_file()
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.2.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), f'0.2.1.dev5+git{self.repo_head_hexsha}')

    def test_tag_on_merged_branch(self):
        self.git_commit_new_file()
        self.repo.create_head('devel')
        self.git_commit_new_file()
        self.repo.git.checkout('devel')
        self.git_commit_new_file()
        self.repo.create_tag('v1.0.0')
        self.repo.git.checkout('master')
        self.repo.git.merge('devel')
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '1.0.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), f'1.0.1.dev1+git{self.repo_head_hexsha}')

    def test_many_versions_on_one_commit(self):
        self.git_commit_new_file()
        self.repo.create_tag('v0.1.0')
        self.repo.create_tag('v0.3.0')
        self.repo.create_tag('v0.2.0')
        self.git_commit_new_file()
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.3.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), f'0.3.1.dev1+git{self.repo_head_hexsha}')

    def test_version_decreased(self):
        self.git_commit_new_file()
        self.repo.create_tag('v0.2.0')
        self.git_commit_new_file()
        self.repo.create_tag('v0.1.0')
        self.git_commit_new_file()
        current_version = query_git_repo(self.repo_path)
        self.assertEqual(current_version.to_str(), '0.1.0')
        upcoming_version = predict_git_repo(self.repo_path)
        self.assertEqual(upcoming_version.to_str(), f'0.1.1.dev1+git{self.repo_head_hexsha}')
