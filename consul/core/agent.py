import json

from .callback import CB
from .check import Check

class Agent(object):
    """
        The Agent endpoints are used to interact with a local Consul agent.
        Usually, services and checks are registered with an agent, which then
        takes on the burden of registering with the Catalog and performing
        anti-entropy to recover from outages.
        """

    def __init__(self, agent):
        self.agent = agent
        self.service = Agent.Service(agent)
        self.check = Agent.Check(agent)
        self.connect = Agent.Connect(agent)

    def self(self, token=None):
        """
            Returns configuration of the local agent and member information.
            """
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(CB.json(), path="/v1/agent/self", headers=headers)

    def services(self, token=None):
        """
            Returns all the services that are registered with the local agent.
            These services were either provided through configuration files, or
            added dynamically using the HTTP API. It is important to note that
            the services known by the agent may be different than those
            reported by the Catalog. This is usually due to changes being made
            while there is no leader elected. The agent performs active
            anti-entropy, so in most situations everything will be in sync
            within a few seconds.
            """
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(
            CB.json(), path="/v1/agent/services", headers=headers
        )

    def checks(self, token=None):
        """
            Returns all the checks that are registered with the local agent.
            These checks were either provided through configuration files, or
            added dynamically using the HTTP API. Similar to services,
            the checks known by the agent may be different than those
            reported by the Catalog. This is usually due to changes being made
            while there is no leader elected. The agent performs active
            anti-entropy, so in most situations everything will be in sync
            within a few seconds.
            """
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(CB.json(), path="/v1/agent/checks", headers=headers)

    def members(self, wan=False, token=None):
        """
            Returns all the members that this agent currently sees. This may
            vary by agent, use the nodes api of Catalog to retrieve a cluster
            wide consistent view of members.

            For agents running in server mode, setting *wan* to *True* returns
            the list of WAN members instead of the LAN members which is
            default.
            """
        params = []
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if wan:
            params.append(("wan", 1))
        return self.agent.http.get(
            CB.json(), path="/v1/agent/members", params=params, headers=headers
        )

    def maintenance(self, enable, reason=None, token=None):
        """
            The node maintenance endpoint can place the agent into
            "maintenance mode".

            *enable* is either 'true' or 'false'. 'true' enables maintenance
            mode, 'false' disables maintenance mode.

            *reason* is an optional string. This is simply to aid human
            operators.
            """

        params = []
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        params.append(("enable", enable))
        if reason:
            params.append(("reason", reason))

        return self.agent.http.put(
            CB.bool(), path="/v1/agent/maintenance", params=params, headers=headers
        )

    def join(self, address, wan=False, token=None):
        """
            This endpoint instructs the agent to attempt to connect to a
            given address.

            *address* is the ip to connect to.

            *wan* is either 'true' or 'false'. For agents running in server
            mode, 'true' causes the agent to attempt to join using the WAN
            pool. Default is 'false'.
            """

        params = []
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if wan:
            params.append(("wan", 1))

        return self.agent.http.put(
            CB.bool(),
            path="/v1/agent/join/%s" % address,
            params=params,
            headers=headers,
        )

    def force_leave(self, node, token=None):
        """
            This endpoint instructs the agent to force a node into the left
            state. If a node fails unexpectedly, then it will be in a failed
            state. Once in the failed state, Consul will attempt to reconnect,
            and the services and checks belonging to that node will not be
            cleaned up. Forcing a node into the left state allows its old
            entries to be removed.

            *node* is the node to change state for.
            """
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.put(
            CB.bool(), path="/v1/agent/force-leave/%s" % node, headers=headers
        )

    class Service(object):
        def __init__(self, agent):
            self.agent = agent

        def register(
            self,
            name,
            service_id=None,
            address=None,
            port=None,
            tags=None,
            check=None,
            token=None,
            meta=None,
            # *deprecated* use check parameter
            script=None,
            interval=None,
            ttl=None,
            http=None,
            timeout=None,
            enable_tag_override=False,
        ):
            """
                Add a new service to the local agent. There is more
                documentation on services
                `here <http://www.consul.io/docs/agent/services.html>`_.

                *name* is the name of the service.

                If the optional *service_id* is not provided it is set to
                *name*. You cannot have duplicate *service_id* entries per
                agent, so it may be necessary to provide one.

                *address* will default to the address of the agent if not
                provided.

                An optional health *check* can be created for this service is
                one of `Check.script`_, `Check.http`_, `Check.tcp`_,
                `Check.ttl`_ or `Check.docker`_.

                *token* is an optional `ACL token`_ to apply to this request.
                Note this call will return successful even if the token doesn't
                have permissions to register this service.

                *meta* specifies arbitrary KV metadata linked to the service
                formatted as {k1:v1, k2:v2}.

                *script*, *interval*, *ttl*, *http*, and *timeout* arguments
                are deprecated. use *check* instead.

                *enable_tag_override* is an optional bool that enable you
                to modify a service tags from servers(consul agent role server)
                Default is set to False.
                This option is only for >=v0.6.0 version on both agent and
                servers.
                for more information
                https://www.consul.io/docs/agent/services.html
                """

            payload = {}

            payload["name"] = name
            if enable_tag_override:
                payload["enabletagoverride"] = enable_tag_override
            if service_id:
                payload["id"] = service_id
            if address:
                payload["address"] = address
            if port:
                payload["port"] = port
            if tags:
                payload["tags"] = tags
            if meta:
                payload["meta"] = meta
            if check:
                payload["check"] = check

            else:
                payload.update(
                    Check._compat(
                        script=script,
                        interval=interval,
                        ttl=ttl,
                        http=http,
                        timeout=timeout,
                    )
                )

            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.put(
                CB.bool(),
                path="/v1/agent/service/register",
                headers=headers,
                data=json.dumps(payload),
            )

        def deregister(self, service_id, token=None):
            """
                Used to remove a service from the local agent. The agent will
                take care of deregistering the service with the Catalog. If
                there is an associated check, that is also deregistered.
                """
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.bool(),
                path="/v1/agent/service/deregister/%s" % service_id,
                headers=headers,
            )

        def maintenance(self, service_id, enable, reason=None, token=None):
            """
                The service maintenance endpoint allows placing a given service
                into "maintenance mode".

                *service_id* is the id of the service that is to be targeted
                for maintenance.

                *enable* is either 'true' or 'false'. 'true' enables
                maintenance mode, 'false' disables maintenance mode.

                *reason* is an optional string. This is simply to aid human
                operators.
                """

            params = [("enable", enable)]
            headers = {}

            token = token or self.agent.token
            if reason:
                params.append(("reason", reason))
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.bool(),
                path="/v1/agent/service/maintenance/{}".format(service_id),
                headers=headers,
                params=params,
            )

    class Check(object):
        def __init__(self, agent):
            self.agent = agent

        def register(
            self,
            name,
            check=None,
            check_id=None,
            notes=None,
            service_id=None,
            token=None,
            # *deprecated* use check parameter
            script=None,
            interval=None,
            ttl=None,
            http=None,
            timeout=None,
        ):
            """
                Register a new check with the local agent. More documentation
                on checks can be found `here
                <http://www.consul.io/docs/agent/checks.html>`_.

                *name* is the name of the check.

                *check* is one of `Check.script`_, `Check.http`_, `Check.tcp`_
                `Check.ttl`_ or `Check.docker`_ and is required.

                If the optional *check_id* is not provided it is set to *name*.
                *check_id* must be unique for this agent.

                *notes* is not used by Consul, and is meant to be human
                readable.

                Optionally, a *service_id* can be specified to associate a
                registered check with an existing service.

                *token* is an optional `ACL token`_ to apply to this request.
                Note this call will return successful even if the token doesn't
                have permissions to register this check.

                *script*, *interval*, *ttl*, *http*, and *timeout* arguments
                are deprecated. use *check* instead.

                Returns *True* on success.
                """
            payload = {"name": name}

            assert check or script or ttl or http, "check is required"

            if check:
                payload.update(check)

            else:
                payload.update(
                    Check._compat(
                        script=script,
                        interval=interval,
                        ttl=ttl,
                        http=http,
                        timeout=timeout,
                    )["check"]
                )

            if check_id:
                payload["id"] = check_id
            if notes:
                payload["notes"] = notes
            if service_id:
                payload["serviceid"] = service_id

            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.put(
                CB.bool(),
                path="/v1/agent/check/register",
                headers=headers,
                data=json.dumps(payload),
            )

        def deregister(self, check_id, token=None):
            """
                Remove a check from the local agent.
                """
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.bool(),
                path="/v1/agent/check/deregister/%s" % check_id,
                headers=headers,
            )

        def ttl_pass(self, check_id, notes=None, token=None):
            """
                Mark a ttl based check as passing. Optional notes can be
                attached to describe the status of the check.
                """
            params = []
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if notes:
                params.append(("note", notes))

            return self.agent.http.put(
                CB.bool(),
                path="/v1/agent/check/pass/%s" % check_id,
                params=params,
                headers=headers,
            )

        def ttl_fail(self, check_id, notes=None, token=None):
            """
                Mark a ttl based check as failing. Optional notes can be
                attached to describe why check is failing. The status of the
                check will be set to critical and the ttl clock will be reset.
                """
            params = []
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if notes:
                params.append(("note", notes))

            return self.agent.http.put(
                CB.bool(),
                path="/v1/agent/check/fail/%s" % check_id,
                params=params,
                headers=headers,
            )

        def ttl_warn(self, check_id, notes=None, token=None):
            """
                Mark a ttl based check with warning. Optional notes can be
                attached to describe the warning. The status of the
                check will be set to warn and the ttl clock will be reset.
                """
            params = []
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if notes:
                params.append(("note", notes))

            return self.agent.http.put(
                CB.bool(),
                path="/v1/agent/check/warn/%s" % check_id,
                params=params,
                headers=headers,
            )

    class Connect(object):
        def __init__(self, agent):
            self.agent = agent

        def authorize(self, target, client_cert_uri, client_cert_serial, token=None):
            payload = {
                "Target": target,
                "ClientCertURI": client_cert_uri,
                "ClientCertSerial": client_cert_serial,
            }
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.post(
                CB.json(),
                path="/v1/agent/connect/authorize",
                headers=headers,
                data=json.dumps(payload),
            )

        def root_certificates(self, token=None):
            """
                :param token:
                :return: returns the trusted certificate authority (CA)
                root certificates.
                """
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.get(
                CB.json(), path="/v1/agent/connect/ca/roots", headers=headers
            )

        def leaf_certificates(self, service, token=None):
            """
                :param token:
                :return: returns the leaf certificate representing
                a single service.
                """
            path = "/agent/connect/ca/leaf/%s" % service
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.get(CB.json(), path=path, headers=headers)
