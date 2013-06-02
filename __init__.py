#!/usr/bin/env python3
"""GitSvnHack is a wrapper that extends git-svn.

The goal of this package is to provide a Git interface for Subversion with
workarounds to handle svn:externals.

The package __init__.py is also the script to be run as git-svnhack.

"""

if __name__ == "__main__":
    from getopt import gnu_getopt
    import os
    import subprocess
    import sys
    # Handle being called with no arguments. Should really print an
    # svnhack-specific message here.
    if len(sys.argv) == 1:
        os.execvp("git", ["git", "svn"])
    # git-svn general options
    gen_shortopts = "A:q"
    gen_longopts = [
        "authors-file=", "authors-prog=",
        "quiet", "repack=", "repack-flags=",
    ]
    # git-svn init options; --no-metadata and --prefix are incompatible
    # with git-svnhack, which needs the metadata and might use --prefix
    # itself in the near future.
    init_shortopts = "T:t:b:s"
    init_longopts = [
        "shared=","template="
        "trunk=", "tags=", "branches=", "stdlayout",
        "use-svm-props", "use-svnsync-props",
        "rewrite-root=", "rewrite-uuid=",
        "username=", "no-minimize-url",
    ]
    # git-svn fetch options
    fetch_shortopts = "r:"
    fetch_longopts = [
        "revision=",
        "localtime", "parent", "ignore-paths=",
        "log-window-size=", "use-log-author",
    ]
    if sys.argv[1] == "clone":
        from GitSvnHack.repository import GitSvnRepo
        shortopts = ""+fetch_shortopts+init_shortopts+gen_shortopts
        longopts = ["preserve-empty-dirs", "placeholder-filename="]
        longopts.extend(gen_longopts)
        longopts.extend(init_longopts)
        longopts.extend(fetch_shortopts)
        opts, args = gnu_getopt(sys.argv[2:], shortopts, longopts)
    else:
        os.execvp("git", ["git", "svn"]+sys.argv[1:])
