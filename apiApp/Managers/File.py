
import os
import pathlib
import subprocess

from apiApp.Managers.Generic import GenericGitManager
# from apiApp.Managers.Namespace import NamespaceGitManager
from apiApp.Managers.Repository import RepositoryGitManager


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
                        git_add = subprocess.run(['git', '--git-dir=%s/.git' % full_repo_path, 'add', file_path],
                                                 stdout=subprocess.PIPE, cwd=full_repo_path)
                        print(git_add.stdout)
                        git_commit = subprocess.run(['git', '--git-dir=%s/.git' % full_repo_path, 'commit', '-m',
                                                     '"%s"' % comment], stdout=subprocess.PIPE, cwd=full_repo_path)
                        print(git_commit.stdout)
                if create_bare:
                    bare_repo_path = self.build_bare_path(namespace=namespace, repository=repository)
                    git_pull = subprocess.run(['git', '--git-dir=%s' % bare_repo_path, 'pull', full_repo_path],
                                              stdout=subprocess.PIPE)
                    print(git_pull.stdout)
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
                git_add = subprocess.run(['git', '--git-dir=%s/.git' % full_repo_path, 'add', file_path],
                                         stdout=subprocess.PIPE, cwd=full_repo_path)
                print(git_add.stdout)
                git_commit = subprocess.run(['git', '--git-dir=%s/.git' % full_repo_path, 'commit', '-m',
                                             '"%s"' % comment], stdout=subprocess.PIPE, cwd=full_repo_path)
                print(git_commit.stdout)
                bare_repo_path = self.build_bare_path(namespace=namespace, repository=repository)
                git_pull = subprocess.run(['git', '--git-dir=%s' % bare_repo_path, 'pull', full_repo_path],
                                          stdout=subprocess.PIPE)
                print(git_pull.stdout)
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
            # we want to use git's internal move operator
            git_mv = subprocess.run(['git', '--git-dir=%s/.git' % full_repo_path, 'mv', old_file_path, new_file_path],
                                    stdout=subprocess.PIPE, cwd=full_repo_path)
            print(git_mv.stdout)
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
            git_commit = subprocess.run(['git', '--git-dir=%s/.git' % full_repo_path, 'commit', '-m',
                                         '"%s"' % comment], stdout=subprocess.PIPE, cwd=full_repo_path)
            print(git_commit.stdout)
            bare_repo_path = self.build_bare_path(namespace=namespace, repository=repository)
            git_pull = subprocess.run(['git', '--work-dir=%s' % bare_repo_path, '--git-dir=%s' % bare_repo_path,
                                       'pull', full_repo_path], stdout=subprocess.PIPE)
            print(git_pull.stdout)
