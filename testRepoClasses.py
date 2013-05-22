#!/usr/bin/env python3
"""Unit test module for RepoClasses.py"""

from GitSvnHack import RepoClasses
import unittest

import os
import re
import shutil
import subprocess
import sys
import tempfile

# Could do something sophisticated or elegant, but easiest to just
# wrap Subversion's CLI.

# For before Python 3.3, need this:
if sys.version_info[0:1] < (3,3):
    subprocess.DEVNULL = os.open(os.devnull,os.O_WRONLY)

def svn_make_test_repo():
    """Returns a URL corresponding to a locally created Subversion
    repo."""
    # Create file and get URL.
    repo_path = tempfile.mkdtemp()
    subprocess.check_call(["svnadmin","create",repo_path])
    repo_url = "file://"+repo_path
    # Create top level directories.
    subprocess.check_call(["svn","mkdir",repo_url+"/trunk",
                           "-m","Creating trunk directory."],
                          stdout=subprocess.DEVNULL)
    subprocess.check_call(["svn","mkdir",repo_url+"/trunk_tags",
                           "-m","Creating trunk_tags directory"],
                          stdout=subprocess.DEVNULL)
    # Add a file.
    foo_fd,foo_path = tempfile.mkstemp()
    with os.fdopen(foo_fd,"w") as foo_file:
        foo_file.write("bar\n")
    subprocess.check_call(["svn","import",foo_path,
                           repo_url+"/trunk/foo",
                           "-m","Adding foo."],
                          stdout=subprocess.DEVNULL)
    # Remove local file
    os.remove(foo_path)
    # Make a trunk tag.
    subprocess.check_call(["svn","cp",repo_url+"/trunk",
                           repo_url+"/trunk_tags/v1",
                           "-m","Making first trunk tag."],
                          stdout=subprocess.DEVNULL)
    # *Finally*, we can create the SvnRepo object and return it.
    return RepoClasses.SvnRepo("test_repo",repo_url,
                               "trunk","trunk_tags/*")

class TestRepo(unittest.TestCase):
    """Test the "Repo" class."""
    repo_class = RepoClasses.Repo
    repo_name = "test_repo"
    repo_path = "/path/to/fake"
    def setUp(self):
        self.my_repo = self.repo_class(self.repo_name, self.repo_path)
    def test_name(self):
        """Test that Repo objects retain names from __init__."""
        self.assertEqual(self.my_repo.get_name(), self.repo_name)
    def test_path(self):
        """Test that Repo objects retain paths from __init__."""
        self.assertEqual(self.my_repo.get_path(), self.repo_path)

class TestSvnBranch(unittest.TestCase):
    """Test the "SvnBranch" class."""
    branch_class = RepoClasses.SvnBranch
    head_path = "trunk"
    tag_expr = "trunk_tags/*"
    def setUp(self):
        self.my_branch = self.branch_class(self.head_path,
                                           self.tag_expr)
    def test_head(self):
        """Test that branch objects retain path to HEAD."""
        self.assertEqual(self.my_branch.get_head(), self.head_path)
    def test_tag_expr(self):
        """Test that branch objects retain tag path expression."""
        self.assertEqual(self.my_branch.get_tag_expr(), self.tag_expr)

class TestSvnRepo(TestRepo):
    """Test the "SvnRepo" class."""
    repo_class = RepoClasses.SvnRepo
    trunk_head = "trunk"
    trunk_tags = "trunk_tags/*"
    def setUp(self):
        self.my_repo = self.repo_class(self.repo_name, self.repo_path,
                                       self.trunk_head, self.trunk_tags)
    def test_trunk_head(self):
        """Test that SvnRepo objects provide trunk path."""
        self.assertEqual(self.my_repo.get_trunk_head(),
                         self.repo_path+"/"+self.trunk_head)
    def test_trunk_tag_expr(self):
        """Test that SvnRepo objects provide trunk tag expression."""
        self.assertEqual(self.my_repo.get_trunk_tag_expr(),
                         self.repo_path+"/"+self.trunk_tags)
    def test_trunk(self):
        """Test that SvnRepo objects provide the whole trunk
        branch."""
        trunk_branch = self.my_repo.get_trunk()
        self.assertEqual(trunk_branch.get_head(),
                         self.trunk_head)
        self.assertEqual(trunk_branch.get_tag_expr(),
                         self.trunk_tags)

class TestGitRepo(TestRepo):
    """Test the "GitRepo" class."""
    repo_class = RepoClasses.GitRepo

class TestGitSvnRepo(TestGitRepo):
    """Test the "GitSvnRepo" class."""
    repo_class = RepoClasses.GitSvnRepo
    def setUp(self):
        self.repo_path = tempfile.mkdtemp()
        self.my_svn_repo = svn_make_test_repo()
        self.my_repo = self.repo_class(self.repo_name,
                                       self.repo_path,
                                       self.my_svn_repo)
    def test_svn_repo(self):
        self.assertIs(self.my_svn_repo, self.my_repo.svn_repo)
    def test_clone(self):
        self.my_repo.clone(stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        foo_path = os.path.join(self.repo_path,"foo")
        with open(foo_path,"r") as foo_file:
            foo_contents=foo_file.read()
        self.assertEqual(foo_contents,"bar\n")
    def tearDown(self):
        shutil.rmtree(re.sub("^file://","",
                             self.my_svn_repo.get_path()))
        shutil.rmtree(self.repo_path)

if __name__ == "__main__":
    unittest.main()
