#!/usr/bin/env python3
"""Main commands for git-svnhack.

The following git-svn commands have wrappers:

clone

There's also a "default" command, which will pass any other command to
git-svn.

"""

from GitSvnHack.repository import SvnRepo, GitSvnRepo

from getopt import gnu_getopt
from itertools import chain
import os


class OptSpec:

    """Option specification.

    Public instance variables:
    shortopts - Short form options.
    longopts - Long form options.

    Public methods:
    copy - Copy this OptSpec object.
    parse - Parse an argument list.
    __iadd__/__add__ - Two OptSpec objects can be combined.

    """

    def __init__(self, shortopts, longopts):
        self._shortopts = shortopts
        self._longopts = longopts[:]

    @property
    def shortopts(self):
        """Getopts-style specification of short options."""
        return self._shortopts

    @property
    def longopts(self):
        """Getopts-style specification of long options."""
        return self._longopts

    def copy(self):
        return OptSpec(self.shortopts, self.longopts)

    def parse(self, args):
        """Parse argument list with gnu_getopts."""
        return gnu_getopt(args, self._shortopts, self._longopts)

    def __iadd__(self, other):
        """Concatenate options into this OptSpec."""
        self._shortopts += other.shortopts
        self._longopts += other.longopts
        return self

    def __add__(self, other):
        "Combine options into a new OptSpec."
        ret = self.copy()
        ret += other
        return ret


# git-svn general options
_gen_opts = OptSpec("A:q", [
    "authors-file=", "authors-prog=",
    "quiet", "repack=", "repack-flags=",
])

# git-svn init options; --no-metadata and --prefix are incompatible
# with git-svnhack, which needs the metadata and might use --prefix
# itself in the near future.
# Also, add here the git-svnhack options "ignore-revs" and
# "config-name".
_init_opts = OptSpec("T:t:b:s", [
    "shared=","template="
    "trunk=", "tags=", "branches=", "stdlayout",
    "use-svm-props", "use-svnsync-props",
    "rewrite-root=", "rewrite-uuid=",
    "username=", "ignore-paths=", "no-minimize-url",
    "ignore-revs=", "config-name=",
])

# git-svn fetch options
_fetch_opts = OptSpec("r:", [
    "revision=",
    "localtime", "parent", "ignore-paths=",
    "log-window-size=", "use-log-author",
])

# git-svn clone options
_clone_opts = OptSpec("", [
    "preserve-empty-dirs", "placeholder-filename="
])

def init(arguments):
    """GitSvnHack init command."""
    opts, args = (_init_opts+_gen_opts).parse(arguments)
    # Dictionary of options to be passed.
    opts_d = {
        "path": args[0],
    }
    # The git repo's path is used if given, or use current working
    # directory.
    if len(args) > 1:
        opts_d["git_path"] = args[1]
    else:
        opts_d["git_path"] = os.getcwd()

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
             opt[0] == "--config-name":
            opts_d["name"] = opt[1]
            opts.remove(opt)
        elif "trunk" not in opts_d and \
             opt[0] == "-s" or opt[0] == "--stdlayout":
            opts_d["trunk"] = "trunk"
            if "trunk_tags" not in opts_d:
                opts_d["trunk_tags"] = "tags"

    # Make the "--config-name" argument optional.
    opts_d.setdefault("name", "unknown")

    # Treate --ignore-revs as a comma-separated list.
    if "ignore_revs" in opts_d:
        ignore_revs = [int(i) for i in
                       opts_d["ignore_revs"].split(",")]
    else:
        ignore_revs = []

    svn_repo = SvnRepo(
        name=opts_d["name"]+"_svn",
        path=opts_d["path"],
        trunk_head=opts_d["trunk"],
        trunk_tags=opts_d["trunk_tags"],
    )

    git_svn_repo = GitSvnRepo(
        name=opts_d["name"],
        path=opts_d["git_path"],
        svn_repo=svn_repo,
        ignore_revs=ignore_revs,
    )

    # Pass git_args by flattening the list with chain.from_iterable,
    # then filtering out the None values.
    git_svn_repo.init(
        git_args=list(filter(lambda x: x is not None and x != "",
                             chain.from_iterable(opts))),
    )


def clone(arguments):
    """GitSvnHack clone command."""
    opts, args = (_clone_opts+_fetch_opts+
                  _init_opts+_gen_opts).parse(arguments)
    # Dictionary of options to be passed.
    opts_d = {
        "path": args[0],
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
        elif "revision" not in opts_d and \
             opt[0] == "--revision" or opt[0] == "-r":
            opts_d["revision"] = opt[1]
            opts.remove(opt)
        elif "name" not in opts_d and \
             opt[0] == "--config-name":
            opts_d["name"] = opt[1]
            opts.remove(opt)
        elif "trunk" not in opts_d and \
             opt[0] == "-s" or opt[0] == "--stdlayout":
            opts_d["trunk"] = "trunk"
            if "trunk_tags" not in opts_d:
                opts_d["trunk_tags"] = "tags"

    # Make the "--config-name" and "-r" arguments optional.
    opts_d.setdefault("name", "unknown")
    if "revision" in opts_d:
        revision = int(opts_d["revision"])
    else:
        revision = None

    # Treate --ignore-revs as a comma-separated list.
    if "ignore_revs" in opts_d:
        ignore_revs = [int(i) for i in
                       opts_d["ignore_revs"].split(",")]
    else:
        ignore_revs = []

    svn_repo = SvnRepo(
        name=opts_d["name"]+"_svn",
        path=opts_d["path"],
        trunk_head=opts_d["trunk"],
        trunk_tags=opts_d["trunk_tags"],
    )

    git_svn_repo = GitSvnRepo(
        name=opts_d["name"],
        path=opts_d["git_path"],
        svn_repo=svn_repo,
        ignore_revs=ignore_revs,
    )

    # Pass git_args by flattening the list with chain.from_iterable,
    # then filtering out the None values.
    git_svn_repo.clone(
        revision=revision,
        git_args=list(filter(lambda x: x is not None and x != "",
                             chain.from_iterable(opts))),
    )

def default(arguments):
    """"Default command that simply calls git svn with all arguments."""
    os.execvp("git", ["git", "svn"]+arguments)
