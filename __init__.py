#!/usr/bin/env python3
"""GitSvnHack is a wrapper that extends git-svn.

The goal of this package is to provide a Git interface for Subversion with
workarounds to handle svn:externals.

The package __init__.py is also the script to be run as git-svnhack.

"""

if __name__ == "__main__":
    import GitSvnHack.commands
    import os
    import sys
    # Handle being called with no arguments. Should really print an
    # svnhack-specific message here.
    if len(sys.argv) == 1:
        os.execvp("git", ["git", "svn"])
    if sys.argv[1] == "init":
        commands.init(sys.argv[2:])
    if sys.argv[1] == "clone":
        commands.clone(sys.argv[2:])
    else:
        commands.default(sys.argv[1:])
