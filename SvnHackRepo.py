#!/usr/bin/env python3

class SvnHackRepo:
    """The SvnHack representation of a repository."""
    def __init__(self, name):
        self.name = name

class SvnRepo(Repo):
    """A representation of a remote Subversion repository."""
    def __init__(self, name):
        
