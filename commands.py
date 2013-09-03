#!/usr/bin/env python3
"""Main commands for git-svnhack.

The following git-svn commands have wrappers:

clone

There's also a "default" command, which will pass any other command to
git-svn.

"""

from GitSvnHack.repository import SvnRepo, GitSvnRepo

from getopt import gnu_getopt
from functools import wraps
from itertools import chain
import os

class ParsedArgs:

    """Container for the passed arguments, after option parsing.

    Public methods:
    get_string_list - Get all arguments in a list of strings.
    pop_any_opt_of - Pop the value of the first option match.
    get_any_opt_of - Get the value of the first option match.
    pop_arg - Pop the first argument.

    """

    def __init__(self, opts, args):
        self._opts = opts
        self._args = args

    def get_string_list(self):
        """Collapse parsed arguments back into a list of strings."""
        is_valid_argument = lambda x: x is not None and x != ""
        flattened_opts = chain.from_iterable(self._opts)
        arg_list = list(filter(is_valid_argument, flattened_opts))
        arg_list += self._args
        return arg_list

    # Use this as a decorator to handle empty strings in return values.
    def _fix_empty_opt(function):
        @wraps(function)
        def fixed_function(*args, **kwargs):
            opt = function(*args, **kwargs)
            if opt != "":
                return opt
            else:
                return True
        return fixed_function

    @_fix_empty_opt
    def pop_any_opt_of(self, *opts_to_pop):
        """Pop the first option matching one of the arguments.

        Outputs are True for binary arguments, the string for a string
        argument, and None for a non-present argument.

        """

        pop_operation = lambda i: self._opts.pop(i)[1]

        return self._apply_to_any_of(pop_operation, *opts_to_pop)

    @_fix_empty_opt
    def get_any_opt_of(self, *opts_to_get):
        """Get the first option matching one of the arguments.

        Outputs are True for binary arguments, the string for a string
        argument, and None for a non-present argument.

        """

        get_operation = lambda i: self._opts[i][1]

        return self._apply_to_any_of(get_operation, *opts_to_get)

    def _apply_to_any_of(self, find_operation, *opts_to_find):

        for i in range(len(self._opts)):
            if self._opts[i][0] in opts_to_find:
                return find_operation(i)

        return None

    # The _fix_empty_opt function does not do anything meaningful outside
    # of this class definition.
    del _fix_empty_opt

    def pop_arg(self):
        """Pop the first non-option argument from the list."""
        if len(self._args) > 0:
            return self._args.pop(0)
        else:
            return None

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

    def copy(self):
        """Return an OptSpec that's a copy of this one."""
        return OptSpec(self._shortopts, self._longopts)

    def parse(self, args):
        """Parse argument list with gnu_getopts."""
        return gnu_getopt(args, self._shortopts, self._longopts)

    def __iadd__(self, other):
        """Concatenate options into this OptSpec."""
        self._shortopts += other._shortopts
        self._longopts += other._longopts
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
    opt_spec = _init_opts+_gen_opts
    parsed_args = ParsedArgs(*opt_spec.parse(arguments))

    # Dictionary of options to be passed.
    opts_d = dict()

    opts_d["path"] = parsed_args.pop_arg()
    opts_d["git_path"] = parsed_args.pop_arg()

    # If the git repo's path is not given, use current working directory.
    if opts_d["git_path"] is None:
        opts_d["git_path"] = os.getcwd()

    # Get parsed arguments into our dictionary.
    # Note that the first "-t" option has special significance; it is
    # assumed to hold the trunk tags.

    opts_d["trunk"] = parsed_args.pop_any_opt_of("-T", "--trunk")
    opts_d["trunk_tags"] = parsed_args.pop_any_opt_of("-t", "--tags")
    opts_d["ignore_revs"] = parsed_args.pop_any_opt_of("--ignore-revs")
    opts_d["name"] = parsed_args.pop_any_opt_of("--config-name")
    if parsed_args.get_any_opt_of("-s", "--stdlayout"):
        opts_d["trunk"] = "trunk"
        opts_d["trunk_tags"] = "tags"

    # Make the "--config-name" argument optional.
    if opts_d["name"] is None:
        opts_d["name"] = "unknown"

    # Treate --ignore-revs as a comma-separated list.
    if opts_d["ignore_revs"] is not None:
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
        git_args=parsed_args.get_string_list(),
    )


def clone(arguments):
    """GitSvnHack clone command."""
    opt_spec = _clone_opts+_fetch_opts+_init_opts+_gen_opts
    parsed_args = ParsedArgs(*opt_spec.parse(arguments))

    # Dictionary of options to be passed.
    opts_d = dict()

    opts_d["path"] = parsed_args.pop_arg()
    opts_d["git_path"] = parsed_args.pop_arg()

    # If the git repo's path is not given, grab it from the end of the svn
    # URL.
    if opts_d["git_path"] is None:
        opts_d["git_path"] = opts_d["path"].split("/")[-1]

    # Get parsed arguments into our dictionary.
    # Note that the first "-t" option has special significance; it is
    # assumed to hold the trunk tags.

    opts_d["trunk"] = parsed_args.pop_any_opt_of("-T", "--trunk")
    opts_d["trunk_tags"] = parsed_args.pop_any_opt_of("-t", "--tags")
    opts_d["ignore_revs"] = parsed_args.pop_any_opt_of("--ignore-revs")
    opts_d["revision"] = parsed_args.pop_any_opt_of("-r", "--revision")
    opts_d["name"] = parsed_args.pop_any_opt_of("--config-name")
    if parsed_args.get_any_opt_of("-s", "--stdlayout"):
        opts_d["trunk"] = "trunk"
        opts_d["trunk_tags"] = "tags"

    # Make the "--config-name" and "-r" arguments optional.
    if opts_d["name"] is None:
        opts_d["name"] = "unknown"
    if opts_d["revision"] is not None:
        opts_d["revision"] = int(opts_d["revision"])

    # Treate --ignore-revs as a comma-separated list.
    if opts_d["ignore_revs"] is not None:
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
        revision=opts_d["revision"],
        git_args=parsed_args.get_string_list(),
    )

def default(arguments):
    """"Default command that simply calls git svn with all arguments."""
    os.execvp("git", ["git", "svn"]+arguments)
