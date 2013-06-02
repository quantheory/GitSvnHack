#!/usr/bin/env python3
"""Classes for interaction with Subversion and Git repositories.

Classes:
Repo - Repository base class.
SvnBranch - Identifies a branch in a Subversion repository.
SvnRepo - Subversion repository class.
GitRepo - Git repository class.
GitSvnRepo - git-svn repository class.

"""

import re
import subprocess


# Regular expression used to get the current revision from "svn info".
# Also works for "git svn info".
_svn_info_regex = re.compile("Revision: (?P<revision>\d+)")


class Repo:

    """Base class for all repository objects.

    Public instance variables:
    name - The repository's name.
    path - The repository's path or URL.

    """

    def __init__(self, *, name, path, **args):
        """Construct a Repo using identifying strings.

        Keyword arguments:
        name - Sets the "name" attribute.
        path - Sets the "path" attribute.

        """
        self._name = name
        self._path = path
        super().__init__(**args)

    @property
    def name(self):
        """An arbitrary name you can give to the repository."""
        return self._name

    @property
    def path(self):
        """The path or URL that will be used to access the repository."""
        return self._path


class SvnBranch:

    """Provides relative paths to a Subversion branch and its tags.

    Public instance variables:
    head - Relative path to the branch's head.
    tags - Glob expression for relative paths to the branch's tags.

    """

    def __init__(self, head, tags):
        """Set the strings used to locate the branch.

        Keyword arguments:
        head - Sets the "head" attribute.
        tags - Sets the "tags" attribute.

        """
        self._head = head
        self._tags = tags

    @property
    def head(self):
        """Path to the head of a branch.

        This is relative to the root directory of a project's space on the
        repository.

        """
        return self._head

    @property
    def tags(self):
        """Expression used to find branch tags.

        This expression is relative to the root directory of the project.
        It should be comprehensible to git-svn, which means that it can
        only use globs and brace expansion to specify multiple paths.

        """
        return self._tags


class SvnRepo(Repo):

    """Provides information about a Subversion repository.

    Strictly speaking, this class is not intended to describe an entire
    Subversion repository containing multiple projects, but instead is for
    a single project's space. It also has no concept of a working
    copy; all information and methods apply only to the repository itself.

    This class inherits from the "Repo" class, and extends the init method
    by adding more information about a project. The "path" attribute
    represents the URL used to locate the project's space on the
    repository.

    Public instance variables:
    trunk_head - URL for the head of the repo's trunk
    trunk_tags - An expression used to find the repo's trunk tags.
    trunk_branch - An SvnBranch object corresponding to the project's
                   trunk.

    Public methods:
    get_current_revision - Query the latest revision number.

    There are also some methods used to interact with the repository, but
    they are fragile and really just meant for testing.

    Repository interaction methods (testing only):
    create - Create a local repository corresponding to this object.
    trunk_import - Import a file to the trunk.
    trunk_rm - Remove a file from the trunk.
    make_trunk_tag - Tag the current trunk by making a copy in the trunk
                     tags directory.

    """

    def __init__(self, *, trunk_head, trunk_tags, **args):
        """Extend the Repo constructor with trunk information.

        New keyword arguments:
        trunk_head - Trunk head location, relative to the "path" argument.
        trunk_tags - Git-svn-compatible glob expression to find trunk_tags,
                     relative to the "path" argument.

        Other keyword arguments are passed to the Repo constructor. The
        "path" argument should contain the URL used to access the
        repository.

        """
        self._trunk_branch = SvnBranch(trunk_head, trunk_tags)
        super().__init__(**args)

    @property
    def trunk_head(self):
        """The full URL to the head of the project's trunk."""
        return self.path+"/"+self._trunk_branch.head

    @property
    def trunk_tags(self):
        """Glob expression for URLs corresponding to the trunk's tags."""
        return self.path+"/"+self._trunk_branch.tags

    @property
    def trunk_branch(self):
        """SvnBranch object corresponding to the project's trunk."""
        return self._trunk_branch

    def get_current_revision(self):
        """Gets the latest revision number from the repository."""

        # Parse the output of "svn info" to get the current revision.
        svn_info = subprocess.check_output(
            ["svn", "info", self.path],
            universal_newlines=True,
        )
        return int(_svn_info_regex.search(svn_info).group("revision"))

    def create(self):
        """Create the repository.

        Should only be used for testing.

        """
        local_path = re.sub("^file://", "", self.path)
        subprocess.check_call(["svnadmin", "create", local_path])

        # Create top level directories (trunk_head, then trunk_tags).
        subprocess.check_call(
            ["svn", "mkdir", self.trunk_head, "-q", \
             "-m", "Creating trunk directory."]
        )
        # This is to ensure we only create until the first "*" or brace
        # expansion. A smarter version would also create all directories
        # in braces.
        my_tags_dir = self.trunk_tags
        glob_part_idx = my_tags_dir.find("*")
        if glob_part_idx >= 0:
            my_tags_dir = my_tags_dir[:glob_part_idx]
        glob_part_idx = my_tags_dir.find("{")
        if glob_part_idx >= 0:
            my_tags_dir = my_tags_dir[:glob_part_idx]
        subprocess.check_call(
            ["svn", "mkdir", my_tags_dir, "-q", \
             "-m", "Creating trunk tags directory."]
        )

    def trunk_import(self, file_path, repo_path, msg="Importing file."):
        """Import a file into the repo's trunk.

        Accepts a path relative to the trunk's root.

        Should only be used for testing.

        """
        subprocess.check_call(
            ["svn", "import", file_path, self.trunk_head+"/"+repo_path,
             "-q", "-m", msg]
        )

    def trunk_rm(self, repo_path, msg="Removing file."):
        """Remove a file from the repo's trunk.

        Accepts a path relative to the trunk's root.

        Should only be used for testing.

        """
        subprocess.check_call(
            ["svn", "rm", self.trunk_head+"/"+repo_path,
             "-q", "-m", msg]
        )

    def make_trunk_tag(self, tag_name, msg="Making tag."):
        """Copy the trunk into "tag_name" in the trunk_tags directory.

        Should only be used for testing.

        """
        # Deal with globs and such, as above.
        my_tags_dir = self.trunk_tags
        glob_part_idx = my_tags_dir.find("*")
        if glob_part_idx >= 0:
            my_tags_dir = my_tags_dir[:glob_part_idx]
        glob_part_idx = my_tags_dir.find("{")
        if glob_part_idx >= 0:
            my_tags_dir = my_tags_dir[:glob_part_idx]
        # Copy to the tag name.
        subprocess.check_call(
            ["svn", "cp", self.trunk_head, my_tags_dir+"/"+tag_name,
             "-q", "-m", msg]
        )


class GitRepo(Repo):

    """Class to describe and manipulate Git repositories.

    This class extends the Repo class with git-specific operations.
    This is expected to be useful in the future, but currently has no well-
    defined purpose, so it is a really just a stub.

    Neither this class nor GitSvnRepo check conditions closely yet, e.g. to
    detect whether a repository already exists before running init or
    clone.

    Public methods:
    init - Create the repository.

    """

    def __init__(self, **args):
        """Wrap the Repo constructor."""
        super().__init__(**args)

    def init(self, **args):
        """Initialize a Git repository.

        This creates an empty repository at the path specified during this
        object's creation.

        Any keyword arguments provided are passed to
        subprocess.check_call().

        """
        # TODO: Perhaps this function should also write the repository name
        # to ".git/description"?
        subprocess.check_call(
            ["git", "init", self.path],
            **args
        )


class GitSvnRepo(GitRepo):

    """Class to describe and manipulate git-svn repositories.

    Extend GitRepo with information about an upstream Subversion
    repository, and methods that interact with git-svn.

    git-svn repositories with multiple Subversion remotes are currently not
    handled.

    Public instance variables:
    svn_repo - An SvnRepo object corresponding to the upstream repo.

    Public methods:
    get_svn_revision - Get the current upstream Subversion revision.
    clone - Use "git svn clone" to create this repository.
    rebase - Use "git svn rebase" to update this repository.

    """

    def __init__(self, *, svn_repo, ignore_revs=(), **args):
        """Extend the GitRepo constructor by accepting a SvnRepo.

        New keyword arguments:
        svn_repo - An SvnRepo object defining the upstream Subversion
                   repository.
        ignore_revs - A sequence containing upstream revisions to ignore.
                      Defaults to an empty tuple.

        """
        self._svn_repo = svn_repo
        self._ignore_revs = sorted(ignore_revs)
        super().__init__(**args)

    @property
    def svn_repo(self):
        """Subversion repository upstream of this GitSvnRepo."""
        return self._svn_repo

    def get_svn_revision(self, **args):
        """Get the Subversion revision upstream of the working copy.

        All keyword arguments are passed to subprocess.check_output().
        If given, stdout will be stripped out, since that allows you to
        specify the same arguments here as for the other methods in this
        class.

        """
        # Parse the output of "git svn info" to get the current revision.
        # It's not clear whether we should really do this, or use git
        # rev-list. It's better to script around plumbing rather than
        # porcelain, but the nature of this project requires making an
        # exception for git-svn anyway.
        #
        # Since we have to capture this output, strip stdout from args we
        # were given.
        output_args = args.copy()
        if "stdout" in output_args:
            del output_args["stdout"]
        git_svn_info = subprocess.check_output(
            ["git", "svn", "info"],
            cwd=self.path,
            universal_newlines=True,
            **output_args
        )

        return int(_svn_info_regex.search(git_svn_info).group("revision"))

    def clone(self, revision=None, **args):
        """Create a Git clone of a Subversion repository with git-svn.

        Arguments:
        revision - The latest revision to use; everything up to this point
                   will be cloned.

        Any additional keyword arguments provided are passed to
        subprocess.check_call().

        """
        rebase_revision = None
        if len(self._ignore_revs) > 0:
            if revision is not None:
                if revision > self._ignore_revs[0]:
                    clone_revision = self._ignore_revs[0] - 1
                    rebase_revision = revision
                else:
                    clone_revision = revision
            else:
                clone_revision = self._ignore_revs[0] - 1
                rebase_revision = "HEAD"
        else:
            if revision is not None:
                clone_revision = revision
            else:
                clone_revision = "HEAD"
        svn_trunk = self.svn_repo.trunk_branch
        subprocess.check_call(
            ["git", "svn", "clone", self.svn_repo.path,
             "-T", svn_trunk.head, "-t", svn_trunk.tags,
             "-r", "BASE:"+str(clone_revision), self.path],
            **args
        )
        if rebase_revision is not None:
            self.rebase(revision=rebase_revision, **args)

    def rebase(self, revision=None, **args):
        """Update this repository from its Subversion upstream.

        Arguments:
        revision - The revision to rebase onto. Must be between the current
                   revision and HEAD. Defaults to HEAD.

        Any additional keyword arguments provided are passed to
        subprocess.check_call().

        """
        svn_trunk = self.svn_repo.trunk_branch

        next_revision = self.get_svn_revision(**args) + 1

        for irev in self._ignore_revs:
            if irev < next_revision:
                continue
            if irev == next_revision:
                next_revision += 1
                continue
            subprocess.check_call(
                ["git", "svn", "fetch",
                 "-r", str(next_revision)+":"+str(irev)],
                cwd=self.path,
                **args
            )
            next_revision = irev+1

        if revision is None:
            revision="HEAD"
        subprocess.check_call(
            ["git", "svn", "fetch",
             "-r", str(next_revision)+":"+str(revision)],
            cwd=self.path,
            **args
        )

        # Finally, rebase
        subprocess.check_call(
            ["git", "svn", "rebase", "--local"],
            cwd=self.path,
            **args
        )
