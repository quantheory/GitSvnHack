#!/usr/bin/env python3

from SvnHack import ConfigFile
import unittest

class TestConfigFile(unittest.TestCase):
    """Test the "ConfigFile" class."""
    cfg_def = "test_files/test_config.def"
    def setUp(self):
        self.my_cfg_file = ConfigFile.ConfigFile(self.cfg_def)
    def test_path(self):
        self.assertEqual(self.my_cfg_file.path(), self.cfg_def)
    def test_read_dict(self):
        cfg_dict = self.my_cfg_file.read_dict()
        test_dict = { "key1": "value1" }
        self.assertDictEqual(cfg_dict, test_dict)

class TestGitSvnDefFile(unittest.TestCase):
    """Test the "TestGitSvnDefFile" class."""
    repo_def = "test_files/test_repo.def"
    def setUp(self):
        self.my_repo_file = ConfigFile.GitSvnDefFile(self.repo_def)
    def test_read_repo(self):
        repo = self.my_repo_file.read_repo()
        self.assertEqual(repo.name, "test_repo")
        self.assertEqual(repo.path, "/path/to/test_repo")
        self.assertEqual(repo.svn_repo.name, "svn_test_repo")
        self.assertEqual(repo.svn_repo.path, "https://path/to/svn_origin")

if __name__ == "__main__":
    unittest.main()
