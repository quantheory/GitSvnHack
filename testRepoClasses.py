#!/usr/bin/env python3

from GitSvnHack import RepoClasses
import unittest

import tempfile
import subprocess
import os
import shutil
import re

# Could do something sophisticated or elegant, but easiest to just
# wrap Subversion's CLI.
# For before python 3.3, need this:
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
    # In order to add a file, we need a working copy.
    wc_path = tempfile.mkdtemp()
    subprocess.check_call(["svn","co",repo_url+"/trunk",wc_path],
                          stdout=subprocess.DEVNULL)
    # Subversion paths always use forward slash, but use os.path.join
    # to add a local "foo" file in the working copy.
    foo_path = os.path.join(wc_path,"foo")
    with open(foo_path,"w") as foo_file:
        foo_file.write("bar\n")
    subprocess.check_call(["svn","add",foo_path],
                          stdout=subprocess.DEVNULL)
    subprocess.check_call(["svn","ci",wc_path,
                           "-m","Adding foo."],
                          stdout=subprocess.DEVNULL)
    # Get rid of that working copy.
    shutil.rmtree(wc_path)
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
    def test_trunk(self):
        """Test that SvnRepo objects provide trunk path."""
        self.assertEqual(self.my_repo.get_trunk_head(),
                         self.repo_path+"/"+self.trunk_head)
    def test_trunk_tag_expr(self):
        """Test that SvnRepo objects provide trunk tag expression."""
        self.assertEqual(self.my_repo.get_trunk_tag_expr(),
                         self.repo_path+"/"+self.trunk_tags)

class TestGitRepo(TestRepo):
    """Test the "GitRepo" class."""
    repo_class = RepoClasses.GitRepo

class TestGitSvnRepo(TestGitRepo):
    """Test the "GitSvnRepo" class."""
    repo_class = RepoClasses.GitSvnRepo
    def setUp(self):
        self.my_svn_repo = svn_make_test_repo()
        self.my_repo = self.repo_class(self.repo_name,
                                       self.repo_path,
                                       self.my_svn_repo)
    def test_svn_repo(self):
        self.assertIs(self.my_svn_repo, self.my_repo.svn_repo)
    def tearDown(self):
        shutil.rmtree(re.sub("^file://","",
                             self.my_svn_repo.get_path()))

if __name__ == "__main__":
    unittest.main()
