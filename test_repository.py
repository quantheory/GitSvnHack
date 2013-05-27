#!/usr/bin/env python3
"""Unit test module for repository.py"""

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

def svn_make_test_repo():
    """Returns a URL corresponding to a locally created Subversion
    repo."""

    # Create repo directory and get URL.
    repo_path = tempfile.mkdtemp()
    repo_url = "file://"+repo_path

    # Use SvnRepo object to initialize the repo there.
    svn_test_repo = SvnRepo(name="test_repo",
                            path=repo_url,
                            trunk_head="trunk",
                            trunk_tags="trunk_tags/*")
    svn_test_repo.create()

    # Add a file.
    with TempFile() as foo_file:
        with foo_file.open("w") as foo:
            foo.write("bar1\n")
        subprocess.check_call(
            ["svn", "import", foo_file.path, repo_url+"/trunk/foo",
             "-m", "Adding foo."],
            stdout=subprocess.DEVNULL
        )

    # Make a trunk tag.
    subprocess.check_call(
        ["svn", "cp", repo_url+"/trunk", repo_url+"/trunk_tags/v1",
         "-m", "Making first trunk tag."],
        stdout=subprocess.DEVNULL
    )
    # *Finally*, we can create the SvnRepo object and return it.
    return svn_test_repo


class TestRepo(unittest.TestCase):
    """Test the "Repo" class."""

    repo_class = Repo
    repo_name = "test_repo"
    repo_path = "/path/to/fake"

    def setUp(self, **args):
        args.setdefault("name",self.repo_name)
        args.setdefault("path",self.repo_path)
        self.my_repo = self.repo_class(**args)

    def test_name(self):
        """Test that Repo objects retain names from __init__."""
        self.assertEqual(self.my_repo.name, self.repo_name)

    def test_path(self):
        """Test that Repo objects retain paths from __init__."""
        self.assertEqual(self.my_repo.path, self.repo_path)

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

    def tearDown(self):
        shutil.rmtree(re.sub("^file://","",\
                             self.repo_path))

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

    def test_create(self):
        """Test that SvnRepo objects, when given a local directory, can
        actually initialize a repo there."""
        self.my_repo.create()
        svn_ls = subprocess.check_output(["svn","ls",self.repo_path],
                                       universal_newlines=True)
        sub_dirs = svn_ls.splitlines()

        def get_path_start(string):
            """Returns everything before the first "/" in as string."""
            idx = string.find("/")
            # Return the string up to the index, or the whole string if
            # there was no "/" (idx < 0).
            if idx >= 0:
                return string[:idx]
            else:
                return string

        # Use get_path_start to make sure that the top level of the repo
        # is right.
        self.assertIn(get_path_start(self.trunk_head)+"/",sub_dirs)
        self.assertIn(get_path_start(self.trunk_tags)+"/",sub_dirs)


class TestGitRepo(TestRepo):
    """Test the "GitRepo" class."""
    repo_class = GitRepo


class TestGitSvnRepo(TestGitRepo):
    """Test the "GitSvnRepo" class."""

    repo_class = GitSvnRepo

    def setUp(self, **args):
        self.repo_path = tempfile.mkdtemp()
        self.my_svn_repo = svn_make_test_repo()
        args.setdefault("svn_repo", self.my_svn_repo)
        super().setUp(**args)

    def tearDown(self):
        shutil.rmtree(re.sub("^file://","",
                             self.my_svn_repo.path))
        shutil.rmtree(self.repo_path)

    def test_svn_repo(self):
        """Check that the Subversion repo used to initialize a
        GitSvnRepo is preserved."""
        self.assertIs(self.my_svn_repo, self.my_repo.svn_repo)

    def test_clone(self):
        """Test GitSvnRepo's clone method."""
        self.my_repo.clone(stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        foo_path = os.path.join(self.repo_path,"foo")
        with open(foo_path,"r") as foo_file:
            foo_contents = foo_file.read()
        self.assertEqual(foo_contents,"bar1\n")


if __name__ == "__main__":
    unittest.main()
