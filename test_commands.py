#!/usr/bin/env python3
""""Tests for the GitSvnHack.commands module."""

from GitSvnHack.commands import *

import os
import sys
import unittest

# In Python 3.2, there is no unittest.mock, but the old mock library may be
# installed:
if sys.version_info[0:1] < (3,3):
    import mock
else:
    import unittest.mock

class TestParsedArgs(unittest.TestCase):

    """Test the ParsedArgs class."""

    def test_get_string_list(self):
        """Check that we get back the same arguments that are put in."""
        test_args = ParsedArgs([("--bar", "bararg")], ["foo"])
        self.assertCountEqual(test_args.get_string_list(),
                              ["foo", "--bar", "bararg"])

    def test_pop_any_opt_of_nomatch(self):
        """Test popping a non-present argument from the option list."""
        test_args = ParsedArgs([], [])
        self.assertIsNone(test_args.pop_any_opt_of("-z"))

    def test_pop_any_opt_of_bin(self):
        """Test popping a binary argument from the option list."""
        test_args = ParsedArgs([("-b", "")], [])
        self.assertTrue(test_args.pop_any_opt_of("-b"))
        self.assertIsNone(test_args.pop_any_opt_of("-b"))

    def test_pop_any_opt_of_dup(self):
        """Test popping a duplicate argument from the option list."""
        test_args = ParsedArgs([("-b", ""), ("-b", ""), ("-b", "")], [])
        self.assertTrue(test_args.pop_any_opt_of("-b"))
        self.assertTrue(test_args.pop_any_opt_of("-b"))
        self.assertTrue(test_args.pop_any_opt_of("-b"))
        self.assertIsNone(test_args.pop_any_opt_of("-b"))

    def test_pop_any_opt_of_multi(self):
        """Test popping any of several arguments."""
        test_args = ParsedArgs([("-b", ""), ("-n", "")], [])
        self.assertTrue(test_args.pop_any_opt_of("-b", "-n", "-z"))
        self.assertTrue(test_args.pop_any_opt_of("-b", "-n", "-z"))
        self.assertIsNone(test_args.pop_any_opt_of("-b", "-n", "-z"))

    def test_pop_any_opt_of_string(self):
        """Test popping a string argument from the option list."""
        test_args = ParsedArgs([("-s", "foo")], [])
        self.assertEqual(test_args.pop_any_opt_of("-s"), "foo")
        self.assertIsNone(test_args.pop_any_opt_of("-s"))

    def test_get_any_opt_of_nomatch(self):
        """Test getting a non-present argument from the option list."""
        test_args = ParsedArgs([], [])
        self.assertIsNone(test_args.get_any_opt_of("-z"))

    def test_get_any_opt_of_bin(self):
        """Test getting binary arguments from the option list."""
        test_args = ParsedArgs([("-b", ""),("-n", "")], [])
        self.assertTrue(test_args.get_any_opt_of("-b"))
        self.assertTrue(test_args.get_any_opt_of("-b"))
        self.assertTrue(test_args.get_any_opt_of("-b", "-n", "-z"))

    def test_get_any_opt_of_string(self):
        """Test popping a string argument from the option list."""
        test_args = ParsedArgs([("-s", "foo")], [])
        self.assertEqual(test_args.get_any_opt_of("-s"), "foo")

    def test_pop_arg(self):
        """Test popping an argument from the list."""
        test_args = ParsedArgs([], ["foo"])
        self.assertEqual(test_args.pop_arg(), "foo")
        self.assertIsNone(test_args.pop_arg())

class TestOptSpec(unittest.TestCase):

    """Test the OptSpec class."""

    shortopts1 = "a:"
    longopts1 = [ "aa=" ]
    shortopts2 = "b"
    longopts2 = [ "bb" ]

    def setUp(self):
        self.opts1 = OptSpec(self.shortopts1, self.longopts1)
        self.opts2 = OptSpec(self.shortopts2, self.longopts2)

    def test_copy(self):
        """Check to see if copies are exact."""
        opts_new = self.opts1.copy()
        self.assertEqual(opts_new._shortopts, self.opts1._shortopts)
        self.assertEqual(opts_new._longopts, self.opts1._longopts)

    def test_parse(self):
        """Test argument parsing."""
        opts, args = self.opts1.parse(["--aa", "foo", "-a", "foo2", "bar"])
        self.assertIn(("--aa", "foo"), opts)
        self.assertIn(("-a", "foo2"), opts)
        self.assertIn("bar", args)
        opts, args = self.opts2.parse(["bar2", "-b", "--bb"])
        self.assertIn(("--bb", ""), opts)
        self.assertIn(("-b", ""), opts)
        self.assertIn("bar2", args)

    def test___iadd__(self):
        """Test in-place combination of OptSpec objects."""
        self.opts1 += self.opts2
        self.assertEqual(self.opts1._shortopts,
                         self.shortopts1+self.shortopts2)
        self.assertEqual(self.opts1._longopts,
                         self.longopts1+self.longopts2)
        self.assertEqual(self.opts2._shortopts, self.shortopts2)
        self.assertEqual(self.opts2._longopts, self.longopts2)

    def test___add__(self):
        """Test creation of a new OptSpec by combining old ones."""
        opts_new = self.opts1 + self.opts2
        self.assertEqual(opts_new._shortopts,
                         self.shortopts1+self.shortopts2)
        self.assertEqual(opts_new._longopts,
                         self.longopts1+self.longopts2)
        self.assertEqual(self.opts1._shortopts, self.shortopts1)
        self.assertEqual(self.opts1._longopts, self.longopts1)
        self.assertEqual(self.opts2._shortopts, self.shortopts2)
        self.assertEqual(self.opts2._longopts, self.longopts2)


class TestInit(unittest.TestCase):

    """Test the init command."""

    @mock.patch('GitSvnHack.commands.GitSvnRepo')
    @mock.patch('GitSvnHack.commands.SvnRepo')
    def test_init(self, mock_SvnRepo, mock_GitSvnRepo):
        """Test basic functionality of the init command.

        This verifies that the command interacts with the Repo objects as
        expected.

        """
        args = [
            "file://foo", "git_foo",
            "--config-name", "foo_name", "--username", "joe",
            "-T", "bar_tr", "--tags", "bar_ta",
            "--ignore-revs", "22",
        ]
        init(args)
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
        mock_GitSvnRepo.return_value.init.assert_called_once_with(
            git_args=["--username", "joe"],
        )

    @mock.patch('GitSvnHack.commands.GitSvnRepo')
    @mock.patch('GitSvnHack.commands.SvnRepo')
    def test_init_minimal(self, mock_SvnRepo, mock_GitSvnRepo):
        """Test init command with minimal arguments.

        This tests that the init command can fill in some arguments.

        """
        args = [
            "file://foo", "-s",
        ]
        init(args)
        mock_SvnRepo.assert_called_once_with(
            name="unknown_svn",
            path="file://foo",
            trunk_head="trunk",
            trunk_tags="tags",
        )
        mock_GitSvnRepo.assert_called_once_with(
            name="unknown",
            path=os.getcwd(),
            svn_repo=mock_SvnRepo.return_value,
            ignore_revs=[],
        )
        mock_GitSvnRepo.return_value.init.assert_called_once_with(
            git_args=["-s"],
        )


class TestClone(unittest.TestCase):

    """Test the clone command."""

    @mock.patch('GitSvnHack.commands.GitSvnRepo')
    @mock.patch('GitSvnHack.commands.SvnRepo')
    def test_clone(self, mock_SvnRepo, mock_GitSvnRepo):
        """Test basic functionality of the clone command.

        This verifies that the command interacts with the Repo objects as
        expected.

        """
        args = [
            "file://foo", "git_foo",
            "--config-name", "foo_name", "--username", "joe",
            "-T", "bar_tr", "--tags", "bar_ta",
            "--ignore-revs", "22", "-r", "25",
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
            revision=25,
            git_args=["--username", "joe"],
        )

    @mock.patch('GitSvnHack.commands.GitSvnRepo')
    @mock.patch('GitSvnHack.commands.SvnRepo')
    def test_clone_minimal(self, mock_SvnRepo, mock_GitSvnRepo):
        """Test clone command with minimal arguments.

        This tests that the clone command can fill in some arguments.

        """
        args = [
            "file://foo", "-s",
        ]
        clone(args)
        mock_SvnRepo.assert_called_once_with(
            name="unknown_svn",
            path="file://foo",
            trunk_head="trunk",
            trunk_tags="tags",
        )
        mock_GitSvnRepo.assert_called_once_with(
            name="unknown",
            path="foo",
            svn_repo=mock_SvnRepo.return_value,
            ignore_revs=[],
        )
        mock_GitSvnRepo.return_value.clone.assert_called_once_with(
            revision=None,
            git_args=["-s"],
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
