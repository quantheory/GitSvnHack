#!/usr/bin/env python3

from SvnHack import RepoClasses
import unittest

class TestRepo(unittest.TestCase):
    """Test the "Repo" class."""
    repo_name = "test_repo"
    repo_class = RepoClasses.Repo
    repo_path = "/path/to/fake"
    def setUp(self):
        self.my_repo = self.repo_class(self.repo_name, self.repo_path)
    def test_name(self):
        """Test that Repo objects retain names from __init__."""
        self.assertEqual(self.my_repo.name, self.repo_name)
    def test_path(self):
        """Test that Repo objects retain paths from __init__."""
        self.assertEqual(self.my_repo.path, self.repo_path)

class TestLocalRepo(TestRepo):
    """Test the "LocalRepo" class."""
    repo_class = RepoClasses.LocalRepo

class TestSvnRepo(TestRepo):
    """Test the "SvnRepo" class."""
    repo_class = RepoClasses.SvnRepo

class TestGitSvnRepo(TestRepo):
    """Test the "GitSvnRepo" class."""
    repo_class = RepoClasses.GitSvnRepo

if __name__ == "__main__":
    unittest.main()
