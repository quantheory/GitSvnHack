#!/usr/bin/env python3
""""Tests for the GitSvnHack.commands module."""

from GitSvnHack.commands import clone, default

import sys
import unittest

# In Python 3.2, there is no unittest.mock, but the old mock library may be
# installed:
if sys.version_info[0:1] < (3,3):
    import mock
else:
    import unittest.mock


class TestClone(unittest.TestCase):

    """Test the clone command."""

    @mock.patch('GitSvnHack.commands.GitSvnRepo')
    @mock.patch('GitSvnHack.commands.SvnRepo')
    def test_clone(self, mock_SvnRepo, mock_GitSvnRepo):
        """Test basic functionality of the clone command.

        This verifies that the command interacts with the Repo commands as
        expected.

        """
        args = [
            "file://foo", "git_foo",
            "--config-name", "foo_name", "--username", "joe",
            "-T", "bar_tr", "--tags", "bar_ta",
            "--ignore-revs", "22",
        ]
        clone(args)
        mock_SvnRepo.assert_called_once_with(
            name="foo_name_svn",
            path="file://foo",
            trunk_head="bar_tr",
            trunk_tags="bar_ta",
        )
        mock_GitSvnRepo.assert_called_once_with(
            name="foo_name",
            path="git_foo",
            svn_repo=mock_SvnRepo.return_value,
            ignore_revs=[22],
        )
        mock_GitSvnRepo.return_value.clone.assert_called_once_with(
            git_args=["--username", "joe"],
        )

    @mock.patch('GitSvnHack.commands.GitSvnRepo')
    @mock.patch('GitSvnHack.commands.SvnRepo')
    def test_clone_minimal(self, mock_SvnRepo, mock_GitSvnRepo):
        """Test clone command with minimal arguments.

        This tests that the clone command can fill in some arguments.

        """
        args = [
            "file://foo",
            "-T", "bar_tr", "--tags", "bar_ta",
        ]
        clone(args)
        mock_SvnRepo.assert_called_once_with(
            name="unknown_svn",
            path="file://foo",
            trunk_head="bar_tr",
            trunk_tags="bar_ta",
        )
        mock_GitSvnRepo.assert_called_once_with(
            name="unknown",
            path="foo",
            svn_repo=mock_SvnRepo.return_value,
            ignore_revs=[],
        )
        mock_GitSvnRepo.return_value.clone.assert_called_once_with(
            git_args=[],
        )


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
