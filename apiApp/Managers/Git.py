
import os
import stat
import pathlib
import subprocess
import re

from apiApp.Managers.Generic import GenericGitManager
from GitServerHTTPEndpoint.settings import SYSTEM_DEBUG, BARE_GIT_REPOS_ROOT, UPDATE_GIT_SERVER_SCRIPT,\
    UPDATE_GIT_SERVER_SCRIPT_CONTENTS, UPDATE_ALL_GIT_SERVER_SCRIPT, UPDATE_ALL_GIT_SERVER_SCRIPT_CONTENTS,\
    UPDATE_GIT_SERVER_INDEX_SCRIPT, UPDATE_GIT_SERVER_INDEX_SCRIPT_CONTENTS, GIT_DIRS_PERMS_SCRIPT,\
    GIT_DIRS_PERMS_SCRIPT_CONTENTS


class GitManager(GenericGitManager):

    def __init__(self, full_repo_path, bare_repo_path, name, email, config_user=True):
        self._full_repo_path = None
        self.set_full_repo_path(full_repo_path=full_repo_path)
        self.bare_repo_path = bare_repo_path
        if config_user and self._full_repo_path is not None:
            self.config_user_full(name=name, email=email)

    '''
    Test the existence of file permissions on a file:
        r / R -> Read
        x / X -> eXecute
        w / W -> Write
        a / A -> All
    Lowercase letters test for the absence of a permission
    Uppercase letters test for the presence of a permission
    '''
    def test_perm(self, path, perm):
        if len(perm) > 1:
            return self.test_perm(path=path, perm=perm[0]) and self.test_perm(path=path, perm=perm[1:])
        if perm == 'r' or perm == 'R':
            os_perm = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        elif perm == 'x' or perm == 'X':
            os_perm = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        elif perm == 'w' or perm == 'W':
            os_perm = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        elif perm == 'a' or perm == 'A':
            if perm == 'a':
                test_perms = 'rxw'
            else:
                test_perms = 'RXW'
            return self.test_perm(path=path, perm=test_perms)
        else:
            raise ValueError("perm must be one of the following characters: rRxXwWaA")
        if 'z' >= perm >= 'a':
            invert_test = True
        else:
            invert_test = False
        st = os.stat(path)
        test = bool(st.st_mode & os_perm)
        return test if not invert_test else not test

    '''
    Set file permissions on a file:
        r / R -> Read
        x / X -> eXecute
        w / W -> Write
        a / A -> All
    Lowercase letters generate absence of a permission
    Uppercase letters generate presence of a permission
    '''
    def set_perm(self, path, perm):
        if self.test_perm(path=path, perm=perm):
            return True
        if len(perm) > 1:
            return self.set_perm(path=path, perm=perm[0]) and self.set_perm(path=path, perm=perm[1:])
        if perm == 'r' or perm == 'R':
            os_perm = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        elif perm == 'x' or perm == 'X':
            os_perm = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        elif perm == 'w' or perm == 'W':
            os_perm = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        elif perm == 'a' or perm == 'A':
            if perm == 'a':
                test_perms = 'rxw'
            else:
                test_perms = 'RXW'
            return self.test_perm(path=path, perm=test_perms)
        else:
            raise ValueError("perm must be one of the following characters: rRxXwWaA")
        current_mode = stat.S_IMODE(os.lstat(path).st_mode)
        if 'z' >= perm >= 'a':
            os_perm = ~os_perm
            os.chmod(path, current_mode & os_perm)
        else:
            os.chmod(path, current_mode | os_perm)
        return True

    def test_and_set_perm(self, path, perm):
        if not self.test_perm(path=path, perm=perm):
            return self.set_perm(path=path, perm=perm)
        return True

    def install_script(self, path, contents):
        upgrade_srv_script_path = pathlib.Path(path)
        upgrade_srv_script_dir_path = upgrade_srv_script_path.parent
        if not upgrade_srv_script_dir_path.exists():
            os.makedirs(upgrade_srv_script_dir_path.__str__(), self.dir_mode, exist_ok=True)
            self.test_and_set_perm(upgrade_srv_script_dir_path.__str__(), self.script_perms)
        else:
            if not upgrade_srv_script_dir_path.is_dir():
                raise ValueError("Parent directory %s must be a directory" % upgrade_srv_script_dir_path)
            self.test_and_set_perm(upgrade_srv_script_dir_path.__str__(), self.script_perms)
        if upgrade_srv_script_path.exists():
            if not upgrade_srv_script_path.is_file():
                raise ValueError("%s is not a file!" % path)
            self.test_and_set_perm(path=path, perm=self.script_perms)
        else:
            with open(path, 'a') as script_file:
                script_file.write(contents)
                script_file.flush()
            self.test_and_set_perm(path=path, perm=self.script_perms)

    def install_update_script(self):
        return self.install_script(path=UPDATE_GIT_SERVER_SCRIPT, contents=UPDATE_GIT_SERVER_SCRIPT_CONTENTS)

    def install_all_update_script(self):
        return self.install_script(path=UPDATE_ALL_GIT_SERVER_SCRIPT, contents=UPDATE_ALL_GIT_SERVER_SCRIPT_CONTENTS)

    def install_update_index_script(self):
        return self.install_script(path=UPDATE_GIT_SERVER_INDEX_SCRIPT,
                                   contents=UPDATE_GIT_SERVER_INDEX_SCRIPT_CONTENTS)

    def install_dirs_perms_script(self):
        return self.install_script(path=GIT_DIRS_PERMS_SCRIPT, contents=GIT_DIRS_PERMS_SCRIPT_CONTENTS)

    def update_server_info(self):
        self.install_update_script()
        self.install_all_update_script()
        # find -iname "*.git" -type d -exec ~/bin/git-perms {} \;
        command = [UPDATE_ALL_GIT_SERVER_SCRIPT]
        self.print_command(command)
        find_cmd = subprocess.run(command, cwd=BARE_GIT_REPOS_ROOT, stdout=subprocess.PIPE)
        return self.format_exit(find_cmd)

    def update_index(self):
        self.update_server_info()
        self.install_update_index_script()
        self.install_dirs_perms_script()
        # find ./ -iname "*.git" -type d | sed 's/^\.\///' | sed 's/$/ Git/' > ~/projects.list
        command = [UPDATE_GIT_SERVER_INDEX_SCRIPT]
        self.print_command(command)
        find_update_index_cmd = subprocess.run(command, cwd=BARE_GIT_REPOS_ROOT, stdout=subprocess.PIPE)
        # find ./ -type d -exec chmod -v o+rx {} \;
        command = [GIT_DIRS_PERMS_SCRIPT]
        self.print_command(command)
        find_dirs_perms_cmd = subprocess.run(command, cwd=BARE_GIT_REPOS_ROOT, stdout=subprocess.PIPE)
        return [
            self.format_exit(find_update_index_cmd), self.format_exit(find_dirs_perms_cmd)
        ]

    def get_full_repo_path(self):
        return self._full_repo_path

    def set_full_repo_path(self, full_repo_path):
        old_full_repo_path = self._full_repo_path
        self._full_repo_path = full_repo_path
        if self._full_repo_path is not None:
            path_full = pathlib.Path("%s/.git" % self._full_repo_path)
            if not path_full.exists():
                self.init_full()
            elif not path_full.is_dir():
                self._full_repo_path = old_full_repo_path
                raise ValueError(".git in Full Repo Path is not a directory as expected")

    full_repo_path = property(fget=get_full_repo_path, fset=set_full_repo_path)
    bare_repo_path = None
    estab_name = False
    estab_email = False
    default_comment = "Commit by Git Server HTTP Endpoint"
    default_debug = {
        'managers': {
            'types': {
                'git': None
            }
        }
    }
    debug_git = SYSTEM_DEBUG.get('git', default_debug).get('managers', default_debug['managers']) \
        .get('types', default_debug['managers']['types']).get('git', default_debug['managers']['types']['git'])

    def format_exit(self, proc):
        if proc is None:
            return None
        if self.debug_git:
            print("STDOUT:")
            print(proc.stdout)
            print("STDERR:")
            print(proc.stderr)
            if type(proc.returncode) == int:
                print("EXIT CODE: %d" % proc.returncode)
            else:
                print("EXIT CODE: %s" % proc.returncode)
        return proc.stdout, proc.stderr, proc.returncode

    def print_command(self, command_list=None, force_print=False):
        if force_print or self.debug_git:
            if type(command_list) == list:
                print("GIT COMMAND DEBUG: ", end='')
                for word in command_list:
                    print(word, end=' ')
                print("")

    def init(self, repo_path, bare=False):
        if repo_path is None:
            raise ValueError("Repository Path can not be None")
        init_repo_path = pathlib.Path(repo_path)
        if not init_repo_path.exists():
            os.makedirs(repo_path, mode=self.dir_mode, exist_ok=True)
        elif not init_repo_path.is_dir():
            raise ValueError("Repo Path is not a directory")
        command = ['git', 'init']
        if bare:
            command.append("--bare")
        self.print_command(command)
        git_init = subprocess.run(command, cwd=repo_path, stdout=subprocess.PIPE)
        self.update_index()
        return self.format_exit(git_init)

    def init_full(self):
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.init(repo_path=self.full_repo_path, bare=False)

    def init_bare(self):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        return self.init(repo_path=self.bare_repo_path, bare=True)

    def config_user(self, repo_path, name=None, email=None):
        if repo_path is None:
            raise ValueError("Repository Path can not be None")
        git_config_user_name = None
        git_config_user_email = None
        if name is not None:
            command = ['git', 'config', 'user.name', '"%s"' % name]
            self.print_command(command)
            git_config_user_name = subprocess.run(command, stdout=subprocess.PIPE, cwd=repo_path)
            self.estab_name = True
        if email is not None:
            command = ['git', 'config', 'user.email', email]
            self.print_command(command)
            git_config_user_email = subprocess.run(command, stdout=subprocess.PIPE, cwd=repo_path)
            self.estab_email = True
        if name is not None and email is not None:
            return [self.format_exit(git_config_user_name), self.format_exit(git_config_user_email)]
        else:
            if name is not None:
                return self.format_exit(git_config_user_name)
            elif email is not None:
                return self.format_exit(git_config_user_email)
            else:
                return None

    def config_user_full(self, name=None, email=None):
        return self.config_user(repo_path=self.full_repo_path, name=name, email=email)

    def clone(self, src_repo, dest_repo, bare=False):
        if src_repo is None:
            raise ValueError("Source Repository can't be None")
        if dest_repo is None:
            raise ValueError("Destination Repository can't be None")
        command = ['git', 'clone']
        if bare:
            command.append("--bare")
        command.append(src_repo)
        command.append(dest_repo)
        self.print_command(command)
        git_clone = subprocess.run(command, stdout=subprocess.PIPE)
        self.update_index()
        return self.format_exit(git_clone)

    def clone_bare(self, src_repo, dest_repo):
        return self.clone(src_repo=src_repo, dest_repo=dest_repo, bare=True)

    def clone_full_to_bare(self):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.clone_bare(src_repo=self.full_repo_path, dest_repo=self.bare_repo_path)

    def clone_bare_to_full(self):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.clone(src_repo=self.bare_repo_path, dest_repo=self.full_repo_path, bare=False)

    def add(self, repo_path, file_path):
        if repo_path is None:
            raise ValueError("Repository Path can not be None")
        if file_path is None:
            raise ValueError("File Path can not be None")
        if type(file_path) == list:
            operations = []
            for fp in file_path:
                operations.append(self.add(repo_path=repo_path, file_path=fp))
            return operations
        command = ['git', 'add', file_path]
        self.print_command(command)
        git_add = subprocess.run(command, stdout=subprocess.PIPE, cwd=repo_path)
        return self.format_exit(git_add)

    def add_bare(self, file_path):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        return self.add(repo_path=self.bare_repo_path, file_path=file_path)

    def add_full(self, file_path):
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.add(repo_path=self.full_repo_path, file_path=file_path)

    def commit(self, repo_path, comment=None):
        if not self.estab_name:
            raise ValueError("Author Name not established")
        if not self.estab_email:
            raise ValueError("Author Email not established")
        if comment is None:
            comment = self.default_comment
        command = ['git', 'commit', '-m', '"%s"' % comment]
        self.print_command(command)
        git_commit = subprocess.run(command, stdout=subprocess.PIPE, cwd=repo_path)
        self.update_index()
        return self.format_exit(git_commit)

    def commit_author(self, repo_path, author_name, author_email, comment=None):
        return [
            self.config_user(repo_path=repo_path, name=author_name, email=author_email),
            self.commit(repo_path=repo_path, comment=comment)
        ]

    def commit_full(self, comment=None):
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.commit(repo_path=self.full_repo_path, comment=comment)

    def commit_full_author(self, author_name, author_email, comment=None):
        return self.commit_author(repo_path=self.full_repo_path, author_name=author_name, author_email=author_email,
                                  comment=comment)

    def pull(self, src_repo, dest_repo, branch):
        if src_repo is None:
            raise ValueError("Source Repository can't be None")
        if dest_repo is None:
            raise ValueError("Destination Repository can't be None")
        if branch is None:
            raise ValueError("Branch can't be None")
        command = ['git', 'pull', src_repo, branch]
        self.print_command(command)
        git_pull = subprocess.run(command, cwd=dest_repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.update_index()
        return self.format_exit(git_pull)

    def pull_full_to_bare(self, branch):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.pull(src_repo=self.full_repo_path, dest_repo=self.bare_repo_path, branch=branch)

    def pull_bare_to_full(self, branch):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.pull(src_repo=self.bare_repo_path, dest_repo=self.full_repo_path, branch=branch)

    def push(self, src_repo, dest_repo, branch, upstream=True):
        if src_repo is None:
            raise ValueError("Source Repository can't be None")
        if dest_repo is None:
            raise ValueError("Destination Repository can't be None")
        if branch is None:
            branch = "--all"
        command = ['git', 'push']
        if upstream:
            command.append("-u")
        command.append(dest_repo)
        command.append(branch)
        self.print_command(command)
        git_push = subprocess.run(command, cwd=src_repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.update_index()
        return self.format_exit(git_push)

    def push_full_to_bare(self, branch):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.push(src_repo=self.full_repo_path, dest_repo=self.bare_repo_path, branch=branch, upstream=True)

    def push_bare_to_full(self, branch):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.push(src_repo=self.bare_repo_path, dest_repo=self.full_repo_path, branch=branch, upstream=True)

    def current_branch(self, repo_path):
        if repo_path is None:
            raise ValueError("No Git Repository Provided")
        # "git branch | grep '*' | awk '{print $2}'"
        command = ["git", "branch", "--list"]
        self.print_command(command)
        git_current_branch = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=repo_path)
        branches = git_current_branch.stdout.read().__str__()
        current_branch_regex = re.compile('\* ([a-z]*)\\\\n')
        current_branch = current_branch_regex.findall(branches)
        if len(current_branch) >= 1:
            return current_branch[0]
        else:
            raise ValueError("Current Branch Not Found")

    def current_bare_branch(self):
        if self.bare_repo_path is None:
            raise ValueError("No assigned bare repository")
        return self.current_branch(self.bare_repo_path)

    def current_full_branch(self):
        if self.full_repo_path is None:
            raise ValueError("No assigned full repository")
        return self.current_branch(self.full_repo_path)

    def move(self, repo_path, old_file_path, new_file_path):
        if repo_path is None:
            raise ValueError("Repo Path can't be None")
        if old_file_path is None:
            raise ValueError("Old File Path can't be None")
        if new_file_path is None:
            raise ValueError("New File Path can't be None")
        command = ['git', 'mv', old_file_path, new_file_path]
        self.print_command(command)
        git_mv = subprocess.run(command, stdout=subprocess.PIPE, cwd=repo_path)
        return self.format_exit(git_mv)

    def move_full(self, old_file_path, new_file_path):
        return self.move(repo_path=self.full_repo_path, old_file_path=old_file_path, new_file_path=new_file_path)
