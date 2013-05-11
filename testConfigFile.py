#!/usr/bin/env python3

from SvnHack import ConfigFile
import unittest

class TestConfigFile(unittest.TestCase):
    """Test the "ConfigFile" class."""
    file_path = "test_files/test_repo.def"
    def setUp(self):
        self.my_config_file = ConfigFile.ConfigFile(self.file_path)
    def test_path(self):
        self.assertEqual(self.my_config_file.path, self.file_path)
    def test_read_repo(self):
        repo = self.my_config_file.read_repo()
        self.assertEqual(repo.name, "test_repo")
        self.assertEqual(repo.path, "/path/to/test_repo")
        self.assertEqual(repo.svn_repo.name, "svn_test_repo")
        self.assertEqual(repo.svn_repo.path, "https://path/to/svn_origin")


if __name__ == "__main__":
    unittest.main()
