#!/usr/bin/env python3
"""Unit test module for parsedef.py"""

import os
import tempfile
import unittest

from GitSvnHack.parsedef import GitSvnDefParser


def write_temp_file(string):
    """Writes a string to a temporary file and returns the name."""
    fd,cfg_name = tempfile.mkstemp(text=True)
    with os.fdopen(fd, "w") as tmp_file:
        tmp_file.write(string)
    return cfg_name


class TestConfigBase(unittest.TestCase):
    """Base test class for parsedef tests."""

    def setUp(self):
        """Create a mock configuration file."""
        self.cfg_name = write_temp_file(self.file_string)

    def tearDown(self):
        """Remove configuration file."""
        os.remove(self.cfg_name)


class TestGitSvnDefParser(TestConfigBase):
    """Test the "GitSvnDefParser" class."""

    # Number of repos to test.
    repo_num = 2

    def setUp(self):
        """Create a mock GitSvnHack definition file."""

        def versioned_dicts(base_dict, n=self.repo_num):
            """Generate dictionary list with numbers appended to the
            value strings.
            E.g. versioned_dicts({"string": "test"},2) ==
            [{"string": "test1"},{"string": "test2"}]"""
            return [dict((key,val+str(i+1))
                         for key,val in base_dict.items())
                    for i in range(n)]

        # Template for dicts.
        repo_base_dict = {
            "name": "test_repo",
            "path": "/path/to/test_repo",
            "svn_url": "file://svn_origin",
            "svn_trunk_head": "trunk",
            "svn_trunk_tags": "trunk_tags/*",
            "ignore_revs": "",
        }

        # Use version_dicts to create several unique repo definitions.
        self.repo_dicts = versioned_dicts(repo_base_dict)
        # Generate a file section representing a repo for each
        # dict.
        file_sections = []
        for rd in self.repo_dicts:
            file_lines = [
                "["+rd["name"]+"]",
                "path = "+rd["path"],
                "svn_url = "+rd["svn_url"],
                "svn_trunk = "+rd["svn_trunk_head"]+
                ","+rd["svn_trunk_tags"],
                "ignore_revs = "+rd["ignore_revs"],
            ]
            file_sections.append("\n".join(file_lines))
        # Get file contents from joining all the sections.
        self.file_string = "\n".join(file_sections)
        # Parent class writes the file.
        super().setUp()
        # Finally, the actual object to test.
        self.git_svn_def = GitSvnDefParser()

    def test_get_repos(self):
        """Test the get_repos method on one file."""
        self.git_svn_def.read(self.cfg_name)
        repos = self.git_svn_def.get_repos()
        self.assertEqual(len(repos),len(self.repo_dicts))
        for repo,rd in zip(repos,self.repo_dicts):
            self.assertEqual(repo.name, rd["name"])
            self.assertEqual(repo.path, rd["path"])
            self.assertEqual(repo.svn_repo.name, "svn_"+rd["name"])
            self.assertEqual(repo.svn_repo.path, rd["svn_url"])
            self.assertEqual(repo.svn_repo.trunk_head,
                             rd["svn_url"]+"/"+rd["svn_trunk_head"])
            self.assertEqual(repo.svn_repo.trunk_tags,
                             rd["svn_url"]+"/"+rd["svn_trunk_tags"])
            self.assertCountEqual(repo.ignore_revs,
                                  [int(s) for s in rd["ignore_revs"]])

    def test_no_files(self):
        """Test that the get_repos method on zero files yields an
        empty list."""
        repos = self.git_svn_def.get_repos()
        self.assertEqual(repos,[])


if __name__ == "__main__":
    unittest.main()
