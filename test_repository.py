#!/usr/bin/env python3
"""Unit test module for repository.py"""

import contextlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from GitSvnHack.repository import Repo, SvnBranch, SvnRepo, \
    GitRepo, GitSvnRepo

# Could do something sophisticated or elegant, but easiest to just
# wrap Subversion's CLI.

# For Python 3.2, need to add some things that are already in 3.3:
if sys.version_info[0:1] < (3,3):
    subprocess.DEVNULL = os.open(os.devnull,os.O_WRONLY)
    FileNotFoundError = OSError


class TempFile:
    """Context manager class for files that exist only for one test, and
    must be deleted afterward."""

    def __init__(self):
        pass

    def __del__(self):
        """Try to delete the file if we forgot along the way."""
        self.delete()

    @property
    def path(self):
        """Path to the file."""
        return self._path

    def open(self, *args):
        """Open the file, passing all arguments to os.fdopen() and
        returning the result."""
        return os.fdopen(self._fd, *args)

    def __enter__(self):
        """Create a file."""
        self._fd,self._path = tempfile.mkstemp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Delete the file we created."""
        self.delete()
        return False

    def delete(self):
        """Delete the file."""
        # If the file was already deleted, don't worry about it; ignore the
        # exception.
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


class TestStaticRepo(unittest.TestCase):
    """Tests for the "Repo" class that don't change an external repository.

    For these tests, we can use the class versions of the setUp and
    tearDown methods to set up a test repository. Of course this only
    matters for subclasses.

    """

    repo_class = Repo
    repo_name = "test_repo"
    repo_path = "/path/to/fake"

    @classmethod
    def setUpClass(cls, **args):
        args.setdefault("name",cls.repo_name)
        args.setdefault("path",cls.repo_path)
        cls.my_repo = cls.repo_class(**args)

    @classmethod
    def tearDownClass(cls, **args):
        """Exists only to be called with super()."""
        pass

    def test_name(self):
        """Test that Repo objects retain names from __init__."""
        self.assertEqual(self.my_repo.name, self.repo_name)

    def test_path(self):
        """Test that Repo objects retain paths from __init__."""
        self.assertEqual(self.my_repo.path, self.repo_path)

class TestRepo(unittest.TestCase):
    """Test the "Repo" class."""

    repo_class = Repo
    repo_name = "test_repo"
    repo_path = "/path/to/fake"

    def setUp(self, **args):
        args.setdefault("name",self.repo_name)
        args.setdefault("path",self.repo_path)
        self.my_repo = self.repo_class(**args)

    def tearDown(self, **args):
        """Exists only to be called with super()."""
        pass


class TestSvnBranch(unittest.TestCase):
    """Test the "SvnBranch" class."""

    branch_class = SvnBranch
    head_path = "trunk"
    tag_expr = "trunk_tags/*"

    def setUp(self):
        self.my_branch = self.branch_class(self.head_path,
                                           self.tag_expr)

    def test_head(self):
        """Test that branch objects retain path to HEAD."""
        self.assertEqual(self.my_branch.head, self.head_path)

    def test_tag_expr(self):
        """Test that branch objects retain tag path expression."""
        self.assertEqual(self.my_branch.tags, self.tag_expr)


# This is used for manipulating paths in some tests below.
def get_path_start(string):
    """Returns everything before the first "/" in as string."""
    idx = string.find("/")
    # Return the string up to the index, or the whole string if
    # there was no "/" (idx < 0).
    if idx >= 0:
        return string[:idx]
    else:
        return string


class TestStaticSvnRepo(TestStaticRepo):
    """Static tests for the "SvnRepo" class.

    All the tests that don't change a repo are here.

    """

    repo_class = SvnRepo
    trunk_head = "trunk"
    trunk_tags = "trunk_tags/*"

    @classmethod
    def setUpClass(cls, **args):
        # Different arguments for SvnRepo vs. the base Repo.
        cls.repo_path="file://"+tempfile.mkdtemp()
        args.setdefault("trunk_head", cls.trunk_head)
        args.setdefault("trunk_tags", cls.trunk_tags)
        super().setUpClass(**args)
        cls.my_repo.create()

    @classmethod
    def tearDownClass(cls, **args):
        shutil.rmtree(re.sub("^file://","",\
                             cls.repo_path))
        super().tearDownClass(**args)

    def test_trunk_head(self):
        """Test that SvnRepo objects provide trunk path."""
        self.assertEqual(self.my_repo.trunk_head,
                         self.repo_path+"/"+self.trunk_head)

    def test_trunk_tag_expr(self):
        """Test that SvnRepo objects provide trunk tag expression."""
        self.assertEqual(self.my_repo.trunk_tags,
                         self.repo_path+"/"+self.trunk_tags)

    def test_trunk(self):
        """Test that SvnRepo objects provide the whole trunk
        branch."""
        trunk_branch = self.my_repo.trunk_branch
        self.assertEqual(trunk_branch.head,
                         self.trunk_head)
        self.assertEqual(trunk_branch.tags,
                         self.trunk_tags)

    def test_get_current_revision(self):
        """Test query for the latest revision number."""
        # Magic number; I happen to know that SvnRepo.create() will make
        # exactly two commits.
        self.assertEqual(self.my_repo.get_current_revision(), 2)

    def test_create(self):
        """Test that SvnRepo objects, when given a local directory,
        actually initialize a repo there."""
        svn_ls = subprocess.check_output(["svn", "ls", self.repo_path],
                                         universal_newlines=True)
        sub_dirs = svn_ls.splitlines()

        # Use get_path_start to make sure that the top level of the repo
        # is right.
        self.assertIn(get_path_start(self.trunk_head)+"/", sub_dirs)
        self.assertIn(get_path_start(self.trunk_tags)+"/", sub_dirs)


class TestSvnRepo(TestRepo):
    """Test the "SvnRepo" class."""

    repo_class = SvnRepo
    trunk_head = "trunk"
    trunk_tags = "trunk_tags/*"

    def setUp(self, **args):
        # Different arguments for SvnRepo vs. the base Repo.
        self.repo_path="file://"+tempfile.mkdtemp()
        args.setdefault("trunk_head", self.trunk_head)
        args.setdefault("trunk_tags", self.trunk_tags)
        super().setUp(**args)
        self.my_repo.create()

    def tearDown(self, **args):
        shutil.rmtree(re.sub("^file://","",\
                             self.repo_path))
        super().tearDown(**args)

    def test_trunk_import(self):
        """Test that we can import a file into the SvnRepo's trunk."""
        foo_path="foo"
        foo_contents="bar"
        with TempFile() as foo_file:
            with foo_file.open("w") as foo:
                foo.write(foo_contents)
            self.my_repo.trunk_import(foo_file.path, foo_path)

        svn_cat = subprocess.check_output(
            ["svn", "cat", self.my_repo.trunk_head+"/"+foo_path],
            universal_newlines=True,
        )
        self.assertEqual(svn_cat, foo_contents)

    def test_trunk_rm(self):
        """Test that we can remove a file from SvnRepo's trunk."""
        foo_path="foo"
        foo_contents="bar"
        with TempFile() as foo_file:
            with foo_file.open("w") as foo:
                foo.write(foo_contents)
            self.my_repo.trunk_import(foo_file.path, foo_path)

        self.my_repo.trunk_rm(foo_path)

        svn_ls = subprocess.check_output(
            ["svn", "ls",
             self.my_repo.trunk_head],
            universal_newlines=True,
        )
        sub_dirs = svn_ls.splitlines()
        self.assertNotIn(foo_path, sub_dirs)

    def test_make_trunk_tag(self):
        """Test that we can make a trunk tag using an SvnRepo."""
        tag_name = "v1"
        self.my_repo.make_trunk_tag(tag_name)

        svn_ls = subprocess.check_output(
            ["svn", "ls",
             self.repo_path+"/"+get_path_start(self.trunk_tags)],
            universal_newlines=True,
        )
        sub_dirs = svn_ls.splitlines()
        self.assertIn(tag_name+"/", sub_dirs)


# This is used to tame the test output, and to clear the environment so
# that tests can be run from a git hook.
_git_cmd_args = {
    "stdout": subprocess.DEVNULL,
    "stderr": subprocess.DEVNULL,
    "env": {},
}

class TestStaticGitRepo(TestStaticRepo):
    """Static tests for the "GitRepo" class.

    All the tests that don't change a repo are here.

    """

    repo_class = GitRepo

    @classmethod
    def setUpClass(cls, **args):
        cls.repo_path = tempfile.mkdtemp()
        super().setUpClass(**args)
        cls.my_repo.init(**_git_cmd_args)

    @classmethod
    def tearDownClass(cls, **args):
        shutil.rmtree(cls.repo_path)
        super().tearDownClass(**args)

    def test_init(self):
        """Test that using init on a GitRepo actually creates a repo."""
        subprocess.check_call(
            ["git", "--git-dir="+os.path.join(self.repo_path,".git"),
             "ls-files"],
            **_git_cmd_args
        )


class TestGitRepo(TestRepo):

    """Test the "GitRepo" class."""

    repo_class = GitRepo

    def setUp(self, **args):
        self.repo_path = tempfile.mkdtemp()
        super().setUp(**args)

    def tearDown(self, **args):
        shutil.rmtree(self.repo_path)
        super().tearDown(**args)


@contextlib.contextmanager
def SvnTestRepo():
    """Context manager for a Subversion test repo. This is set up for
    convenience in testing GitSvnRepo."""

    # Use SvnRepo object to initialize the repo in a temporary directory.
    svn_test_repo = SvnRepo(name="test_repo",
                            path="file://"+tempfile.mkdtemp(),
                            trunk_head="trunk",
                            trunk_tags="trunk_tags/*")
    svn_test_repo.create()

    # For now, just assume that the above is revision 2. Then this is
    # revision 3.
    with TempFile() as bad_file:
        with bad_file.open("w") as bad:
            bad.write("BADTOTHEBONE\n")
        svn_test_repo.trunk_import(bad_file.path, "bad", "Evil commit.")

    # Make a trunk tag.
    svn_test_repo.make_trunk_tag("bad_tag", "Making bad trunk tag.")

    svn_test_repo.trunk_rm("bad", "Undo evil.")

    # Add a file.
    with TempFile() as foo_file:
        with foo_file.open("w") as foo:
            foo.write("bar1\n")
        svn_test_repo.trunk_import(foo_file.path, "foo", "Adding foo.")

    # Make a trunk tag.
    svn_test_repo.make_trunk_tag("v1", "Making first trunk tag.")

    # *Finally*, we can return the SvnRepo object.
    yield svn_test_repo

    # This will execute when exiting the context.
    shutil.rmtree(re.sub("^file://","",
                         svn_test_repo.path))


class TestStaticGitSvnRepo(TestStaticGitRepo):

    """Test the "GitSvnRepo" class.

    Only for tests that don't make changes to the repository and only need
    a fairly "vanilla" setup.

    """

    repo_class = GitSvnRepo
    ignore_revs = (4,)
    clone_revision = None

    @classmethod
    def setUpClass(cls, **args):
        cls.svn_test_repo = SvnTestRepo()
        cls.my_svn_repo = cls.svn_test_repo.__enter__()
        args.setdefault("svn_repo", cls.my_svn_repo)
        args.setdefault("ignore_revs", cls.ignore_revs)
        super().setUpClass(**args)
        cls.my_repo.clone(revision=cls.clone_revision, **_git_cmd_args)

    @classmethod
    def tearDownClass(cls, **args):
        super().tearDownClass(**args)
        cls.svn_test_repo.__exit__(None, None, None)

    def test_svn_repo(self):
        """Check that the Subversion repo used to initialize a
        GitSvnRepo is preserved."""
        self.assertIs(self.my_svn_repo, self.my_repo.svn_repo)

    def test_get_svn_revision(self):
        """Check that we can query the revision number and get the same
        answer as Subversion gives."""
        # Magic number: I know that the last commit to the test repo was
        # the creation of a trunk tag, which doesn't change the revision
        # number that git-svn uses for the trunk. So I add 1 to make up the
        # difference.
        self.assertEqual(
            self.my_svn_repo.get_current_revision(),
            self.my_repo.get_svn_revision(**_git_cmd_args)+1
        )

    def test_clone(self):
        """Test that GitSvnRepo.clone() produces the expected content."""

        foo_path = os.path.join(self.repo_path,"foo")
        with open(foo_path,"r") as foo_file:
            foo_contents = foo_file.read()
        self.assertEqual(foo_contents,"bar1\n")

    def test_clone_tag(self):
        """Test that GitSvnRepo.clone() pulls in tags."""

        subprocess.check_call(
            ["git", "show-ref", "-q", "--verify", "refs/remotes/tags/v1"],
            cwd=self.repo_path,
            **_git_cmd_args
        )

    def test_ignore_revs(self):
        """Test that GitSvnRepo.clone skips ignored revisions."""

        # If revision 4 was skipped, "bad_tag" should be missing.
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_call(
                ["git", "show-ref", "-q", "--verify",
                 "refs/remotes/tags/bad_tag"],
                cwd=self.repo_path,
                **_git_cmd_args
            )


class TestGitSvnRepoBase(TestGitRepo):
    """Base class for classes to test "GitSvnRepo".

    Only for tests that don't make changes to the upstream Subversion
    repository.

    """

    repo_class = GitSvnRepo
    ignore_revs = ()

    @classmethod
    def setUpClass(cls, **args):
        cls.svn_test_repo = SvnTestRepo()
        cls.my_svn_repo = cls.svn_test_repo.__enter__()

    @classmethod
    def tearDownClass(cls, **args):
        cls.svn_test_repo.__exit__(None, None, None)

    def setUp(self, **args):
        args.setdefault("svn_repo", self.my_svn_repo)
        args.setdefault("ignore_revs", self.ignore_revs)
        super().setUp(**args)

    def tearDown(self, **args):
        super().tearDown(**args)

class TestGitSvnRepo(TestGitSvnRepoBase):

    """Tests for GitSvnRepo using one ignored revision."""

    ignore_revs = (4,)

    def test_clone_revision(self):
        """Test that GitSvnRepo.clone() respects the revision argument."""
        self.my_repo.clone(
            revision=3,
            **_git_cmd_args
        )
        sub_dirs = os.listdir(self.repo_path)

        # At revision 3, we have the bad file, but not foo.
        self.assertIn("bad", sub_dirs)
        self.assertNotIn("foo", sub_dirs)

    def test_rebase(self):
        """Test that GitSvnRepo.rebase() updates the repository."""
        self.my_repo.clone(
            revision=3,
            **_git_cmd_args
        )

        self.my_repo.rebase(**_git_cmd_args)

        # If revision 4 was skipped, "bad_tag" should be missing.
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_call(
                ["git", "show-ref", "-q", "--verify",
                 "refs/remotes/tags/bad_tag"],
                cwd=self.repo_path,
                **_git_cmd_args
            )

        sub_dirs = os.listdir(self.repo_path)

        # After an update, should have foo, but not the bad file.
        self.assertNotIn("bad", sub_dirs)
        self.assertIn("foo", sub_dirs)


class TestGitSvnRepo2(TestGitSvnRepoBase):

    """Test the "GitSvnRepo" class with multiple ignore_revs."""

    repo_class = GitSvnRepo
    ignore_revs = (7,4)

    def test_rebase_revision(self):
        """Test that GitSvnRepo.rebase respects the "revision" argument."""
        self.my_repo.clone(
            revision=1,
            **_git_cmd_args
        )

        self.my_repo.rebase(revision=5, **_git_cmd_args)

        # If revision 4 was skipped, "bad_tag" should be missing.
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.check_call(
                ["git", "show-ref", "-q", "--verify",
                 "refs/remotes/tags/bad_tag"],
                cwd=self.repo_path,
                **_git_cmd_args
            )

        # At revision 5, there should be no files.
        sub_dirs = os.listdir(self.repo_path)
        self.assertNotIn("bad", sub_dirs)
        self.assertNotIn("foo", sub_dirs)


if __name__ == "__main__":
    unittest.main()
