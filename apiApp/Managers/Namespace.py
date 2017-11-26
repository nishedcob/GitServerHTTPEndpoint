
import os
import pathlib

from apiApp.Managers.Generic import GenericGitManager


class NamespaceGitManager(GenericGitManager):

    def build_full_path(self, namespace):
        return "%s/%s" % (self.full_root_path, namespace)

    def build_bare_path(self, namespace):
        return "%s/%s" % (self.bare_root_path, namespace)

    def exists_full(self, namespace):
        namespace_full_path = pathlib.Path(self.build_full_path(namespace=namespace))
        if namespace_full_path.exists():
            if namespace_full_path.is_dir():
                return True
            raise ValueError("%s is not a Directory" % self.build_full_path(namespace=namespace))
        return False

    def exists_bare(self, namespace):
        namespace_bare_path = pathlib.Path(self.build_bare_path(namespace=namespace))
        if namespace_bare_path.exists():
            if namespace_bare_path.is_dir():
                return True
            raise ValueError("%s is not a Directory" % self.build_bare_path(namespace=namespace))
        return False

    def create(self, namespace):
        try:
            full_path = self.build_full_path(namespace=namespace)
            if not self.exists_full(namespace=namespace):
                os.mkdir(full_path, self.dir_mode)
            bare_path = self.build_bare_path(namespace=namespace)
            if not self.exists_bare(namespace=namespace):
               os.mkdir(bare_path, self.dir_mode)
            return True
        except ValueError:
            return False
        except Exception as e:
            raise e

    def move(self, old_namespace, new_namespace):
        if self.exists_full(namespace=new_namespace):
            raise ValueError("%s already exists" % self.build_full_path(namespace=new_namespace))
        if not self.exists_full(namespace=old_namespace):
            raise ValueError("%s does not exist" % self.build_full_path(namespace=old_namespace))
        os.rename(self.build_full_path(namespace=old_namespace), self.build_full_path(namespace=new_namespace))
