class BaseHTTPClient(six.with_metaclass(abc.ABCMeta, object)):
    def __init__(
        self,
        host="127.0.0.1",
        port=8500,
        scheme="http",
        verify=True,
        cert=None,
        timeout=None,
    ):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.verify = verify
        self.base_uri = "%s://%s:%s" % (self.scheme, self.host, self.port)
        self.cert = cert
        self.timeout = timeout

    def uri(self, path, params=None):
        uri = self.base_uri + urllib.parse.quote(path, safe="/:")
        if params:
            uri = "%s?%s" % (uri, urllib.parse.urlencode(params))
        return uri

    @abc.abstractmethod
    def get(self, callback, path, params=None, headers=None):
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, callback, path, params=None, data="", headers=None):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, callback, path, params=None, data="", headers=None):
        raise NotImplementedError

    @abc.abstractmethod
    def post(self, callback, path, params=None, data="", headers=None):
        raise NotImplementedError
