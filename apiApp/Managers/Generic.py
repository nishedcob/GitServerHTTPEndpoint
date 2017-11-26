
from GitServerHTTPEndpoint.settings import BARE_GIT_REPOS_ROOT, FULL_GIT_REPOS_ROOT


class GenericGitManager:

    bare_root_path = BARE_GIT_REPOS_ROOT
    full_root_path = FULL_GIT_REPOS_ROOT

    dir_mode = 0o770
