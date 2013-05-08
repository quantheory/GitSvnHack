#!/usr/bin/env python3

from SvnHack import ConfigFile
import unittest

class TestConfigFile(unittest.TestCase):
    """Test the "ConfigFile" class."""
    file_name = "test_files/test_repo.def"
    def setUp(self):
        self.my_config_file = ConfigFile.ConfigFile(self.file_name)
    def test_name(self):
        self.assertEqual(self.my_config_file.name, self.file_name)
