class Config(object):
    """
        The /config endpoints create, update, delete and query central
        configurationentries registered with Consul. See the agent
        configuration for moreinformation on how to enable this
        functionality for centrally configuring services and
        configuration entries docs for a description of the
        configuration entries content.
        """

    def __init__(self, agent):
        self.agent = agent

    def put(self, data, dc=None, token=None, cas=None):
        """
            This endpoint creates or updates the given config entry.

            *dc* is the datacenter that this agent will communicate with. By
            default the datacenter of the host is used.

            *cas* is the current Consul index, suitable for making subsequent
            calls to wait for changes since this query was last run.

            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        token = token or self.agent.token

        if dc:
            params.append(("dc", dc))
        if token:
            headers["X-Consul-Token"] = token
        if cas:
            params.append(("cas", cas))

        if data:
            data = json.dumps(data)
        else:
            data = ""
        return self.agent.http.put(
            CB.json(), path="/v1/config", params=params, headers=headers, data=data
        )

    def get(self, kind, name, dc=None, token=None):
        """
            This endpoint returns a specific config entry.

            *dc* (string: "") - Specifies the datacenter to query. This will
            default to the datacenter of the agent being queried. This is
            specified as part of the URL as a query parameter

            *kind* (string: <required>) - Specifies the kind of the entry to
             read. This is specified as part of the URL.

            *name* (string: <required>) - Specifies the name of the entry to
             read. This is specified as part of the URL
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        token = token or self.agent.token
        path = "/v1/config/%s/%s" % (kind, name)

        if dc:
            params.append(("dc", dc))
        if token:
            headers["X-Consul-Token"] = token

        return self.agent.http.get(CB.json(), path=path, params=params, headers=headers)

    def list(self, kind, dc=None, token=None):
        """
            This endpoint returns all config entries of the given kind.

            *dc* (string: "") - Specifies the datacenter to query. This will
            default to the datacenter of the agent being queried. This is
            specified as part of the URL as a query parameter

            *kind* (string: <required>) - Specifies the kind of the entry to
             read. This is specified as part of the URL.
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        token = token or self.agent.token
        path = "/v1/config/%s" % kind

        if dc:
            params.append(("dc", dc))
        if token:
            headers["X-Consul-Token"] = token

        return self.agent.http.get(CB.json(), path=path, params=params, headers=headers)

    def delete(self, kind, name, dc=None, token=None):
        """
            This endpoint delete the given config entry.


            *dc* (string: "") - Specifies the datacenter to query. This will
            default to the datacenter of the agent being queried. This is
            specified as part of the URL as a query parameter

            *kind* (string: <required>) - Specifies the kind of the entry to
             read. This is specified as part of the URL.

            *name* (string: <required>) - Specifies the name of the entry to
             read. This is specified as part of the URL
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        token = token or self.agent.token
        path = "/v1/config/%s/%s" % (kind, name)

        if dc:
            params.append(("dc", dc))
        if token:
            headers["X-Consul-Token"] = token

        return self.agent.http.delete(
            CB.bool(), path=path, params=params, headers=headers
        )
