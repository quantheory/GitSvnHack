#!/usr/bin/env python3
"""Main commands for git-svnhack.

The following git-svn commands have wrappers:

clone

There's also a "default" command, which will pass any other command to
git-svn.

"""

import os

def default(args):
    """"Default command that simply calls git svn with all arguments."""
    os.execvp("git", ["git", "svn"]+args)
