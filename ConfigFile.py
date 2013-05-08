#!/usr/bin/env python3

from SvnHack.RepoClasses import GitSvnRepo

class ConfigFile():
    """Class for files defining the Subversion to Git translation."""
    def __init__(self, file_name):
        self.name = file_name
