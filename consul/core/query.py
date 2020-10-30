import json

from .callback import CB

class Query(object):
    def __init__(self, agent):
        self.agent = agent

    def list(self, dc=None, token=None):
        """
            Lists all the active  queries. This is a privileged endpoint,
            therefore you will only be able to get the prepared queries
            which the token supplied has read privileges to.

            *dc* is the datacenter that this agent will communicate with. By
            default the datacenter of the host is used.

            *token* is an optional `ACL token`_ to apply to this request.
            """
        params = []
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if dc:
            params.append(("dc", dc))

        return self.agent.http.get(
            CB.json(), path="/v1/query", params=params, headers=headers
        )

    def _query_data(
        self,
        service=None,
        name=None,
        session=None,
        token=None,
        nearestn=None,
        datacenters=None,
        onlypassing=None,
        tags=None,
        ttl=None,
        regexp=None,
        near=None,
        nodemeta=None,
        servicemeta=None,
    ):
        """
            {
    "Service": "redis",
    "Failover": {
      "NearestN": 3,
      "Datacenters": ["dc1", "dc2"]
    },
    "Near": "node1",
    "OnlyPassing": false,
    "Tags": ["primary", "!experimental"],
    "NodeMeta": {"instance_type": "m3.large"},
    "ServiceMeta": {"environment": "production"}
  },
            """
        service_body = dict(
            [
                (k, v)
                for k, v in {
                    "Service": service,
                    "onlypassing": onlypassing,
                    "tags": tags,
                    "near": near,
                    "nodemeta": nodemeta,
                    "servicemeta": servicemeta,
                    "failover": dict(
                        [
                            (k, v)
                            for k, v in {
                                "nearestn": nearestn,
                                "datacenters": datacenters,
                            }.items()
                            if v is not None
                        ]
                    ),
                }.items()
                if v is not None
            ]
        )

        data = dict(
            [
                (k, v)
                for k, v in {
                    "name": name,
                    "session": session,
                    "token": token or self.agent.token,
                    "dns": {"ttl": ttl} if ttl is not None else None,
                    "template": dict(
                        [
                            (k, v)
                            for k, v in {
                                "type": "name_prefix_match",
                                "regexp": regexp,
                            }.items()
                            if v is not None
                        ]
                    ),
                    "service": service_body,
                }.items()
                if v is not None
            ]
        )
        return json.dumps(data)

    def create(
        self,
        service,
        name=None,
        dc=None,
        session=None,
        token=None,
        nearestn=None,
        datacenters=None,
        onlypassing=None,
        tags=None,
        ttl=None,
        regexp=None,
        near=None,
        nodemeta=None,
        servicemeta=None,
    ):
        """
            Creates a new query. This is a privileged endpoint, and
            requires a management token for a certain query name.*token* will
            override this client's default token.

            *service* is mandatory for new query. represent service name to
            query.

            *name* is an optional name for this query.

            *dc* is the datacenter that this agent will communicate with. By
            default the datacenter of the host is used.

            *token* is an optional `ACL token`_ to apply to this request.

            *nearestn* if set to a value greater than zero, then the query will
            be forwarded to up to NearestN other datacenters based on their
            estimated network round trip time using Network Coordinates from
            the WAN gossip pool.

            *datacenters* is a fixed list of remote datacenters to forward the
            query to if there are no healthy nodes in the local datacenter.

            *onlypassing* controls the behavior of the query's health check
            filtering.

            *tags* is a list of service tags to filter the query results.

            *ttl*  is a duration string that can use "s" as a suffix for
            seconds. It controls how the TTL is set when query results are
            served over DNS.

            *regexp* is optional for template this option is only supported
            in Consul 0.6.4 or later. The only option for type is
            name_prefix_match so if you want a query template with no regexp
            enter an empty string.

            For more information about query
            https://www.consul.io/docs/agent/http/query.html
            """
        path = "/v1/query"
        params = [] if dc is None else [("dc", dc)]
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        data = self._query_data(
            service,
            name,
            session,
            token,
            nearestn,
            datacenters,
            onlypassing,
            tags,
            ttl,
            regexp,
            near,
            nodemeta,
            servicemeta,
        )
        return self.agent.http.post(
            CB.json(), path, params=params, headers=headers, data=data
        )

    def update(
        self,
        query_id,
        service=None,
        name=None,
        dc=None,
        session=None,
        token=None,
        nearestn=None,
        datacenters=None,
        onlypassing=None,
        tags=None,
        ttl=None,
        regexp=None,
        near=None,
        nodemeta=None,
        servicemeta=None,
    ):
        """
            This endpoint will update a certain query

            *query_id* is the query id for update

            all the other setting remains the same as the query create method
            """
        path = "/v1/query/%s" % query_id
        params = []
        headers = {}
        if dc:
            params.append(("dc", dc))
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        data = self._query_data(
            service,
            name,
            session,
            token,
            nearestn,
            datacenters,
            onlypassing,
            tags,
            ttl,
            regexp,
            near,
            nodemeta,
            servicemeta,
        )
        return self.agent.http.put(
            CB.bool(), path, params=params, headers=headers, data=data
        )

    def get(self, query_id, token=None, dc=None):
        """
            This endpoint will return information about a certain query

            *query_id* the query id to retrieve information about

            *token* is an optional `ACL token`_ to apply to this request.

            *dc* is the datacenter that this agent will communicate with. By
            default the datacenter of the host is used.
            """
        params = []
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if dc:
            params.append(("dc", dc))
        return self.agent.http.get(
            CB.json(), path="/v1/query/%s" % query_id, params=params, headers=headers
        )

    def delete(self, query_id, token=None, dc=None):
        """
            This endpoint will delete certain query

            *query_id* the query id delete

            *token* is an optional `ACL token`_ to apply to this request.

            *dc* is the datacenter that this agent will communicate with. By
            default the datacenter of the host is used.
            """
        params = []
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if dc:
            params.append(("dc", dc))
        return self.agent.http.delete(
            CB.bool(), path="/v1/query/%s" % query_id, params=params, headers=headers
        )

    def execute(self, query, token=None, dc=None, near=None, limit=None):
        """
            This endpoint will execute certain query

            *query* name or query id to execute

            *token* is an optional `ACL token`_ to apply to this request.

            *dc* is the datacenter that this agent will communicate with. By
            default the datacenter of the host is used.

            *near* is a node name to sort the resulting list in ascending
            order based on the estimated round trip time from that node

            *limit* is used to limit the size of the list to the given number
            of nodes. This is applied after any sorting or shuffling.
            """
        params = []
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if dc:
            params.append(("dc", dc))
        if near:
            params.append(("near", near))
        if limit:
            params.append(("limit", limit))
        return self.agent.http.get(
            CB.json(),
            path="/v1/query/%s/execute" % query,
            params=params,
            headers=headers,
        )

    def explain(self, query, token=None, dc=None):
        """
            This endpoint shows a fully-rendered query for a given name

            *query* name to explain. This cannot be query id.

            *token* is an optional `ACL token`_ to apply to this request.

            *dc* is the datacenter that this agent will communicate with. By
            default the datacenter of the host is used.
            """
        params = []
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        if dc:
            params.append(("dc", dc))
        return self.agent.http.get(
            CB.json(),
            path="/v1/query/%s/explain" % query,
            params=params,
            headers=headers,
        )
