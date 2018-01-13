
# import config from somewhere, for example with Django I would use a settings file
#from GitEDU.settings import GIT_SERVER_HTTP_ENDPOINT_CONFIG

# In this case, I will just place an example config here, extracted from GitEDU:
GIT_SERVER_HTTP_ENDPOINT_CONFIG = {
    "protocol": "http",
    "host": "127.0.0.1",
    "port": 8020,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHBpcmVzIjpmYWxzZSwiYXBwX25hbWUiOiJHaXRFRFUiLCJlZGl0X2RhdGUiOiIy"
             "MDE3LTExLTI1IDIwOjI2OjIzLjQ3MDgxNyswMDowMCIsImNyZWF0ZWRfZGF0ZSI6IjIwMTctMTEtMjUgMjA6MjY6MjMuNDcwNzUwKzAwO"
             "jAwIn0.jVHEmUAgJcQy7sU-qyULAnAiIrBAPNbeDjOiwjk5EEk"
}

import requests


class GitServerHTTPEndpointConsumer:

    create_operation = 'create'
    edit_operation = 'edit'
    edit_mv_operation = "%s/mv" % edit_operation
    edit_contents_operation = "%s/contents" % edit_operation

    url_template = "%s://%s:%d/api/%s/%s/%s"

    def build_url(self, protocol, host, port, object_type, operation, object_path):
        return self.url_template % (protocol, host, port, object_type, operation, object_path)

    def build_inicial_payload(self):
        return dict()

    def post_url(self, url, payload):
        return requests.post(url, data=payload)

    def validate_url(self, url):
        if not url.endswith("/"):
            url += "/"
        return url


class ConfigGitSrvHTTPEpConsumer(GitServerHTTPEndpointConsumer):

    protocol = None
    host = None
    port = None
    object_type = None
    token = None

    def __init__(self, protocol=None, host=None, port=None, object_type=None, token=None):
        self.protocol = self.protocol if protocol is None else protocol
        self.host = self.host if host is None else host
        self.port = self.port if port is None else port
        self.object_type = self.object_type if object_type is None else object_type
        self.token = self.token if token is None else token

    def build_inicial_payload(self):
        return {
            'token': self.token
        }

    def build_config_url(self, operation, object_path):
        return self.build_url(protocol=self.protocol, host=self.host, port=self.port, object_type=self.object_type,
                              operation=operation, object_path=object_path)


class DefaultConfigGitSrvHTTPEpConsumer(ConfigGitSrvHTTPEpConsumer):
    protocol = GIT_SERVER_HTTP_ENDPOINT_CONFIG.get('protocol')
    host = GIT_SERVER_HTTP_ENDPOINT_CONFIG.get('host')
    port = GIT_SERVER_HTTP_ENDPOINT_CONFIG.get('port')
    token = GIT_SERVER_HTTP_ENDPOINT_CONFIG.get('token')


class NamespaceGitSrvHTTPEpConsumer(DefaultConfigGitSrvHTTPEpConsumer):
    object_type = 'ns'

    def build_call_url(self, operation, namespace):
        url = self.build_config_url(operation=operation, object_path=namespace)
        if not url.endswith("/"):
            url += "/"
        return url

    def create_call(self, namespace):
        payload = self.build_inicial_payload()
        url = self.build_call_url(operation=self.create_operation, namespace=namespace)
        return self.post_url(url=url, payload=payload)

    def edit_call(self, namespace, new_namespace):
        payload = self.build_inicial_payload()
        payload['new_namespace'] = new_namespace
        url = self.build_call_url(operation=self.edit_operation, namespace=namespace)
        return self.post_url(url=url, payload=payload)


class RepositoryGitSrvHTTPEpConsumer(DefaultConfigGitSrvHTTPEpConsumer):
    object_type = 'repo'

    def build_object_path(self, namespace, repository):
        return "%s/%s" % (namespace, repository)

    def build_call_url(self, operation, namespace, repository):
        object_path = self.build_object_path(namespace=namespace, repository=repository)
        url = self.build_config_url(operation=operation, object_path=object_path)
        if not url.endswith("/"):
            url += "/"
        return url

    def create_call(self, namespace, repository):
        payload = self.build_inicial_payload()
        url = self.build_call_url(operation=self.create_operation, namespace=namespace, repository=repository)
        return self.post_url(url=url, payload=payload)

    def edit_call(self, namespace, repository, new_repository, new_namespace=None):
        payload = self.build_inicial_payload()
        if new_namespace is not None:
            payload['new_namespace'] = new_namespace
        payload['new_repository'] = new_repository
        url = self.build_call_url(operation=self.edit_operation, namespace=namespace, repository=repository)
        return self.post_url(url=url, payload=payload)


class FileGitSrvHTTPEpConsumer(DefaultConfigGitSrvHTTPEpConsumer):
    object_type = 'file'

    def build_object_path(self, namespace, repository, file_path):
        return "%s/%s/%s" % (namespace, repository, file_path)

    def build_call_url(self, operation, namespace, repository, file_path):
        object_path = self.build_object_path(namespace=namespace, repository=repository, file_path=file_path)
        return self.build_config_url(operation=operation, object_path=object_path)

    def create_call(self, namespace, repository, file_path, commit=True):
        payload = self.build_inicial_payload()
        payload['commit'] = commit
        url = self.build_call_url(operation=self.create_operation, namespace=namespace, repository=repository,
                                  file_path=file_path)
        return self.post_url(url=url, payload=payload)

    def edit_mv_call(self, namespace, repository, file_path, new_file_path, new_repository=None, new_namespace=None):
        payload = self.build_inicial_payload()
        if new_namespace is not None:
            payload['new_namespace'] = new_namespace
        if new_repository is not None:
            payload['new_repository'] = new_repository
        payload['new_file_path'] = new_file_path
        url = self.build_call_url(operation=self.edit_mv_operation, namespace=namespace, repository=repository,
                                  file_path=file_path)
        return self.post_url(url=url, payload=payload)

    def edit_contents_call(self, namespace, repository, file_path, contents):
        payload = self.build_inicial_payload()
        payload['contents'] = contents
        url = self.build_call_url(operation=self.edit_contents_operation, namespace=namespace, repository=repository,
                                  file_path=file_path)
        return self.post_url(url=url, payload=payload)

    def create_and_edit_contents_call(self, namespace, repository, file_path, contents):
        return [
            self.create_call(namespace=namespace, repository=repository, file_path=file_path, commit=False),
            self.edit_contents_call(namespace=namespace, repository=repository, file_path=file_path, contents=contents)
        ]


# to test: set test to True and run "python manage.py -c "import ideApp.git_server_http_endpoint"
test = False
if test:
    namespace = 'nishedcob3'
    repository = 'test2'
    file_path = 'folder/test2.py'

    # Example File Creation Call:
    file_consumer = FileGitSrvHTTPEpConsumer()
    file_create = file_consumer.create_call(namespace=namespace, repository=repository, file_path=file_path,
                                            commit=False)

    print('url: %s' % file_create.request.url)
    print('data: %s' % file_create.request.body)

    contents = "print('hello world')\n"

    # Example File Edit Call:
    file_edit = file_consumer.edit_contents_call(namespace=namespace, repository=repository, file_path=file_path,
                                                 contents=contents)

    print('url: %s' % file_edit.request.url)
    print('data: %s' % file_edit.request.body)

    file_path = 'folder/test3.py'

    file_create_and_edit = file_consumer.create_and_edit_contents_call(namespace=namespace, repository=repository,
                                                                       file_path=file_path, contents=contents)
    print("FILE CREATE")
    file_create = file_create_and_edit[0]
    print('url: %s' % file_create.request.url)
    print('data: %s' % file_create.request.body)

    print("FILE EDIT")
    file_edit = file_create_and_edit[1]
    print('url: %s' % file_edit.request.url)
    print('data: %s' % file_edit.request.body)
