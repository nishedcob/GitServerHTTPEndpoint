
import os
import pathlib
import subprocess
import re

from apiApp.Managers.Generic import GenericGitManager
from apiApp.Managers.Namespace import NamespaceGitManager
from apiApp.Managers.Git import GitManager


class RepositoryGitManager(GenericGitManager):

    author_name = "Git Server HTTP Endpoint"
    author_email = None
    try:
        author_email = "git@%s" % re.compile("^b'(.*)\\\\n'$").match(subprocess.run(['hostname'],
                                                                                    stdout=subprocess.PIPE).stdout
                                                                     .__str__()).group(1)
    except IndexError:
        author_email = "git@Unknown"

    namespace_manager = NamespaceGitManager()

    def build_full_path(self, namespace, repository):
        return "%s/%s/%s" % (self.full_root_path, namespace, repository)

    def build_bare_path(self, namespace, repository):
        return "%s/%s/%s.git" % (self.bare_root_path, namespace, repository)

    def exists_full(self, namespace, repository):
        namespace_exists_full = getattr(self.namespace_manager, 'exists_full')
        namespace_exists = namespace_exists_full(namespace=namespace)
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
        namespace_exists_bare = getattr(self.namespace_manager, 'exists_bare')
        namespace_exists = namespace_exists_bare(namespace=namespace)
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
        namespace_create = getattr(self.namespace_manager, 'create')
        namespace_create(namespace=namespace)
        try:
            create_full = not self.exists_full(namespace=namespace, repository=repository)
            create_bare = not self.exists_bare(namespace=namespace, repository=repository)
            if create_full or create_bare:
                full_path = self.build_full_path(namespace=namespace, repository=repository)
                bare_path = self.build_bare_path(namespace=namespace, repository=repository)
                gm = GitManager(full_repo_path=full_path, bare_repo_path=bare_path, name=self.author_name,
                                email=self.author_email, config_user=False)
                if create_full and create_bare:
                    os.mkdir(full_path, self.dir_mode)
                    gm.init_bare()
                    gm.config_user_full(name=self.author_name, email=self.author_email)
                    gm.clone_full_to_bare()
                elif create_full:
                    gm.clone_bare_to_full()
                    gm.config_user_full(name=self.author_name, email=self.author_email)
                elif create_bare:
                    gm.clone_full_to_bare()
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
        if self.exists_bare(namespace=namespace, repository=new_repository):
            raise ValueError("%s already exists" % self.build_bare_path(namespace=namespace, repository=new_repository))
        if not self.exists_bare(namespace=namespace, repository=old_repository):
            raise ValueError("%s does not exist" % self.build_bare_path(namespace=namespace, repository=old_repository))
        os.rename(
            self.build_full_path(namespace=namespace, repository=old_repository),
            self.build_full_path(namespace=namespace, repository=new_repository)
        )
        os.rename(
            self.build_bare_path(namespace=namespace, repository=old_repository),
            self.build_bare_path(namespace=namespace, repository=new_repository)
        )
