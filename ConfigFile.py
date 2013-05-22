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
        """Read definition file into repository objects (Currently
        only handles one definition in one file)."""
        self._cfg_parse.read(self._path)
        repo_name = self._cfg_parse.sections()[0]
        section_dict = self._cfg_parse[repo_name]
        trunk,trunk_tags = section_dict["svn_trunk"].split(",")
        svn_repo = SvnRepo( "svn_"+repo_name,
                            section_dict["svn_url"],
                            trunk, trunk_tags)
        repo = GitSvnRepo( repo_name,
                           section_dict["path"],
                           svn_repo )
        return [repo]
