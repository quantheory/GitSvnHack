#!/usr/bin/env python3

class Repo:
    """Repository class."""
    def __init__(self, name, path):
        self.name = name
        self.path = path

class LocalRepo(Repo):
    """Local repository class."""
    def __init__(self, name, path):
        Repo.__init__(self, name, path)

class SvnRepo(Repo):
    """Remote Subversion repository class."""
    def __init__(self, name, path):
        Repo.__init__(self, name, path)
