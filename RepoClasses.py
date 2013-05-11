#!/usr/bin/env python3

class Repo:
    """Repository class."""
    def __init__(self, name, path):
        self._name = name
        self._path = path
    def name(self):
        return self._name
    def path(self):
        return self._path

class SvnBranch:
    """Relative paths to a Subversion branch and its tags."""
    def __init__(self, head, tag_expr):
        self._head = head
        self._tags = tag_expr
    def head(self):
        return self._head
    def tag_expr(self):
        return self._tags

class SvnRepo(Repo):
    """Remote Subversion repository class."""
    def __init__(self, name, path, trunk):
        Repo.__init__(self, name, path)
        self._trunk_branch = trunk
    def trunk(self):
        return Repo.path(self)+"/"+self._trunk_branch.head()
    def trunk_tag_expr(self):
        return Repo.path(self)+"/"+self._trunk_branch.tag_expr()

class GitRepo(Repo):
    """Local Git repository class."""
    def __init__(self, name, path):
        Repo.__init__(self, name, path)

class GitSvnRepo(GitRepo):
    """Local git-svn repository class."""
    def __init__(self, name, path, svn_repo):
        GitRepo.__init__(self, name, path)
        self.svn_repo = svn_repo
