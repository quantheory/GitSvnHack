#!/usr/bin/env python3

from SvnHack import RepoClasses
import unittest

class TestRepo(unittest.TestCase):
    """Test the "Repo" class."""
    repo_class = RepoClasses.Repo
    repo_name = "test_repo"
    repo_path = "/path/to/fake"
    def setUp(self):
        self.my_repo = self.repo_class(self.repo_name, self.repo_path)
    def test_name(self):
        """Test that Repo objects retain names from __init__."""
        self.assertEqual(self.my_repo.name(), self.repo_name)
    def test_path(self):
        """Test that Repo objects retain paths from __init__."""
        self.assertEqual(self.my_repo.path(), self.repo_path)

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
        self.assertEqual(self.my_branch.head(), self.head_path)
    def test_tag_expr(self):
        """Test that branch objects retain tag path expression."""
        self.assertEqual(self.my_branch.tag_expr(), self.tag_expr)

class TestSvnRepo(TestRepo):
    """Test the "SvnRepo" class."""
    repo_class = RepoClasses.SvnRepo

class TestGitRepo(TestRepo):
    """Test the "GitRepo" class."""
    repo_class = RepoClasses.GitRepo

class TestGitSvnRepo(TestGitRepo):
    """Test the "GitSvnRepo" class."""
    repo_class = RepoClasses.GitSvnRepo
    svn_repo_class = RepoClasses.SvnRepo
    svn_repo_name = "test_svn_repo"
    svn_repo_path = "https://path/to/fake"
    def setUp(self):
        self.my_svn_repo = self.svn_repo_class(self.svn_repo_name,
                                               self.svn_repo_path)
        self.my_repo = self.repo_class(self.repo_name,
                                       self.repo_path,
                                       self.my_svn_repo)
    def test_svn_repo(self):
        self.assertIs(self.my_svn_repo, self.my_repo.svn_repo)

if __name__ == "__main__":
    unittest.main()
