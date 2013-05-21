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
    cfg_file_class = ConfigFile.ConfigFile
    def setUp(self):
        """Create a mock configuration file."""
        self.cfg_name = write_temp_file(self.file_string)
        self.my_cfg_file = self.cfg_file_class(self.cfg_name)
    def tearDown(self):
        """Remove configuration file."""
        os.remove(self.cfg_name)

class TestConfigFile(TestConfigBase):
    """Test the "ConfigFile" class."""
    sect_str = "section1"
    key_str = "key1"
    val_str = "value1"
    file_string = "["+sect_str+"]\n"+key_str+"="+val_str
    def test_path(self):
        """Test "path" method output."""
        self.assertEqual(self.my_cfg_file.get_path(), self.cfg_name)
    def test_get_dict(self):
        """Test "get_dict" output."""
        cfg_dict = self.my_cfg_file.get_dict()
        test_dict = { self.key_str: self.val_str }
        self.assertDictEqual(cfg_dict, test_dict)

class TestConfigFileBadLine(TestConfigBase):
    """Test bad line error from the "ConfigFile" class."""
    file_string = "This is no good as a ConfigFile."
    def test_bad_line(self):
        """Test that a file with a bad line raises ValueError."""
        with self.assertRaises(ValueError):
            self.my_cfg_file.get_dict()

class TestConfigFileEmpty(TestConfigBase):
    """Test empty line in the "ConfigFile" class."""
    file_string = "\n\n"
    def test_empty_line(self):
        """Test that reading an empty line is fine."""
        self.my_cfg_file.get_dict()

class TestConfigFileComment(TestConfigBase):
    """Test comment line in the "ConfigFile" class."""
    file_string = "  # Hi! \n"
    def test_comment_line(self):
        """Test that reading a comment line is fine."""
        self.my_cfg_file.get_dict()

class TestGitSvnDefFile(TestConfigBase):
    """Test the "TestGitSvnDefFile" class."""
    cfg_file_class = ConfigFile.GitSvnDefFile
    repo_name = "test_repo"
    repo_path = "/path/to/test_repo"
    repo_svn_url = "https://path/to/svn_origin"
    repo_svn_trunk_head = "trunk"
    repo_svn_trunk_tags = "trunk_tags/*"
    file_string = "["+repo_name+"]\n" \
                  "name = "+repo_name+"\n" \
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
