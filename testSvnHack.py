#!/usr/bin/env python3

from SvnHack import RepoClasses
import unittest

class TestRepo(unittest.TestCase):
    """Test the "Repo" class."""
    repo_name = "test_repo"
    def setUp(self):
        self.my_repo = RepoClasses.Repo(self.repo_name)
    def test_name(self):
        """Test that Repo objects retain names from __init__."""
        self.assertEqual(self.my_repo.name, self.repo_name)

class TestSvnRepo(TestRepo):
    """Test the "SvnRepo" class."""
    def setUp(self):
        self.my_repo = RepoClasses.SvnRepo(self.repo_name)

if __name__ == "__main__":
    unittest.main()
