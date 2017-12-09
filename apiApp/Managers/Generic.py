
from GitServerHTTPEndpoint.settings import BARE_GIT_REPOS_ROOT, FULL_GIT_REPOS_ROOT


class GenericGitManager:

    def __call__(self, *args, **kwargs):
        return self.__init__()

    bare_root_path = BARE_GIT_REPOS_ROOT
    full_root_path = FULL_GIT_REPOS_ROOT

    dir_mode = 0o770
    script_perms = 'RX'
