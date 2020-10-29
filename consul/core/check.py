class Check(object):
    """
    There are three different kinds of checks: script, http and ttl
    """

    @classmethod
    def script(klass, args, interval):
        """
        Run the script *args* every *interval* (e.g. "10s") to peform health
        check
        """
        if isinstance(args, six.string_types) or isinstance(args, six.binary_type):
            warnings.warn("Check.script should take a list of arg", DeprecationWarning)
            args = ["sh", "-c", args]
        return {"args": args, "interval": interval}

    @classmethod
    def http(
        klass,
        url,
        interval,
        timeout=None,
        deregister=None,
        header=None,
        tls_skip_verify=None,
    ):
        """
        Perform a HTTP GET against *url* every *interval* (e.g. "10s") to
        perform health check with an optional *timeout* and optional
        *deregister* after which a failing service will be automatically
        deregistered. Optional parameter *header* specifies headers sent in
        HTTP request. *header* parameter is in form of map of lists of
        strings, e.g. {"x-foo": ["bar", "baz"]}. Optional parameter
        *tls_skip_verify* allow to skip TLS certificate verification.
        """
        ret = {"http": url, "interval": interval}
        if timeout:
            ret["timeout"] = timeout
        if deregister:
            ret["DeregisterCriticalServiceAfter"] = deregister
        if header:
            ret["header"] = header
        if tls_skip_verify:
            ret["TLSSkipVerify"] = tls_skip_verify
        return ret

    @classmethod
    def tcp(klass, host, port, interval, timeout=None, deregister=None):
        """
        Attempt to establish a tcp connection to the specified *host* and
        *port* at a specified *interval* with optional *timeout* and optional
        *deregister* after which a failing service will be automatically
        deregistered.
        """
        ret = {
            "tcp": "{host:s}:{port:d}".format(host=host, port=port),
            "interval": interval,
        }
        if timeout:
            ret["timeout"] = timeout
        if deregister:
            ret["DeregisterCriticalServiceAfter"] = deregister
        return ret

    @classmethod
    def ttl(klass, ttl):
        """
        Set check to be marked as critical after *ttl* (e.g. "10s") unless the
        check is periodically marked as passing.
        """
        return {"ttl": ttl}

    @classmethod
    def docker(klass, container_id, shell, script, interval, deregister=None):
        """
        Invoke *script* packaged within a running docker container with
        *container_id* at a specified *interval* on the configured
        *shell* using the Docker Exec API.  Optional *register* after which a
        failing service will be automatically deregistered.
        """
        ret = {
            "docker_container_id": container_id,
            "shell": shell,
            "script": script,
            "interval": interval,
        }
        if deregister:
            ret["DeregisterCriticalServiceAfter"] = deregister
        return ret

    @classmethod
    def grpc(klass, grpc, interval, deregister=None):
        """
        grpc (string: "") - Specifies a gRPC check's endpoint that
        supports the standard gRPC health checking protocol.
        The state of the check will be updated at the given
        Interval by probing the configured endpoint. Add the
        service identifier after the gRPC check's endpoint in the
        following format to check for a specific service instead of
        the whole gRPC server /:service_identifier.
        """
        ret = {"GRPC": grpc, "Interval": interval}
        if deregister:
            ret["DeregisterCriticalServiceAfter"] = deregister
        return ret

    @classmethod
    def _compat(
        self,
        script=None,
        interval=None,
        ttl=None,
        http=None,
        timeout=None,
        deregister=None,
    ):

        if not script and not http and not ttl:
            return {}

        log.warning("DEPRECATED: use consul.Check.script/http/ttl to specify check")

        ret = {"check": {}}

        if script:
            assert interval and not (ttl or http)
            ret["check"] = {"script": script, "ttl": interval}
        if ttl:
            assert not (interval or script or http)
            ret["check"] = {"ttl": ttl}
        if http:
            assert interval and not (script or ttl)
            ret["check"] = {"http": http, "interval": interval}
        if timeout:
            assert http
            ret["check"]["timeout"] = timeout

        # if deregister:
        #     ret['check']['DeregisterCriticalServiceAfter'] = deregister

        return ret
