#!/usr/bin/env python3
"""Classes corresponding to configuration files."""

from GitSvnHack.RepoClasses import SvnBranch, SvnRepo, GitSvnRepo

from configparser import ConfigParser, ExtendedInterpolation

class GitSvnDefFile:
    """Class for files defining the Subversion to Git translation."""
    def __init__(self, path):
        self._path = path
        self._cfg_parse \
            = ConfigParser(delimiters=('='),
                           comment_prefixes=('#'),
                           empty_lines_in_values=False,
                           interpolation=ExtendedInterpolation())
    def get_repos(self):
        """Read definition file into repository objects."""
        self._cfg_parse.read(self._path)
        repo_names = self._cfg_parse.sections()
        repos = []
        for name in repo_names:
            section_dict = self._cfg_parse[name]
            trunk,trunk_tags = section_dict["svn_trunk"].split(",")
            svn_repo = SvnRepo( "svn_"+name,
                                section_dict["svn_url"],
                                trunk, trunk_tags)
            repos.append( GitSvnRepo( name,
                                      section_dict["path"],
                                      svn_repo)
                      )
        return repos
