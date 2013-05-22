#!/usr/bin/env python3
"""Classes for interaction with Subversion and Git repositories."""

import subprocess

class Repo:
    """Repository class."""
    def __init__(self, name, path, **args):
        self._name = name
        self._path = path
        super().__init__(**args)
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
    def __init__(self, trunk_head, trunk_tags, **args):
        self._trunk_branch = SvnBranch(trunk_head, trunk_tags)
        super().__init__(**args)
    def get_trunk_head(self):
        """Return URL for the repo's trunk."""
        return Repo.get_path(self)+"/"+self._trunk_branch.get_head()
    def get_trunk_tag_expr(self):
        """Return expression for the URLs corresponding to trunk
        tags."""
        return Repo.get_path(self)+"/"+self._trunk_branch.get_tag_expr()
    def get_trunk(self):
        """Return entire trunk branch."""
        return self._trunk_branch

class GitRepo(Repo):
    """Git repository class."""
    def __init__(self, **args):
        super().__init__(**args)

class GitSvnRepo(GitRepo):
    """git-svn repository class."""
    def __init__(self, svn_repo, **args):
        self.svn_repo = svn_repo
        super().__init__(**args)
    def clone(self, stdout=None, stderr=None):
        """Use "git svn clone" to clone the repo."""
        svn_trunk = self.svn_repo.get_trunk()
        subprocess.check_call(["git","svn","clone",
                               self.svn_repo.get_path(),
                               "-T",svn_trunk.get_head(),
                               self.get_path()],
                              stdout=stdout, stderr=stderr)
