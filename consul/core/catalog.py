import json

from .callback import CB

class Catalog(object):
    def __init__(self, agent):
        self.agent = agent

    def register(
        self,
        node,
        address,
        service=None,
        skipnodeupdate=False,
        check=None,
        dc=None,
        token=None,
        node_meta=None,
    ):
        """
            A low level mechanism for directly registering or updating entries
            in the catalog. It is usually recommended to use
            agent.service.register and agent.check.register, as they are
            simpler and perform anti-entropy.

            *node* is the name of the node to register.

            *address* is the ip of the node.

            *service* is an optional service to register. if supplied this is a
            dict::

                {
                    "Service": "redis",
                    "ID": "redis1",
                    "Tags": [
                        "master",
                        "v1"
                    ],
                    "Port": 8000
                }

            where

                *Service* is required and is the name of the service

                *ID* is optional, and will be set to *Service* if not provided.
                Note *ID* must be unique for the given *node*.

                *Tags* and *Port* are optional.

            *skipnodeupdate* is an optional boolean which, when set to True,
            skips updating the node's information during registration. By
            default, it is set to False. For information on this parameter, see
            `here <https://www.consul.io/api-docs/catalog#skipnodeupdate`_.

            *check* is an optional check to register. if supplied this is a
            dict::

                {
                    "Node": "foobar",
                    "CheckID": "service:redis1",
                    "Name": "Redis health check",
                    "Notes": "Script based health check",
                    "Status": "passing",
                    "ServiceID": "redis1"
                }

            *dc* is the datacenter of the node and defaults to this agents
            datacenter.

            *token* is an optional `ACL token`_ to apply to this request.

            *node_meta* is an optional meta data used for filtering, a
            dictionary formatted as {k1:v1, k2:v2}.

            This manipulates the health check entry, but does not setup a
            script or TTL to actually update the status. The full documentation
            is `here <https://consul.io/docs/agent/http.html#catalog>`_.

            Returns *True* on success.
            """
        data = {"node": node, "address": address}
        params = []
        headers = {}
        dc = dc or self.agent.dc
        if dc:
            data["datacenter"] = dc
        if service:
            data["service"] = service
        if skipnodeupdate:
            data["skipnodeupdate"] = True
        if check:
            data["check"] = check
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if node_meta:
            nm = {}
            for nodemeta_name, nodemeta_value in node_meta.items():
                nm[nodemeta_name] = nodemeta_value
            data["NodeMeta"] = nm
        return self.agent.http.put(
            CB.bool(),
            path="/v1/catalog/register",
            data=json.dumps(data),
            params=params,
            headers=headers,
        )

    def deregister(self, node, service_id=None, check_id=None, dc=None, token=None):
        """
            A low level mechanism for directly removing entries in the catalog.
            It is usually recommended to use the agent APIs, as they are
            simpler and perform anti-entropy.

            *node* and *dc* specify which node on which datacenter to remove.
            If *service_id* and *check_id* are not provided, all associated
            services and checks are deleted. Otherwise only one of *service_id*
            and *check_id* should be provided and only that service or check
            will be removed.

            *token* is an optional `ACL token`_ to apply to this request.

            Returns *True* on success.
            """
        assert not (service_id and check_id)
        data = {"node": node}
        params = []
        headers = {}
        dc = dc or self.agent.dc
        token = token or self.agent.token

        if dc:
            data["datacenter"] = dc
        if service_id:
            data["serviceid"] = service_id
        if check_id:
            data["checkid"] = check_id
        if token:
            headers["X-Consul-Token"] = token

        return self.agent.http.put(
            CB.bool(),
            path="/v1/catalog/deregister",
            params=params,
            headers=headers,
            data=json.dumps(data),
        )

    def datacenters(self):
        """
            Returns all the datacenters that are known by the Consul server.
            """
        return self.agent.http.get(CB.json(), path="/v1/catalog/datacenters")

    def nodes(
        self,
        index=None,
        wait=None,
        consistency=None,
        dc=None,
        near=None,
        token=None,
        node_meta=None,
    ):
        """
            Returns a tuple of (*index*, *nodes*) of all nodes known
            about in the *dc* datacenter. *dc* defaults to the current
            datacenter of this agent.

            *index* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            *wait* the maximum duration to wait (e.g. '10s') to retrieve
            a given index. this parameter is only applied if *index* is also
            specified. the wait time by default is 5 minutes.

            *near* is a node name to sort the resulting list in ascending
            order based on the estimated round trip time from that node

            *consistency* can be either 'default', 'consistent' or 'stale'. if
            not specified *consistency* will the consistency level this client
            was configured with.

            *token* is an optional `ACL token`_ to apply to this request.

            *node_meta* is an optional meta data used for filtering, a
            dictionary formatted as {k1:v1, k2:v2}.

            The response looks like this::

                (index, [
                    {
                        "Node": "baz",
                        "Address": "10.1.10.11"
                    },
                    {
                        "Node": "foobar",
                        "Address": "10.1.10.12"
                    }
                ])
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        if dc:
            params.append(("dc", dc))
        if index:
            params.append(("index", index))
            if wait:
                params.append(("wait", wait))
        if near:
            params.append(("near", near))
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        consistency = consistency or self.agent.consistency
        if consistency in ("consistent", "stale"):
            params.append((consistency, "1"))
        if node_meta:
            for nodemeta_name, nodemeta_value in node_meta.items():
                params.append(
                    ("node-meta", "{0}:{1}".format(nodemeta_name, nodemeta_value))
                )
        return self.agent.http.get(
            CB.json(index=True),
            path="/v1/catalog/nodes",
            params=params,
            headers=headers,
        )

    def services(
        self,
        index=None,
        wait=None,
        consistency=None,
        dc=None,
        token=None,
        node_meta=None,
    ):
        """
            Returns a tuple of (*index*, *services*) of all services known
            about in the *dc* datacenter. *dc* defaults to the current
            datacenter of this agent.

            *index* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            *wait* the maximum duration to wait (e.g. '10s') to retrieve
            a given index. this parameter is only applied if *index* is also
            specified. the wait time by default is 5 minutes.

            *consistency* can be either 'default', 'consistent' or 'stale'. if
            not specified *consistency* will the consistency level this client
            was configured with.

            *token* is an optional `ACL token`_ to apply to this request.

            *node_meta* is an optional meta data used for filtering, a
            dictionary formatted as {k1:v1, k2:v2}.

            The response looks like this::

                (index, {
                    "consul": [],
                    "redis": [],
                    "postgresql": [
                        "master",
                        "slave"
                    ]
                })

            The main keys are the service names and the list provides all the
            known tags for a given service.
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        if dc:
            params.append(("dc", dc))
        if index:
            params.append(("index", index))
            if wait:
                params.append(("wait", wait))
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        consistency = consistency or self.agent.consistency
        if consistency in ("consistent", "stale"):
            params.append((consistency, "1"))
        if node_meta:
            for nodemeta_name, nodemeta_value in node_meta.items():
                params.append(
                    ("node-meta", "{0}:{1}".format(nodemeta_name, nodemeta_value))
                )
        return self.agent.http.get(
            CB.json(index=True),
            path="/v1/catalog/services",
            params=params,
            headers=headers,
        )

    def node(self, node, index=None, wait=None, consistency=None, dc=None, token=None):
        """
            Returns a tuple of (*index*, *services*) of all services provided
            by *node*.

            *index* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            *wait* the maximum duration to wait (e.g. '10s') to retrieve
            a given index. this parameter is only applied if *index* is also
            specified. the wait time by default is 5 minutes.

            *consistency* can be either 'default', 'consistent' or 'stale'. if
            not specified *consistency* will the consistency level this client
            was configured with.

            *dc* is the datacenter of the node and defaults to this agents
            datacenter.

            *token* is an optional `ACL token`_ to apply to this request.

            The response looks like this::

                (index, {
                    "Node": {
                        "Node": "foobar",
                        "Address": "10.1.10.12"
                    },
                    "Services": {
                        "consul": {
                            "ID": "consul",
                            "Service": "consul",
                            "Tags": null,
                            "Port": 8300
                        },
                        "redis": {
                            "ID": "redis",
                            "Service": "redis",
                            "Tags": [
                                "v1"
                            ],
                            "Port": 8000
                        }
                    }
                })
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        if dc:
            params.append(("dc", dc))
        if index:
            params.append(("index", index))
            if wait:
                params.append(("wait", wait))
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        consistency = consistency or self.agent.consistency
        if consistency in ("consistent", "stale"):
            params.append((consistency, "1"))
        return self.agent.http.get(
            CB.json(index=True),
            path="/v1/catalog/node/%s" % node,
            params=params,
            headers=headers,
        )

    def service(
        self,
        service,
        index=None,
        wait=None,
        tag=None,
        consistency=None,
        dc=None,
        near=None,
        token=None,
        node_meta=None,
    ):
        """
            Returns a tuple of (*index*, *nodes*) of the nodes providing
            *service* in the *dc* datacenter. *dc* defaults to the current
            datacenter of this agent.

            *index* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            *wait* the maximum duration to wait (e.g. '10s') to retrieve
            a given index. this parameter is only applied if *index* is also
            specified. the wait time by default is 5 minutes.

            If *tag* is provided, the list of nodes returned will be filtered
            by that tag.

            *near* is a node name to sort the resulting list in ascending
            order based on the estimated round trip time from that node

            *consistency* can be either 'default', 'consistent' or 'stale'. if
            not specified *consistency* will the consistency level this client
            was configured with.

            *token* is an optional `ACL token`_ to apply to this request.

            *node_meta* is an optional meta data used for filtering, a
            dictionary formatted as {k1:v1, k2:v2}.

            The response looks like this::

                (index, [
                    {
                        "Node": "foobar",
                        "Address": "10.1.10.12",
                        "ServiceID": "redis",
                        "ServiceName": "redis",
                        "ServiceTags": null,
                        "ServicePort": 8000
                    }
                ])
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        if dc:
            params.append(("dc", dc))
        if tag:
            params.append(("tag", tag))
        if index:
            params.append(("index", index))
            if wait:
                params.append(("wait", wait))
        if near:
            params.append(("near", near))
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        consistency = consistency or self.agent.consistency
        if consistency in ("consistent", "stale"):
            params.append((consistency, "1"))
        if node_meta:
            for nodemeta_name, nodemeta_value in node_meta.items():
                params.append(
                    ("node-meta", "{0}:{1}".format(nodemeta_name, nodemeta_value))
                )
        return self.agent.http.get(
            CB.json(index=True),
            path="/v1/catalog/service/%s" % service,
            params=params,
            headers=headers,
        )
