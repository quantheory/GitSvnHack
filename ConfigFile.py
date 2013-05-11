#!/usr/bin/env python3

from SvnHack.RepoClasses import SvnRepo, GitSvnRepo
import re

# Regex for empty lines in a file (i.e. only whitespace or comments).
empty_line = re.compile("^\s*(#.*)$")

# Regex for configuration line in a file.
# Currently does not allow end-of-line comments.
config_line = re.compile("^\s*(?P<var>\w+)\s*=\s*(?P<value>.*\S)\s*$")

class ConfigFile():
    """Class for general-purpose configuration files."""
    def __init__(self, file_path):
        self._path = file_path
    def path(self):
        return self._path
    def read_dict(self):
        config_vars = dict()
        with open(self._path, "r") as my_file:
            for line in my_file:
                if empty_line.match(line):
                    continue
                re_match = config_line.match(line)
                if re_match:
                    re_match.group("var")
                    config_vars[re_match.group("var")] = \
                        re_match.group("value")
                else:
                    # Unrecognized line, so raise exception.
                    raise ValueError( \
                        "Unparseable line in config file.")
        return config_vars

class GitSvnDefFile():
    """Class for files defining the Subversion to Git translation."""
    def __init__(self, file_path):
        self._cfg_file = ConfigFile(file_path)
    def read_repo(self):
        definition = self._cfg_file.read_dict()
        svn_repo = SvnRepo( "svn_"+definition["name"],
                            definition["svnurl"])
        repo = GitSvnRepo( definition["name"],
                           definition["path"],
                           svn_repo )
        return repo
