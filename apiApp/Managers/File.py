
import os
import pathlib
import subprocess

from apiApp.Managers.Generic import GenericGitManager
# from apiApp.Managers.Namespace import NamespaceGitManager
from apiApp.Managers.Repository import RepositoryGitManager
from apiApp.Managers.Git import GitManager


class FileGitManager(GenericGitManager):

    repository_manager = RepositoryGitManager()
    namespace_manager = repository_manager.namespace_manager

    def build_full_path(self, namespace, repository, file_path):
        return "%s/%s/%s/%s" % (self.full_root_path, namespace, repository, file_path)

    def build_bare_path(self, namespace, repository):
        return "%s/%s/%s.git" % (self.bare_root_path, namespace, repository)

    def exists_full(self, namespace, repository, file_path):
        # Test namespace existence (included in repository existence test)
        # Test repository existence
        repo_exists_full = getattr(self.repository_manager, 'exists_full')
        repo_test = repo_exists_full(namespace=namespace, repository=repository)
        if not repo_test:
            raise ValueError("Namespace/Repository %s/%s does not exist" % (namespace, repository))
        # Test file existence
        file_full_path = pathlib.Path(
            self.build_full_path(namespace=namespace, repository=repository, file_path=file_path)
        )
        if file_full_path.exists():
            if file_full_path.is_file():
                return True
            raise ValueError("%s is not a file!" % self.build_full_path(namespace=namespace, repository=repository,
                                                                        file_path=file_path))
        return False

    def exists_bare(self, namespace, repository):
        # Test namespace existence (included in repository existence test)
        # Test repository existence
        repo_exists_bare = getattr(self.repository_manager, 'exists_bare')
        return repo_exists_bare(namespace=namespace, repository=repository)

    def create(self, namespace, repository, file_path, commit=True, comment=None):
        # Create namespace if it doesn't exist (included in repository create)
        # Create repository if it doesn't exist
        repository_create = getattr(self.repository_manager, 'create')
        repository_create(namespace=namespace, repository=repository)
        # Create file if it doesn't exist
        try:
            create_full = not self.exists_full(namespace=namespace, repository=repository, file_path=file_path)
            create_bare = commit    # We should only copy the file into the bare repository if we are allowed to make a
                                    # commit in the full repository first
            if create_full or create_bare:
                full_repo_path_builder = getattr(self.repository_manager, 'build_full_path')
                full_repo_path = full_repo_path_builder(namespace=namespace, repository=repository)
                gm = GitManager(full_repo_path=full_repo_path, bare_repo_path=None,
                                name=RepositoryGitManager.author_name, email=RepositoryGitManager.author_email)
                if create_full:
                    # Create File
                    full_file_path = self.build_full_path(namespace=namespace, repository=repository,
                                                          file_path=file_path)
                    full_dir_path = pathlib.Path(full_file_path).parent
                    os.makedirs(full_dir_path.__str__(), self.dir_mode)
                    open(full_file_path, 'a').close()
                    # Add Git Commit of empty file if requested
                    if commit:
                        if comment is None:
                            comment = "File created/commited by Git Server HTTP Endpoint"
                        gm.add_full(file_path=file_path)
                        gm.commit_full(comment=comment)
                if create_bare:
                    bare_repo_path = self.build_bare_path(namespace=namespace, repository=repository)
                    gm.bare_repo_path = bare_repo_path
                    # git branch | grep '*' | awk '{print $2}'
                    full_branch = gm.current_full_branch()
                    # git push -u $bare_repo_path $(git branch | grep '*' | awk '{print $2}')
                    gm.push_full_to_bare(full_branch)
            return True
        except ValueError:
            return False
        except Exception as e:
            raise e

    def edit(self, namespace, repository, file_path, contents, commit=True, comment=None):
        # Create namespace/repository/file if they don't exist,
        # but don't commit (we want to commit with initial contents)
        self.create(namespace=namespace, repository=repository, file_path=file_path, commit=False)
        # Overwrite file with contents
        try:
            full_file_path = self.build_full_path(namespace=namespace, repository=repository, file_path=file_path)
            with open(full_file_path, 'w') as file:
                file.write(contents)
            # Commit if requested
            if commit:
                full_repo_path_builder = getattr(self.repository_manager, 'build_full_path')
                full_repo_path = full_repo_path_builder(namespace=namespace, repository=repository)
                if comment is None:
                    comment = "File Edited/Commit created by Git Server HTTP Endpoint"
                gm = GitManager(full_repo_path=full_repo_path, bare_repo_path=None,
                                name=RepositoryGitManager.author_name, email=RepositoryGitManager.author_email)
                gm.add_full(file_path=file_path)
                gm.commit_full(comment=comment)
                bare_repo_path = self.build_bare_path(namespace=namespace, repository=repository)
                gm.bare_repo_path = bare_repo_path
                full_branch = gm.current_full_branch()
                gm.push_full_to_bare(branch=full_branch)
            return True
        except ValueError:
            return False
        except Exception as e:
            raise e

    def move(self, namespace, repository, old_file_path, new_file_path, overwrite=False, git_op=True, commit=True,
             comment=None):
        # Rename file
        if not overwrite and self.exists_full(namespace=namespace, repository=repository, file_path=new_file_path):
            raise ValueError("%s already exists" % new_file_path)
        if not self.exists_full(namespace=namespace, repository=repository, file_path=old_file_path):
            raise ValueError("%s does not exist" % old_file_path)
        full_repo_path_builder = getattr(self.repository_manager, 'build_full_path')
        full_repo_path = full_repo_path_builder(namespace=namespace, repository=repository)
        if git_op:
            gm = GitManager(full_repo_path=full_repo_path, bare_repo_path=None,
                            name=RepositoryGitManager.author_name, email=RepositoryGitManager.author_email)
            # we want to use git's internal move operator
            gm.move_full(old_file_path=old_file_path, new_file_path=new_file_path)
        else:
            # if we don't want to use git's internal move operator, use Operating System's move operation
            os.rename(
                self.build_full_path(namespace=namespace, repository=repository, file_path=old_file_path),
                self.build_full_path(namespace=namespace, repository=repository, file_path=new_file_path)
            )
        # Commit if requested
        if commit:
            if comment is None:
                comment = "File Moved/Commit created by Git Server HTTP Endpoint"
            gm = GitManager(full_repo_path=full_repo_path, bare_repo_path=None,
                            name=RepositoryGitManager.author_name, email=RepositoryGitManager.author_email)
            gm.commit_full(comment=comment)
            bare_repo_path = self.build_bare_path(namespace=namespace, repository=repository)
            gm.bare_repo_path = bare_repo_path
            full_branch = gm.current_full_branch()
            gm.push_full_to_bare(branch=full_branch)
