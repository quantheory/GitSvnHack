#!/usr/bin/env python3

class Repo:
    """Repository class."""
    def __init__(self, name):
        self.name = name

class LocalRepo(Repo):
    """Local repository class."""
    def __init__(self, name, path):
        Repo.__init__(self, name)

class SvnRepo(Repo):
    """Remote Subversion repository class."""
    def __init__(self, name):
        Repo.__init__(self, name)
