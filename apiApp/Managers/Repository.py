
import os
import pathlib
import subprocess

from apiApp.Managers.Generic import GenericGitManager
from apiApp.Managers.Namespace import NamespaceGitManager


class RepositoryGitManager(GenericGitManager):

    namespace_manager = NamespaceGitManager

    def build_full_path(self, namespace, repository):
        return "%s/%s/%s" % (self.full_root_path, namespace, repository)

    def build_bare_path(self, namespace, repository):
        return "%s/%s/%s.git" % (self.bare_root_path, namespace, repository)

    def exists_full(self, namespace, repository):
        namespace_exists = self.namespace_manager.exists_full(namespace=namespace)
        if namespace_exists:
            repository_full_path = pathlib.Path(self.build_full_path(namespace=namespace, repository=repository))
            if repository_full_path.exists():
                if repository_full_path.is_dir():
                    return True
                raise ValueError("%s is not a Directory" % self.build_full_path(namespace=namespace,
                                                                                repository=repository))
            return False
        else:
            raise ValueError("Namespace %s does not exist" % namespace)

    def exists_bare(self, namespace, repository):
        namespace_exists = self.namespace_manager.exists_bare(namespace=namespace)
        if namespace_exists:
            repository_bare_path = pathlib.Path(self.build_bare_path(namespace=namespace, repository=repository))
            if repository_bare_path.exists():
                if repository_bare_path.is_dir():
                    return True
                raise ValueError("%s is not a Directory" % self.build_bare_path(namespace=namespace,
                                                                                repository=repository))
            return False
        else:
            raise ValueError("Namespace %s does not exist" % namespace)

    def create(self, namespace, repository):
        self.namespace_manager.create(namespace=namespace)
        try:
            create_full = not self.exists_full(namespace=namespace, repository=repository)
            create_bare = not self.exists_bare(namespace=namespace, repository=repository)
            if create_full or create_bare:
                full_path = self.build_full_path(namespace=namespace, repository=repository)
                bare_path = self.build_bare_path(namespace=namespace, repository=repository)
                if create_full and create_bare:
                    os.mkdir(full_path, self.dir_mode)
                    git_init = subprocess.run(['git', 'init'], cwd=full_path, stdout=subprocess.PIPE)
                    print(git_init.stdout)
                    git_clone = subprocess.run(['git', 'clone', '--bare', full_path, bare_path], stdout=subprocess.PIPE)
                    print(git_clone.stdout)
                elif create_full:
                    git_clone = subprocess.run(['git', 'clone', bare_path, full_path], stdout=subprocess.PIPE)
                    print(git_clone.stdout)
                elif create_bare:
                    git_clone = subprocess.run(['git', 'clone', '--bare', full_path, bare_path], stdout=subprocess.PIPE)
                    print(git_clone.stdout)
            return True
        except ValueError:
            return False
        except Exception as e:
            raise e

    def move(self, namespace, old_repository, new_repository):
        if self.exists_full(namespace=namespace, repository=new_repository):
            raise ValueError("%s already exists" % self.build_full_path(namespace=namespace, repository=new_repository))
        if not self.exists_full(namespace=namespace, repository=old_repository):
            raise ValueError("%s does not exist" % self.build_full_path(namespace=namespace, repository=old_repository))
        os.rename(
            self.build_full_path(namespace=namespace, repository=old_repository),
            self.build_full_path(namespace=namespace, repository=new_repository)
        )
