from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from authApp.tokens import validate_api_token
from authApp.models import APIToken

from apiApp.Managers.Namespace import NamespaceGitManager
from apiApp.Managers.Repository import RepositoryGitManager
from apiApp.Managers.File import FileGitManager

# Create your views here.


@method_decorator(csrf_exempt, name="dispatch")
class NamespaceTokenAuthenticatedView(View):

    template = None

    def post_proc_steps(self):
        return [self.validate_call, self.pre_proc, self.proc, self.post_proc]

    def authenticate(self, request):
        client_token = request.POST.get('token')
        if client_token is None:
            raise PermissionDenied("No client token provided")
        if not validate_api_token(client_api_token=client_token):
            raise PermissionDenied("Invalid Token")

    def not_authorized(self, request, reason):
        raise reason

    def validate_call(self, request, namespace):
        return None

    def pre_proc(self, request, namespace):
        return None

    def proc(self, request, namespace):
        return None

    def post_proc(self, request, namespace):
        return self.success()

    def post(self, request, namespace):
        try:
            self.authenticate(request=request)
            for func in self.post_proc_steps():
                response = func(request=request, namespace=namespace)
                if response is not None:
                    return response
            return None
        except PermissionDenied as pe:
            return self.not_authorized(request=request, reason=pe)

    def get(self, request, namespace):
        pass

    def success(self):
        return HttpResponse(content='OK', content_type="text/plain", status=200, charset='UTF-8')


@method_decorator(csrf_exempt, name="dispatch")
class RepositoryTokenAuthenticatedView(View):

    template = None

    def post_proc_steps(self):
        return [self.validate_call, self.pre_proc, self.proc, self.post_proc]

    def authenticate(self, request):
        client_token = request.POST.get('token')
        if client_token is None:
            raise PermissionDenied("No client token provided")
        if not validate_api_token(client_api_token=client_token):
            raise PermissionDenied("Invalid Token")

    def not_authorized(self, request, reason):
        raise reason

    def validate_call(self, request, namespace, repository):
        return None

    def pre_proc(self, request, namespace, repository):
        return None

    def proc(self, request, namespace, repository):
        return None

    def post_proc(self, request, namespace, repository):
        return self.success()

    def post(self, request, namespace, repository):
        try:
            self.authenticate(request=request)
            for func in self.post_proc_steps():
                response = func(request=request, namespace=namespace, repository=repository)
                if response is not None:
                    return response
            return None
        except PermissionDenied as pe:
            return self.not_authorized(request=request, reason=pe)

    def get(self, request, namespace, repository):
        pass

    def success(self):
        return HttpResponse(content='OK', content_type="text/plain", status=200, charset='UTF-8')


@method_decorator(csrf_exempt, name="dispatch")
class FileTokenAuthenticatedView(View):

    template = None

    def post_proc_steps(self):
        return [self.validate_call, self.pre_proc, self.proc, self.post_proc]

    def authenticate(self, request):
        client_token = request.POST.get('token')
        if client_token is None:
            raise PermissionDenied("No client token provided")
        if not validate_api_token(client_api_token=client_token):
            raise PermissionDenied("Invalid Token")

    def not_authorized(self, request, reason):
        raise reason

    def validate_call(self, request, namespace, repository, file_path):
        return None

    def pre_proc(self, request, namespace, repository, file_path):
        return None

    def proc(self, request, namespace, repository, file_path):
        return None

    def post_proc(self, request, namespace, repository, file_path):
        return self.success()

    def post(self, request, namespace, repository, file_path):
        try:
            self.authenticate(request=request)
            for func in self.post_proc_steps():
                response = func(request=request, namespace=namespace, repository=repository, file_path=file_path)
                if response is not None:
                    return response
            return None
        except PermissionDenied as pe:
            return self.not_authorized(request=request, reason=pe)

    def get(self, request, namespace, repository, file):
        pass

    def success(self):
        return HttpResponse(content='OK', content_type="text/plain", status=200, charset='UTF-8')


class ManagedNamespaceView(NamespaceTokenAuthenticatedView):

    manager = NamespaceGitManager()


class ManagedRepositoryView(RepositoryTokenAuthenticatedView):

    managed_namespace_view = ManagedNamespaceView()
    manager = RepositoryGitManager()
    namespace_manager = manager.namespace_manager()


class ManagedFileView(FileTokenAuthenticatedView):

    managed_repository_view = ManagedRepositoryView()
    managed_namespace_view = ManagedNamespaceView()
    manager = FileGitManager()
    repository_manager = manager.repository_manager()
    namespace_manager = manager.namespace_manager()


class CreateNamespaceView(ManagedNamespaceView):

    def post_proc_steps(self):
        return [self.validate_call, self.proc]

    def validate_call(self, request, namespace):
        # Test for existence of namespace
        try:
            exists_full = getattr(self.manager, 'exists_full')
            exists_bare = getattr(self.manager, 'exists_bare')
            if exists_full(namespace=namespace)\
                    and exists_bare(namespace=namespace):
                return self.success()
            else:
                return None
        except ValueError as ve:
            raise ve

    def proc(self, request, namespace):
        # Create namespace
        try:
            create = getattr(self.manager, 'create')
            create(namespace=namespace)
            return self.success()
        except ValueError as ve:
            raise ve


class EditNamespaceView(ManagedNamespaceView):

    def post_proc_steps(self):
        return [self.validate_call, self.proc]

    def validate_call(self, request, namespace):
        # Test for existence of old and new namespace
        new_namespace = request.POST.get('new_namespace', None)
        try:
            exists_full = getattr(self.manager, 'exists_full')
            exists_bare = getattr(self.manager, 'exists_bare')
            if exists_full(namespace=namespace) and exists_bare(namespace=namespace):
                if new_namespace is None:
                    return None
                if not exists_full(namespace=new_namespace) and not exists_bare(namespace=new_namespace):
                    return None
                raise ValueError("%s ya existe" % new_namespace)
            else:
                raise ValueError("%s no existe" % namespace)
        except ValueError as ve:
            raise ve

    def proc(self, request, namespace):
        # Edit namespace
        new_namespace = request.POST.get('new_namespace', None)
        if new_namespace is None:
            return self.success()
        try:
            move = getattr(self.manager, 'move')
            move(namespace, new_namespace)
            return self.success()
        except ValueError as ve:
            raise ve


class CreateRepositoryView(ManagedRepositoryView):

    managed_namespace_view = CreateNamespaceView()

    def post_proc_steps(self):
        return [self.validate_call, self.proc]

    def validate_call(self, request, namespace, repository):
        # Test for existence of namespace
        namespace_valid_call = getattr(self.managed_namespace_view, 'validate_call')
        namespace_valid = namespace_valid_call(request=request, namespace=namespace)
        if namespace_valid is None:
            namespace_proc = getattr(self.managed_namespace_view, 'proc')
            namespace_valid = namespace_proc(request=request, namespace=namespace)
        if namespace_valid is None:
            raise ValueError("Error with %s namespace" % namespace)
        # Test for existence of repository
        try:
            exists_full = getattr(self.manager, 'exists_full')
            exists_bare = getattr(self.manager, 'exists_bare')
            if exists_full(namespace=namespace, repository=repository) \
                    and exists_bare(namespace=namespace, repository=repository):
                return self.success()
            else:
                return None
        except ValueError as ve:
            raise ve

    def proc(self, request, namespace, repository):
        # Create repository
        try:
            create = getattr(self.manager, 'create')
            create(namespace=namespace, repository=repository)
            return self.success()
        except ValueError as ve:
            raise ve


class EditRepositoryView(ManagedRepositoryView):

    managed_namespace_view = EditNamespaceView()

    def post_proc_steps(self):
        return [self.validate_call, self.pre_proc, self.proc]

    def validate_call(self, request, namespace, repository):
        # Test for existence of namespace
        namespace_valid_call = getattr(self.managed_namespace_view, 'validate_call')
        namespace_valid = namespace_valid_call(request=request, namespace=namespace)
        if namespace_valid is not None:
            raise ValueError("Unable to preform operation due to Namespace Error")
        # Test for existence of repository
        new_namespace = request.POST.get('new_namespace', None)
        new_repository = request.POST.get('new_repository', None)
        try:
            exists_full = getattr(self.manager, 'exists_full')
            exists_bare = getattr(self.manager, 'exists_bare')
            if exists_full(namespace=namespace, repository=repository)\
                    and exists_bare(namespace=namespace, repository=repository):
                if new_repository is None:
                    return None
                try:
                    if not exists_full(namespace=new_namespace, repository=new_repository)\
                            and not exists_bare(namespace=new_namespace, repository=new_repository):
                        return None
                except ValueError:
                    return None
                raise ValueError("%s ya existe" % new_repository)
            else:
                raise ValueError("%s no existe" % repository)
        except ValueError as ve:
            raise ve

    def pre_proc(self, request, namespace, repository):
        # Edit Namespace
        namespace_proc = getattr(self.managed_namespace_view, 'proc')
        namespace_mv = namespace_proc(request=request, namespace=namespace)
        if namespace_mv is None:
            raise ValueError("Error in moving Namespace")
        return None

    def proc(self, request, namespace, repository):
        # Edit repository
        new_repository = request.POST.get('new_repository', None)
        if new_repository is None:
            return self.success()
        current_namespace = request.POST.get('new_namespace', None)
        if current_namespace is None:
            current_namespace = namespace
        try:
            move = getattr(self.manager, 'move')
            move(namespace=current_namespace, old_repository=repository, new_repository=new_repository)
            return self.success()
        except ValueError as ve:
            raise ve


class CreateFileView(ManagedFileView):

    managed_repository_view = CreateRepositoryView()
    managed_namespace_view = managed_repository_view.managed_namespace_view

    def post_proc_steps(self):
        return [self.validate_call, self.proc]

    def validate_call(self, request, namespace, repository, file_path):
        # Test for existence of namespace/repository
        repository_valid_call = getattr(self.managed_repository_view, 'validate_call')
        repository_valid = repository_valid_call(request=request, namespace=namespace, repository=repository)
        if repository_valid is None:
            repository_proc = getattr(self.managed_repository_view, 'proc')
            repository_valid = repository_proc(request=request, namespace=namespace, repository=repository)
        if repository_valid is None:
            raise ValueError("Error with %s repository" % repository)
        # Test for existence of file
        try:
            exists_full = getattr(self.manager, 'exists_full')
            if exists_full(namespace=namespace, repository=repository, file_path=file_path):
                return self.success()
            else:
                return None
        except ValueError as ve:
            raise ve

    def proc(self, request, namespace, repository, file_path):
        # Create file
        token = request.POST.get('token', None)
        name = "Unknown App"
        if token is not None:
            api_token = APIToken.objects.get(token=token)
            name = api_token.app_name
        comment = "File created by %s" % name
        try:
            create = getattr(self.manager, 'create')
            create(namespace=namespace, repository=repository, file_path=file_path, commit=True, comment=comment)
            return self.success()
        except ValueError as ve:
            raise ve


class EditFileView(ManagedFileView):

    managed_repository_view = EditRepositoryView()
    managed_namespace_view = managed_repository_view.managed_namespace_view

    def post_proc_steps(self):
        return [self.validate_call, self.pre_proc, self.proc]

    def validate_call(self, request, namespace, repository, file_path):
        # Test for existence of namespace/repository
        repository_valid_call = getattr(self.managed_repository_view, 'validate_call')
        repository_valid = repository_valid_call(request=request, namespace=namespace, repository=repository)
        if repository_valid is not None:
            raise ValueError("Unable to preform operation due to Repository Error")
        # Test for existence of repository
        new_namespace = request.POST.get('new_namespace', None)
        new_repository = request.POST.get('new_repository', None)
        new_file_path = request.POST.get('new_file_path', None)
        try:
            exists_full = getattr(self.manager, 'exists_full')
            if exists_full(namespace=namespace, repository=repository, file_path=file_path):
                if new_file_path is None:
                    return None
                try:
                    if not exists_full(namespace=new_namespace, repository=new_repository, file_path=new_file_path):
                        return None
                except ValueError:
                    return None
                raise ValueError("%s ya existe" % new_file_path)
            else:
                raise ValueError("%s no existe" % file_path)
        except ValueError as ve:
            raise ve


class MoveEditFileView(EditFileView):

    def pre_proc(self, request, namespace, repository, file_path):
        # Edit Namespace/Repository
        repository_proc = getattr(self.managed_repository_view, 'proc')
        repository_mv = repository_proc(request=request, repository=repository)
        if repository_mv is None:
            raise ValueError("Error in moving Repository")
        return None

    def proc(self, request, namespace, repository, file_path):
        # Edit file_path
        new_file_path = request.POST.get('new_file_path', None)
        if new_file_path is None:
            return self.success()
        current_namespace = request.POST.get('new_namespace', None)
        if current_namespace is None:
            current_namespace = namespace
        current_repository = request.POST.get('new_repository', None)
        if current_repository is None:
            current_repository = repository
        token = request.POST.get('token', None)
        name = "Unknown App"
        if token is not None:
            api_token = APIToken.objects.get(token=token)
            name = api_token.app_name
        comment = "File moved by %s" % name
        commit = request.POST.get('commit', True)   # look for commit variable, otherwise assume that we should create a
                                                    # commit
        try:
            move = getattr(self.manager, 'move')
            move(namespace=current_namespace, repository=current_repository, old_file_path=file_path,
                 new_file_path=new_file_path, comment=comment, commit=commit)
            return self.success()
        except ValueError as ve:
            raise ve


class ContentsEditFileView(EditFileView):

    def post_proc_steps(self):
        return [self.validate_call, self.proc]

    def proc(self, request, namespace, repository, file_path):
        contents = request.POST.get('contents', "")  # look for contents variable in POST request or use empty string
        token = request.POST.get('token', None)
        name = "Unknown App"
        if token is not None:
            api_token = APIToken.objects.get(token=token)
            name = api_token.app_name
        comment = "File edited by %s" % name
        commit = request.POST.get('commit', True)   # look for commit variable, otherwise assume that we should create a
                                                    # commit
        try:
            edit = getattr(self.manager, 'edit')
            edit(namespace=namespace, repository=repository, file_path=file_path, contents=contents, commit=commit,
                 comment=comment)
            return self.success()
        except ValueError as ve:
            raise ve
