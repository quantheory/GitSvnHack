#!/usr/bin/env python3
"""Classes corresponding to configuration files."""

from configparser import ConfigParser, ExtendedInterpolation

from GitSvnHack.repository import SvnBranch, SvnRepo, GitSvnRepo


class GitSvnDefParser:
    """Class for files defining the Subversion to Git translation."""
    def __init__(self):
        self._cfg_parse = ConfigParser(
            delimiters=('='),
            comment_prefixes=('#'),
            empty_lines_in_values=False,
            interpolation=ExtendedInterpolation()
        )

    def read(self, path):
        self._cfg_parse.read(path)

    def get_repos(self):
        """Read definition file into repository objects."""
        repo_names = self._cfg_parse.sections()
        repos = []
        for name in repo_names:
            repo_dict = self._cfg_parse[name]
            trunk_head,trunk_tags = repo_dict["svn_trunk"].split(",")
            svn_repo = SvnRepo(name="svn_"+name,
                               path=repo_dict["svn_url"],
                               trunk_head=trunk_head,
                               trunk_tags=trunk_tags)
            repos.append(
                GitSvnRepo(name=name,
                           path=repo_dict["path"],
                           svn_repo=svn_repo)
            )
        return repos
