#!/usr/bin/env python3

class Repo:
    """The SvnHack representation of a repository."""
    def __init__(self, name):
        self.name = name

class SvnRepo(Repo):
    """The SvnHack representation of a remote Subversion repository."""
    def __init__(self, name):
        Repo.__init__(self, name)
