class Health(object):
    # TODO: All of the health endpoints support all consistency modes
    def __init__(self, agent):
        self.agent = agent

    def service(
        self,
        service,
        index=None,
        wait=None,
        passing=None,
        tag=None,
        dc=None,
        near=None,
        token=None,
        node_meta=None,
    ):
        """
            Returns a tuple of (*index*, *nodes*)

            *index* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            *wait* the maximum duration to wait (e.g. '10s') to retrieve
            a given index. this parameter is only applied if *index* is also
            specified. the wait time by default is 5 minutes.

            *nodes* are the nodes providing the given service.

            Calling with *passing* set to True will filter results to only
            those nodes whose checks are currently passing.

            Calling with *tag* will filter the results by tag.

            *dc* is the datacenter of the node and defaults to this agents
            datacenter.

            *near* is a node name to sort the resulting list in ascending
            order based on the estimated round trip time from that node

            *token* is an optional `ACL token`_ to apply to this request.

            *node_meta* is an optional meta data used for filtering, a
            dictionary formatted as {k1:v1, k2:v2}.
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        token = token or self.agent.token

        if index:
            params.append(("index", index))
            if wait:
                params.append(("wait", wait))
        if passing:
            params.append(("passing", "1"))
        if tag is not None:
            params.append(("tag", tag))
        if dc:
            params.append(("dc", dc))
        if near:
            params.append(("near", near))
        if token:
            headers["X-Consul-Token"] = token
        if node_meta:
            for nodemeta_name, nodemeta_value in node_meta.items():
                params.append(
                    ("node-meta", "{0}:{1}".format(nodemeta_name, nodemeta_value))
                )
        return self.agent.http.get(
            CB.json(index=True),
            path="/v1/health/service/%s" % service,
            params=params,
            headers=headers,
        )

    def checks(
        self,
        service,
        index=None,
        wait=None,
        dc=None,
        near=None,
        token=None,
        node_meta=None,
    ):
        """
            Returns a tuple of (*index*, *checks*) with *checks* being the
            checks associated with the service.

            *service* is the name of the service being checked.

            *index* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            *wait* the maximum duration to wait (e.g. '10s') to retrieve
            a given index. this parameter is only applied if *index* is also
            specified. the wait time by default is 5 minutes.

            *dc* is the datacenter of the node and defaults to this agents
            datacenter.

            *near* is a node name to sort the resulting list in ascending
            order based on the estimated round trip time from that node

            *token* is an optional `ACL token`_ to apply to this request.

            *node_meta* is an optional meta data used for filtering, a
            dictionary formatted as {k1:v1, k2:v2}.
            """
        params = []
        headers = {}
        if index:
            params.append(("index", index))
            if wait:
                params.append(("wait", wait))
        dc = dc or self.agent.dc
        if dc:
            params.append(("dc", dc))
        if near:
            params.append(("near", near))
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if node_meta:
            for nodemeta_name, nodemeta_value in node_meta.items():
                params.append(
                    ("node-meta", "{0}:{1}".format(nodemeta_name, nodemeta_value))
                )
        return self.agent.http.get(
            CB.json(index=True),
            path="/v1/health/checks/%s" % service,
            params=params,
            headers=headers,
        )

    def state(
        self,
        name,
        index=None,
        wait=None,
        dc=None,
        near=None,
        token=None,
        node_meta=None,
    ):
        """
            Returns a tuple of (*index*, *nodes*)

            *name* is a supported state. From the Consul docs:

                The supported states are any, unknown, passing, warning, or
                critical. The any state is a wildcard that can be used to
                return all checks.

            *index* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            *wait* the maximum duration to wait (e.g. '10s') to retrieve
            a given index. this parameter is only applied if *index* is also
            specified. the wait time by default is 5 minutes.

            *dc* is the datacenter of the node and defaults to this agents
            datacenter.

            *near* is a node name to sort the resulting list in ascending
            order based on the estimated round trip time from that node

            *token* is an optional `ACL token`_ to apply to this request.

            *node_meta* is an optional meta data used for filtering, a
            dictionary formatted as {k1:v1, k2:v2}.

            *nodes* are the nodes providing the given service.
            """
        assert name in ["any", "unknown", "passing", "warning", "critical"]
        params = []
        headers = {}
        if index:
            params.append(("index", index))
            if wait:
                params.append(("wait", wait))
        dc = dc or self.agent.dc
        token = token or self.agent.token

        if dc:
            params.append(("dc", dc))
        if near:
            params.append(("near", near))
        if token:
            headers["X-Consul-Token"] = token
        if node_meta:
            for nodemeta_name, nodemeta_value in node_meta.items():
                params.append(
                    ("node-meta", "{0}:{1}".format(nodemeta_name, nodemeta_value))
                )
        return self.agent.http.get(
            CB.json(index=True),
            path="/v1/health/state/%s" % name,
            params=params,
            headers=headers,
        )

    def node(self, node, index=None, wait=None, dc=None, token=None):
        """
            Returns a tuple of (*index*, *checks*)

            *index* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            *wait* the maximum duration to wait (e.g. '10s') to retrieve
            a given index. this parameter is only applied if *index* is also
            specified. the wait time by default is 5 minutes.

            *dc* is the datacenter of the node and defaults to this agents
            datacenter.

            *token* is an optional `ACL token`_ to apply to this request.

            *nodes* are the nodes providing the given service.
            """
        params = []
        headers = {}
        if index:
            params.append(("index", index))
            if wait:
                params.append(("wait", wait))
        dc = dc or self.agent.dc
        if dc:
            params.append(("dc", dc))
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token

        return self.agent.http.get(
            CB.json(index=True),
            path="/v1/health/node/%s" % node,
            params=params,
            headers=headers,
        )
