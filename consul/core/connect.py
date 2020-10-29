class Connect(object):
    """
        The */connect* endpoints provide access to Connect-related
        operations for  intentions and the certificate authority.

        There are also Connect-related endpoints in the Agent and Catalog APIs.
        For example, the API for requesting a TLS certificate for a service is
        part of the agent APIs. And the catalog API has an endpoint for finding
        all Connect-capable services in the catalog..
        """

    def __init__(self, agent):
        self.agent = agent
        self.certificates = Consul.Connect.Certificates(agent)
        self.intentions = Consul.Connect.Intentions(agent)

    class Certificates:
        """
            This endpoint returns the current list of trusted CA root
            certificates in the cluster.
            """

        def __init__(self, agent):
            self.agent = agent

        def list(self, token=None):
            path = "/v1/connect/ca/roots"
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def current(self, token=None):
            """
                This endpoint returns the current CA configuration.
                """
            path = "/v1/connect/ca/configuration"
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def put(self, config, provider, token=None):
            """
                This endpoint updates the configuration for the CA.
                If this results in a new root certificate being used,
                the Root Rotation process will be triggered.

                *Provider*
                *Config*
                dict::

                {
                    "LeafCertTTL": "72h",
                    "PrivateKey": "-----BEGIN RSA PRIVATE KEY-----...",
                    "RootCert": "-----BEGIN CERTIFICATE-----...",
                    "RotationPeriod": "2160h"
                 }
                :return:
                """
            path = "/v1/connect/ca/configuration"
            payload = {"Provider": provider, "Config": config}
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.bool(), path=path, headers=headers, data=json.dumps(payload)
            )

    class Intentions:
        """
            This endpoint returns the current list of trusted CA root
            certificates in the cluster.
            """

        def __init__(self, agent):
            self.agent = agent

        def create(
            self,
            source_name,
            destination_name,
            source_type,
            action,
            description=None,
            meta=None,
            token=None,
        ):
            """
                :param source_name:
                :param destination_name:
                :param source_type:
                :param action:
                :param description:
                :param meta:
                :param token:
                :return: intentions id
                """
            path = "/v1/connect/intentions"
            payload = {
                "SourceName": source_name,
                "DestinationName": destination_name,
                "SourceType": source_type,
                "Action": action,
            }
            if description:
                payload["Description"] = description
            if meta:
                payload["Meta"] = meta
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.post(
                CB.json(), path=path, headers=headers, data=json.dumps(payload)
            )

        def get(self, intention_id, token=None):
            path = "/v1/connect/intentions/%s" % intention_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def list(self, token=None):
            path = "/v1/connect/intentions"
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def put(
            self,
            intention_id,
            token=None,
            source_name=None,
            destination_name=None,
            source_type=None,
            action=None,
            description=None,
            meta=None,
        ):
            """
                :param intention_id:
                :param token:
                :param source_name:
                :param destination_name:
                :param source_type:
                :param action:
                :param description:
                :param meta:
                :return:
                """
            path = "/v1/connect/intentions/%s" % intention_id
            payload = {}
            if source_name:
                payload["SourceName"] = source_name
            if destination_name:
                payload["DestinationName"] = destination_name
            if source_type:
                payload["SourceType"] = source_type
            if action:
                payload["Action"] = action
            if description:
                payload["Description"] = description
            if meta:
                payload["Meta"] = meta
            headers = {}
            token = token or self.agent.token
            if payload:
                data = json.dumps(payload)
            else:
                data = ""
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(CB.bool(), path=path, headers=headers, data=data)

        def delete(self, intention_id, token=None):
            path = "/v1/connect/intentions/%s" % intention_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.delete(CB.bool(), path=path, headers=headers)

        def check(self, source, destination, token=None):
            path = "/v1/connect/intentions/check"
            params = []
            headers = {}
            token = token or self.agent.token
            params.append(("source", source))
            params.append(("destination", destination))
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(
                CB.json(), path=path, params=params, headers=headers
            )

        def list_match(self, by, name, token=None):
            path = "/v1/connect/intentions/match"
            params = []
            headers = {}
            token = token or self.agent.token
            params.append(("by", by))
            params.append(("name", name))
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(
                CB.json(), path=path, params=params, headers=headers
            )
