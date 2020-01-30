"""Perform tests on and in synthetic git repositories."""

import logging
import pathlib
import platform
import tempfile
import unittest

import git

_LOG = logging.getLogger(__name__)

__updated__ = '2020-01-29'


class GitRepoTests(unittest.TestCase):

    """Provide several utility propertied and methods named repo_* and git_*."""

    repo = None  # type: git.Repo
    repo_path = None  # type: pathlib.Path

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo_path = pathlib.Path(self._tmpdir.name)
        self.assertTrue(self.repo_path.is_dir())
        self.repo = None
        self._repo_files = []

    def tearDown(self):
        for path in self._repo_files:
            if path.is_file():
                path.unlink()
        if self.repo is not None:
            self.assertIsInstance(self.repo, git.Repo)
            self.repo.close()
            self.repo = None
        if platform.system() != 'Windows':
            self._tmpdir.cleanup()
            self._tmpdir = None

    @property
    def repo_head_hexsha(self) -> str:
        return self.repo.head.commit.hexsha[:8]

    def git_init(self) -> git.Repo:
        """Initialize a git repository in the temporary folder."""
        self.repo = git.Repo.init(str(self.repo_path))
        self.assertIsInstance(self.repo, git.Repo)
        self.repo.git.config('user.email', 'you@example.com')
        self.repo.git.config('user.name', 'Your Name')
        return self.repo

    def git_clone(self, remote_name: str, url: str) -> git.Repo:
        """Clone a git repository into the temporary folder."""
        self.repo = git.Repo.clone_from(url, str(self.repo_path), origin=remote_name)
        self.assertIsInstance(self.repo, git.Repo)
        self.repo.git.config('user.email', 'you@example.com')
        self.repo.git.config('user.name', 'Your Name')
        return self.repo

    def git_commit_new_file(self) -> pathlib.Path:
        """Create a new file and commit it."""
        with tempfile.NamedTemporaryFile('w', dir=str(self.repo_path), delete=False) as repo_file:
            repo_file.write('spam spam lovely spam\n')
            path = pathlib.Path(repo_file.name)
        self.repo.index.add([path.name])
        self.repo.index.commit(f'created file {path}')
        _LOG.debug('commited file %s as %s', path, self.repo_head_hexsha)
        self._repo_files.append(path)
        return path

    def git_modify_file(self, path: pathlib.Path, add: bool = False, commit: bool = False) -> None:
        """Modify an existing file."""
        self.assertIsInstance(self.repo, git.Repo)
        self.assertIsInstance(path, pathlib.Path)
        self.assertTrue(path.is_file())
        with path.open('a') as repo_file:
            repo_file.write('spam eggs ham\n')
        if add or commit:
            self.repo.index.add([path.name])
        if commit:
            self.repo.index.commit(f'modified file {path}')


class GitRepoSelfTests(GitRepoTests):

    def test_typical(self):
        self.git_init()
        pth = self.git_commit_new_file()
        self.git_modify_file(pth)
        pth = self.git_commit_new_file()
        self.git_modify_file(pth, add=True)
        pth = self.git_commit_new_file()
        self.git_modify_file(pth, commit=True)

    def test_clone(self):
        path = pathlib.Path(__file__).resolve().parent.parent
        self.git_clone('origin', str(path))

    def test_no_repo(self):
        self.assertIsNone(self.repo)

    def test_cleanup_nonexisting(self):
        self.git_init()
        pth = self.git_commit_new_file()
        pth.unlink()
        self.assertFalse(pth.is_file())
