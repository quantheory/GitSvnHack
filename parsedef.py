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
        "Read a definition file."
        self._cfg_parse.read(path)

    def write(self, path):
        "Write out the definition file."
        with open(path, "w+") as def_file:
            self._cfg_parse.write(def_file)

    def get_repos(self):
        """Read definition file into repository objects."""
        repo_names = self._cfg_parse.sections()
        repos = []
        for name in repo_names:
            repo_dict = self._cfg_parse[name]
            trunk_head, trunk_tags = repo_dict["svn_trunk"].split(",")
            svn_repo = SvnRepo(name="svn_"+name,
                               path=repo_dict["svn_url"],
                               trunk_head=trunk_head,
                               trunk_tags=trunk_tags)
            ignore_revs = [int(s) for s in
                           repo_dict["ignore_revs"].split(",")]
            repos.append(
                GitSvnRepo(name=name,
                           path=repo_dict["path"],
                           ignore_revs=ignore_revs,
                           svn_repo=svn_repo)
            )
        return repos

    def set_repos(self, repos):
        "Set a list of repos whose definitions will be written."
        for repo in repos:
            self._cfg_parse.add_section(repo.name)
            self._cfg_parse.set(
                repo.name, "svn_trunk",
                ",".join([repo.svn_repo.trunk_head,
                          repo.svn_repo.trunk_tags])
            )
            self._cfg_parse.set(repo.name, "svn_url", repo.svn_repo.path)
            self._cfg_parse.set(repo.name, "path", repo.path)
            self._cfg_parse.set(repo.name, "ignore_revs",
                                ",".join(str(i) for i in repo.ignore_revs))
