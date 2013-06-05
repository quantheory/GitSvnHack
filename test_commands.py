#!/usr/bin/env python3
""""Tests for the GitSvnHack.commands module."""

from GitSvnHack.commands import default
import sys
import unittest

# In Python 3.2, there is no unittest.mock, but the old mock library may be
# installed:
if sys.version_info[0:1] < (3,3):
    import mock
else:
    import unittest.mock


class TestDefault(unittest.TestCase):

    """Test the default command."""

    @mock.patch('os.execvp')
    def test_default(self, mock_exec):
        """Test that the default command calls git svn correctly."""
        args = ["foo", "bar"]
        default(args)
        mock_exec.assert_called_once_with("git", ["git","svn"]+args)


if __name__ == "__main__":
    unittest.main()
