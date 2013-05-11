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
