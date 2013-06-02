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
    # Also, add here the git-svnhack options "ignore-revs" and
    # "config-name".
    init_shortopts = "T:t:b:s"
    init_longopts = [
        "shared=","template="
        "trunk=", "tags=", "branches=", "stdlayout",
        "use-svm-props", "use-svnsync-props",
        "rewrite-root=", "rewrite-uuid=",
        "username=", "no-minimize-url",
        "ignore-revs", "config-name",
    ]
    # git-svn fetch options
    fetch_shortopts = "r:"
    fetch_longopts = [
        "revision=",
        "localtime", "parent", "ignore-paths=",
        "log-window-size=", "use-log-author",
    ]
    if sys.argv[1] == "clone":
        from GitSvnHack.repository import SvnRepo, GitSvnRepo
        shortopts = ""+fetch_shortopts+init_shortopts+gen_shortopts
        longopts = ["preserve-empty-dirs", "placeholder-filename="]
        longopts.extend(gen_longopts)
        longopts.extend(init_longopts)
        longopts.extend(fetch_shortopts)
        opts, args = gnu_getopt(sys.argv[2:], shortopts, longopts)
        # Here are all the options we need to fill in.
        opts_d = {
            "path": args[0],
            "name": None,
            "trunk": None,
            "trunk_tags": None,
            "ignore_revs": None,
        }
        # The git repo's path is used if given, or we grab it from the
        # end of the svn path.
        if len(args) > 1:
            opts_d["git_path"] = args[1]
        else:
            opts_d["git_path"] = opts_d["path"].split("/")[-1]

        # Loop over a copy of the options, removing values we handle as we
        # go.
        # Note that the first "-t" option has special significance; it is
        # assumed to hold the trunk tags.
        for opt in opts[:]:
            if "trunk" not in opts_d and \
               opt[0] == "-T" or opt[0] == "--trunk":
                opts_d["trunk"] = opt[1]
                opts.remove(opt)
            elif "trunk_tags" not in opts_d and \
                 opt[0] == "-t" or opt[0] == "--tags":
                opts_d["trunk_tags"] = opt[1]
                opts.remove(opt)
            elif "ignore_revs" not in opts_d and \
                 opt[0] == "--ignore-revs":
                opts_d["ignore_revs"] = opt[1]
                opts.remove(opt)
            elif "name" not in opts_d and \
                 opt[0] == "--config_name":
                opts_d["name"] = opt[1]
                opts.remove(opt)

        svn_repo = SvnRepo(
            name=opts_d["name"]+"_svn",
            path=opts_d["path"],
            trunk_head=opts_d["trunk"],
            trunk_tags=opts_d["trunk_tags"],
        )

        # Treate --ignore-revs as a comma-separated list.
        if opts_d["ignore_revs"] is None:
            ignore_revs = []
        else:
            ignore_revs = [int(i) for i in
                           opts_d["ignore_revs"].split(",")]

        git_svn_repo = GitSvnRepo(
            name=opts_d["name"],
            path=opts_d["git_path"],
            svn_repo=svn_repo,
            ignore_revs=ignore_revs,
        )

    else:
        os.execvp("git", ["git", "svn"]+sys.argv[1:])
