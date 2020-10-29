class Operator(object):
    def __init__(self, agent):
        self.agent = agent
        self.autopilot = Consul.Operator.Autopilot(agent)
        self.keyring = Consul.Operator.Keyring(agent)
        self.raft = Consul.Operator.Raft(agent)

    def raft_config(self, token=None):
        """
            Returns raft configuration.
            """
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(
            CB.json(), path="/v1/operator/raft/configuration", headers=headers
        )

    class Autopilot:
        """
            doing Autopilot
            """

        def __init__(self, agent=None):
            self.agent = agent

        def configuration(self, stale=None, dc=None, token=None):
            path = "/v1/operator/autopilot/configuration"
            params = []
            headers = {}
            dc = dc or self.agent.dc
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if dc:
                params.append(("dc", dc))
            if stale:
                params.append(("stale", stale))
            return self.agent.http.get(
                CB.json(), path=path, params=params, headers=headers
            )

        def update(self, payload, cas=None, dc=None, token=None):
            path = "/v1/operator/autopilot/configuration"
            params = []
            headers = {}
            dc = dc or self.agent.dc
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if dc:
                params.append(("dc", dc))
            if cas:
                params.append(("cas", cas))
            return self.agent.http.put(
                CB.json(),
                path=path,
                params=params,
                headers=headers,
                data=json.dumps(payload),
            )

        def health(self, dc=None, token=None):
            path = "/v1/operator/autopilot/health"
            params = []
            headers = {}
            token = token or self.agent.token
            dc = dc or self.agent.dc
            if token:
                headers["X-Consul-Token"] = token
            if dc:
                params.append(("dc", dc))
            return self.agent.http.get(
                CB.json(), path=path, params=params, headers=headers
            )

    class Keyring:
        def __init__(self, agent=None):
            self.agent = agent

        def create(self, key, relay_factor=None, token=None):
            path = "/v1/operator/keyring"
            params = []
            headers = {}
            payload = {"Key": key}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if relay_factor:
                params.append(("relay-factor", relay_factor))
            return self.agent.http.post(
                CB.bool(),
                path=path,
                params=params,
                headers=headers,
                data=json.dumps(payload),
            )

        def update(self, key, relay_factor=None, token=None):
            path = "/v1/operator/keyring"
            params = []
            headers = {}
            payload = {"Key": key}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if relay_factor:
                params.append(("relay-factor", relay_factor))
            return self.agent.http.put(
                CB.bool(),
                path=path,
                params=params,
                headers=headers,
                data=json.dumps(payload),
            )

        def delete(self, key, token=None):
            path = "/v1/operator/keyring"
            headers = {}
            payload = {"Key": key}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.delete(
                CB.bool(), path=path, headers=headers, data=json.dumps(payload)
            )

        def list(self, relay_factor=None, local_only=None, token=None):
            params = []
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if relay_factor:
                params.append(("relay-factor", relay_factor))
            if local_only:
                params.append(("local-only", local_only))
            return self.agent.http.get(
                CB.json(), path="/v1/operator/keyring", params=params, headers=headers
            )

    class Raft:
        """
            Raft
            """

        def __init__(self, agent=None):
            self.agent = agent

        def configuration(self, dc=None, stale=None, token=None):
            path = "/v1/operator/raft/configuration"
            params = []
            headers = {}
            dc = dc or self.agent.dc
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if dc:
                params.append(("dc", dc))
            if stale:
                params.append(("stale", stale))

            return self.agent.http.get(
                CB.json(), path=path, params=params, headers=headers
            )

        def delete(self, raft_id=None, address=None, dc=None, token=None):
            """
                This endpoint removes the Consul server with given address from
                the Raft configuration.

                There are rare cases where a peer may be left behind in the
                Raft configuration even though the server is no longer
                present and known to the cluster. This endpoint can be used
                to remove the failed server so that it is no longer affects
                the Raft quorum.

                If ACLs are enabled, the client will need to supply an ACL
                Token with operator write privileges.
                """
            path = "/v1/operator/raft/peer"
            params = []
            headers = {}
            token = token or self.agent.token
            dc = dc or self.agent.dc
            assert (raft_id or address) and not (raft_id and address), (
                "raft_id or address there" " just and must be one"
            )

            if raft_id:
                params.append(("id", raft_id))
            else:
                params.append(("address", address))
            if token:
                headers["X-Consul-Token"] = token
            if dc:
                params.append(("dc", dc))
            return self.agent.http.delete(
                CB.bool(), path=path, params=params, headers=headers
            )
