#!/usr/bin/env python3

from SvnHack.RepoClasses import SvnRepo, GitSvnRepo
import re

# Regex for empty lines in a file (i.e. only whitespace or comments).
empty_line = re.compile("^\s*(#.*)$")

# Regex for configuration line in a file.
# Currently does not allow end-of-line comments.
config_line = re.compile("^\s*(?P<var>\w+)\s*=\s*(?P<value>.*\S)\s*$")

class ConfigFile():
    """Class for files defining the Subversion to Git translation."""
    def __init__(self, file_path):
        self.path = file_path
    def read_repo(self):
        config_values = dict()
        with open(self.path, "r") as my_file:
            for line in my_file:
                if empty_line.match(line):
                    continue
                re_match = config_line.match(line)
                if re_match:
                    re_match.group("var")
                    config_values[re_match.group("var")] = \
                        re_match.group("value")
                else:
                    # Unrecognized line, so exit.
                    return
        svn_repo = SvnRepo( "svn_"+config_values["name"],
                            config_values["svnurl"])
        repo = GitSvnRepo( config_values["name"],
                           config_values["path"],
                           svn_repo )
        return repo
