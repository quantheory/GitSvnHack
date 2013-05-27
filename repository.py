#!/usr/bin/env python3
"""Classes for interaction with Subversion and Git repositories."""

import re
import subprocess


class Repo:
    """Repository class."""
    def __init__(self, name, path, **args):
        self._name = name
        self._path = path
        super().__init__(**args)

    @property
    def name(self):
        """Name for the repository."""
        return self._name

    @property
    def path(self):
        """Path to the repository."""
        return self._path


class SvnBranch:
    """Relative paths to a Subversion branch and its tags."""
    def __init__(self, head, tags):
        self._head = head
        self._tags = tags

    @property
    def head(self):
        """Relative path to the branch's head."""
        return self._head

    @property
    def tags(self):
        """Glob expression for relative path to the branch's tags."""
        return self._tags


class SvnRepo(Repo):
    """Subversion repository class."""
    def __init__(self, trunk_head, trunk_tags, **args):
        self._trunk_branch = SvnBranch(trunk_head, trunk_tags)
        super().__init__(**args)

    @property
    def trunk_head(self):
        """URL for the repo's trunk."""
        return self.path+"/"+self._trunk_branch.head

    @property
    def trunk_tags(self):
        """Glob expression for the URLs corresponding to trunk
        tags."""
        return self.path+"/"+self._trunk_branch.tags

    @property
    def trunk_branch(self):
        """SvnBranch object for trunk."""
        return self._trunk_branch

    def create(self):
        """Creates the repository it describes. Should only be used for
        testing."""
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
        """Import a file into the repo, using a path relative to the
        trunk's root. Should only be used for testing."""
        subprocess.check_call(
            ["svn", "import", file_path, self.trunk_head+"/"+repo_path,
             "-q", "-m", msg]
        )


class GitRepo(Repo):
    """Git repository class."""
    def __init__(self, **args):
        super().__init__(**args)


class GitSvnRepo(GitRepo):
    """git-svn repository class."""
    def __init__(self, svn_repo, **args):
        self._svn_repo = svn_repo
        super().__init__(**args)

    @property
    def svn_repo(self):
        """Subversion repository corresponding to this GitSvnRepo."""
        return self._svn_repo

    def clone(self, stdout=None, stderr=None):
        """Use "git svn clone" to clone the repo."""
        svn_trunk = self.svn_repo.trunk_branch
        subprocess.check_call(
            ["git", "svn", "clone", self.svn_repo.path,
             "-T", svn_trunk.head, self.path],
            stdout=stdout, stderr=stderr,
        )
