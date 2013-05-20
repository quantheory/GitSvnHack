#!/usr/bin/env python3
"""Classes for interaction with Subversion and Git repositories."""

import subprocess

class Repo:
    """Repository class."""
    def __init__(self, name, path):
        self._name = name
        self._path = path
    def get_name(self):
        """Get the repository name."""
        return self._name
    def get_path(self):
        """Get the repository path."""
        return self._path

class SvnBranch:
    """Relative paths to a Subversion branch and its tags."""
    def __init__(self, head, tag_expr):
        self._head = head
        self._tags = tag_expr
    def get_head(self):
        return self._head
    def get_tag_expr(self):
        return self._tags

class SvnRepo(Repo):
    """Subversion repository class."""
    def __init__(self, name, path, trunk_head, trunk_tags):
        Repo.__init__(self, name, path)
        self._trunk_branch = SvnBranch(trunk_head, trunk_tags)
    def get_trunk_head(self):
        return Repo.get_path(self)+"/"+self._trunk_branch.get_head()
    def get_trunk_tag_expr(self):
        return Repo.get_path(self)+"/"+self._trunk_branch.get_tag_expr()

class GitRepo(Repo):
    """Git repository class."""
    def __init__(self, name, path):
        Repo.__init__(self, name, path)

class GitSvnRepo(GitRepo):
    """git-svn repository class."""
    def __init__(self, name, path, svn_repo):
        GitRepo.__init__(self, name, path)
        self.svn_repo = svn_repo
    def clone(self, stdout=None, stderr=None):
        subprocess.check_call(["git","svn","clone",
                               self.svn_repo.get_trunk_head(),
                               self.get_path()],
                              stdout=stdout, stderr=stderr)
