#!/usr/bin/env python3

class Repo:
    """Repository class."""
    def __init__(self, name, path):
        self.name = name
        self.path = path

class LocalRepo(Repo):
    """Local Git repository class."""
    def __init__(self, name, path):
        Repo.__init__(self, name, path)

class SvnRepo(Repo):
    """Remote Subversion repository class."""
    def __init__(self, name, path):
        Repo.__init__(self, name, path)

class GitSvnRepo(LocalRepo):
    """Local git-svn repository class."""
    def __init__(self, name, path, svn_repo):
        Repo.__init__(self, name, path)
        self.svn_repo = svn_repo
