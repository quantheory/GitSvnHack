#!/usr/bin/env python3
"""Unit test module for ConfigFile.py"""

from GitSvnHack import ConfigFile
import unittest
from tempfile import mkstemp
import os

def write_temp_file(string):
    """Writes a string to a temporary file and returns the name."""
    fd,cfg_name = mkstemp(text=True)
    with os.fdopen(fd, "w") as tmp_file:
        tmp_file.write(string)
    return cfg_name

class TestConfigBase(unittest.TestCase):
    """Base test class for ConfigFile tests."""
    def setUp(self):
        """Create a mock configuration file."""
        self.cfg_name = write_temp_file(self.file_string)
        self.my_cfg_file = self.cfg_file_class(self.cfg_name)
    def tearDown(self):
        """Remove configuration file."""
        os.remove(self.cfg_name)

class TestGitSvnDefFile(TestConfigBase):
    """Test the "TestGitSvnDefFile" class."""
    cfg_file_class = ConfigFile.GitSvnDefFile
    repo_name = "test_repo"
    repo_path = "/path/to/test_repo"
    repo_svn_url = "https://path/to/svn_origin"
    repo_svn_trunk_head = "trunk"
    repo_svn_trunk_tags = "trunk_tags/*"
    file_string = "["+repo_name+"]\n" \
                  "path = "+repo_path+"\n" \
                  "svn_url = "+repo_svn_url+"\n" \
                  "svn_trunk = "+repo_svn_trunk_head+ \
                  ","+repo_svn_trunk_tags
    def test_get_repos(self):
        """Test the get_repos method with one repo."""
        repo = self.my_cfg_file.get_repos()[0]
        self.assertEqual(repo.get_name(), self.repo_name)
        self.assertEqual(repo.get_path(), self.repo_path)
        self.assertEqual(repo.svn_repo.get_name(), "svn_"+self.repo_name)
        self.assertEqual(repo.svn_repo.get_path(), self.repo_svn_url)
        self.assertEqual(repo.svn_repo.get_trunk_head(),
                         self.repo_svn_url+"/"+self.repo_svn_trunk_head)
        self.assertEqual(repo.svn_repo.get_trunk_tag_expr(),
                         self.repo_svn_url+"/"+self.repo_svn_trunk_tags)

if __name__ == "__main__":
    unittest.main()
