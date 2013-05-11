#!/usr/bin/env python3

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
    key_str = "key1"
    val_str = "value1"
    file_string = key_str+"="+val_str
    def test_path(self):
        """Test "path" method output."""
        self.assertEqual(self.my_cfg_file.path(), self.cfg_name)
    def test_read_dict(self):
        """Test "read_dict" output."""
        cfg_dict = self.my_cfg_file.read_dict()
        test_dict = { self.key_str: self.val_str }
        self.assertDictEqual(cfg_dict, test_dict)

class TestConfigFileBadLine(TestConfigBase):
    """Test bad line error from the "ConfigFile" class."""
    file_string = "This is no good as a ConfigFile."
    def test_bad_line(self):
        """Test that a file with a bad line raises ValueError."""
        with self.assertRaises(ValueError):
            self.my_cfg_file.read_dict()

class TestConfigFileEmpty(TestConfigBase):
    """Test empty line in the "ConfigFile" class."""
    file_string = "\n\n"
    def test_empty_line(self):
        """Test that reading an empty line is fine."""
        self.my_cfg_file.read_dict()

class TestConfigFileComment(TestConfigBase):
    """Test comment line in the "ConfigFile" class."""
    file_string = "  # Hi! \n"
    def test_comment_line(self):
        """Test that reading a comment line is fine."""
        self.my_cfg_file.read_dict()

class TestGitSvnDefFile(TestConfigBase):
    """Test the "TestGitSvnDefFile" class."""
    cfg_file_class = ConfigFile.GitSvnDefFile
    repo_name = "test_repo"
    repo_path = "/path/to/test_repo"
    repo_svnurl = "https://path/to/svn_origin"
    file_string = "name = "+repo_name+"\n" \
        "path = "+repo_path+"\n" \
        "svnurl = "+repo_svnurl
    def test_read_repo(self):
        """Test the read_repo method."""
        repo = self.my_cfg_file.read_repo()
        self.assertEqual(repo.name(), self.repo_name)
        self.assertEqual(repo.path(), self.repo_path)
        self.assertEqual(repo.svn_repo.name(), "svn_"+self.repo_name)
        self.assertEqual(repo.svn_repo.path(), self.repo_svnurl)

if __name__ == "__main__":
    unittest.main()
