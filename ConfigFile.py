#!/usr/bin/env python3

from GitSvnHack.RepoClasses import SvnBranch, SvnRepo, GitSvnRepo
import re

# Regex for empty lines in a file (i.e. only whitespace or comments).
empty_line = re.compile("^\s*(#.*)?$")

# Regex for configuration line in a file.
# Currently does not allow end-of-line comments.
config_line = re.compile("^\s*(?P<var>\w+)\s*=\s*(?P<value>.*\S)\s*$")

class ConfigFile:
    """Class for general-purpose configuration files."""
    def __init__(self, path):
        self._path = path
    def get_path(self):
        """Return path that this object was created with."""
        return self._path
    def read_dict(self):
        """Read configuration file into a dictionary."""
        config_vars = dict()
        with open(self._path, "r") as my_file:
            for line in my_file:
                if empty_line.match(line):
                    continue
                re_match = config_line.match(line)
                if re_match:
                    config_vars[re_match.group("var")] = \
                        re_match.group("value")
                else:
                    # Unrecognized line, so raise exception.
                    raise ValueError( \
                        "Unparseable line in config file.")
        return config_vars

class GitSvnDefFile:
    """Class for files defining the Subversion to Git translation."""
    def __init__(self, path):
        self._cfg_file = ConfigFile(path)
    def read_repo(self):
        """Read definition file into a repository object."""
        definition = self._cfg_file.read_dict()
        trunk,trunk_tags = definition["svn_trunk"].split(",")
        svn_repo = SvnRepo( "svn_"+definition["name"],
                            definition["svn_url"],
                            SvnBranch(trunk, trunk_tags) )
        repo = GitSvnRepo( definition["name"],
                           definition["path"],
                           svn_repo )
        return repo
