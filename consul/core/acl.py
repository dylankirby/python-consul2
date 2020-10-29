import warnings

class ACL(object):
    def __init__(self, agent):
        self.agent = agent
        self.tokens = ACL.Tokens(agent)
        self.legacy_tokens = ACL.LegacyTokens(agent)
        self.policy = ACL.Policy(agent)
        self.roles = ACL.Roles(agent)
        self.auth_method = ACL.AuthMethod(agent)
        self.binding_rule = ACL.BindingRule(agent)

    def self(self, token=None):
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(
            CB.json(), path="/v1/acl/token/self", headers=headers
        )

    def list(self, token=None):
        """
            Lists all the active ACL tokens. This is a privileged endpoint, and
            requires a management token. *token* will override this client's
            default token.  An *ACLPermissionDenied* exception will be raised
            if a management token is not used.
            """
        warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(CB.json(), path="/v1/acl/list", headers=headers)

    def info(self, acl_id, token=None):
        """
            Returns the token information for *acl_id*.
            """
        warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(
            CB.json(one=True), path="/v1/acl/info/%s" % acl_id, headers=headers
        )

    def create(self, name=None, type="client", rules=None, acl_id=None, token=None):
        """
            Creates a new ACL token. This is a privileged endpoint, and
            requires a management token. *token* will override this client's
            default token.  An *ACLPermissionDenied* exception will be raised
            if a management token is not used.

            *name* is an optional name for this token.

            *type* is either 'management' or 'client'. A management token is
            effectively like a root user, and has the ability to perform any
            action including creating, modifying, and deleting ACLs. A client
            token can only perform actions as permitted by *rules*.

            *rules* is an optional `HCL`_ string for this `ACL Token`_ Rule
            Specification.

            Rules look like this::

                # Default all keys to read-only
                key "" {
                  policy = "read"
                }
                key "foo/" {
                  policy = "write"
                }
                key "foo/private/" {
                  # Deny access to the private dir
                  policy = "deny"
                }

            Returns the string *acl_id* for the new token.
            """
        warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token

        payload = {}
        if name:
            payload["Name"] = name
        if type:
            assert type in ("client", "management"), "type must be client or management"
            payload["Type"] = type
        if rules:
            assert isinstance(
                rules, str
            ), "Only HCL or JSON encoded strings supported for the moment"
            payload["Rules"] = rules
        if acl_id:
            payload["ID"] = acl_id

        if payload:
            data = json.dumps(payload)
        else:
            data = ""

        return self.agent.http.put(
            CB.json(is_id=True), path="/v1/acl/create", headers=headers, data=data
        )

    def update(self, acl_id, name=None, type=None, rules=None, token=None):
        """
            Updates the ACL token *acl_id*. This is a privileged endpoint, and
            requires a management token. *token* will override this client's
            default token. An *ACLPermissionDenied* exception will be raised if
            a management token is not used.

            *name* is an optional name for this token.

            *type* is either 'management' or 'client'. A management token is
            effectively like a root user, and has the ability to perform any
            action including creating, modifying, and deleting ACLs. A client
            token can only perform actions as permitted by *rules*.

            *rules* is an optional `HCL`_ string for this `ACL Token`_ Rule
            Specification.

            Returns the string *acl_id* of this token on success.
            """
        warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token

        payload = {"ID": acl_id}
        if name:
            payload["Name"] = name
        if type:
            assert type in ("client", "management"), "type must be client or management"
            payload["Type"] = type
        if rules:
            assert isinstance(
                rules, str
            ), "Only HCL or JSON encoded strings supported for the moment"
            payload["Rules"] = rules

        data = json.dumps(payload)

        return self.agent.http.put(
            CB.json(is_id=True), path="/v1/acl/update", headers=headers, data=data
        )

    def clone(self, acl_id, token=None):
        """
            Clones the ACL token *acl_id*. This is a privileged endpoint, and
            requires a management token. *token* will override this client's
            default token. An *ACLPermissionDenied* exception will be raised if
            a management token is not used.

            Returns the string of the newly created *acl_id*.
            """
        warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.put(
            CB.json(is_id=True), path="/v1/acl/clone/%s" % acl_id, headers=headers
        )

    def destroy(self, acl_id, token=None):
        """
            Destroys the ACL token *acl_id*. This is a privileged endpoint, and
            requires a management token. *token* will override this client's
            default token. An *ACLPermissionDenied* exception will be raised if
            a management token is not used.

            Returns *True* on success.
            """
        warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.put(
            CB.json(), path="/v1/acl/destroy/%s" % acl_id, headers=headers
        )

    def bootstrap(self, token=None):
        """
            This endpoint does a special one-time bootstrap of the ACL system,
            making the first management token if the acl.tokens.master
            configuration entry is not specified in the Consul server
            configuration and if the cluster has not been bootstrapped
            previously. This is available in Consul 0.9.1 and later, and
            requires all Consul servers to be upgraded in order to operate.
            :param token:
            :return:
            """
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.put(CB.json(), path="/v1/acl/bootstrap", headers=headers)

    def replication(self, dc=None, token=None):
        """
            This endpoint returns the status of the ACL replication
            processes in the datacenter. This is intended to be used
            by operators or by automation checking to discover the
            health of ACL replication.
            :param dc:
            :header token:
            :return:
            """
        params = []
        headers = {}
        token = token or self.agent.token
        dc = dc or self.agent.dc
        if token:
            headers["X-Consul-Token"] = token
        if dc:
            params.append(("dc", dc))
        return self.agent.http.get(
            CB.json(), path="/v1/acl/replication", params=params, headers=headers
        )

    def create_translate(self, payload, token=None):
        """
            This endpoint translates the legacy rule syntax into the latest
            syntax. It is intended to be used by operators managing Consul's
            ACLs and performing legacy token to new policy migrations.
            *payload*

            agent "" {
                policy = "read"
            }

            :return:
            """
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.post(
            CB.binary(), path="/v1/acl/rules/translate", headers=headers, data=payload
        )

    def get_translate(self, accessor_id, token=None):
        """
            This endpoint translates the legacy rules embedded within a legacy
            ACL into the latest syntax.
            :param accessor_id:
            :param token:
            :return:
            """
        path = "/v1/acl/rules/translate/%s" % accessor_id
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(CB.json(), path=path, headers=headers)

    def login(self, auth_method, bearer_token, meta=None, token=None):
        payload = {"AuthMethod": auth_method, "BearerToken": bearer_token}
        if meta:
            payload["Meta"] = meta
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.post(
            CB.json(), path="/v1/acl/login", headers=headers, data=json.dumps(payload)
        )

    def logout(self, token=None):
        headers = {}
        token = token or self.agent.token
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.post(CB.json(), path="/v1/acl/logout", headers=headers)

    class Tokens(object):
        """
            The APIs are available in Consul versions 1.4.0 and later.
            """

        def __init__(self, agent=None):
            self.agent = agent

        def create(self, payload, token=None):
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(),
                path="/v1/acl/token",
                headers=headers,
                data=json.dumps(payload),
            )

        def get(self, accessor_id, token=None):
            path = "/v1/acl/token/%s" % accessor_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def self(self, token=None):
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(
                CB.json(), path="/v1/acl/token/self", headers=headers
            )

        def update(self, payload, accessor_id, token=None):
            path = "/v1/acl/token/%s" % accessor_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(), path=path, headers=headers, data=json.dumps(payload)
            )

        def clone(self, description="", token=None, accessor_id=None):
            payload = {"Description": description}
            path = "/v1/acl/token/%s/clone" % accessor_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(), path=path, headers=headers, data=json.dumps(payload)
            )

        def delete(self, accessor_id, token=None):
            path = "/v1/acl/token/%s" % accessor_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.delete(CB.bool(), path=path, headers=headers)

        def list(self, policy=None, role=None, authmethod=None, token=None):
            params = []
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            if policy:
                params.append(("policy", policy))
            if role:
                params.append(("role", role))
            if authmethod:
                params.append(("authmethod", authmethod))
            return self.agent.http.get(
                CB.json(), path="/v1/acl/tokens", params=params, headers=headers
            )

    class LegacyTokens(object):
        def __init__(self, agent=None):
            warnings.warn("Consul 1.4.0 deprecates the legacy ACL.", DeprecationWarning)
            self.agent = agent

        def list(self, token=None):
            warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
            params = []
            token = token or self.agent.token
            if token:
                params.append(("token", token))
            return self.agent.http.get(CB.json(), path="/v1/acl/list", params=params)

        def info(self, acl_id, token=None):
            """
                Returns the token information for *acl_id*.
                """
            warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
            params = []
            token = token or self.agent.token
            if token:
                params.append(("token", token))
            return self.agent.http.get(
                CB.json(one=True), path="/v1/acl/info/%s" % acl_id, params=params
            )

        def create(self, name=None, type="client", rules=None, acl_id=None, token=None):
            warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
            params = []
            token = token or self.agent.token
            if token:
                params.append(("token", token))

            payload = {}
            if name:
                payload["Name"] = name
            if type:
                assert type in (
                    "client",
                    "management",
                ), "type must be client or management"
                payload["Type"] = type
            if rules:
                assert isinstance(rules, str), (
                    "Only HCL or JSON encoded strings" " supported for the moment"
                )
                payload["Rules"] = rules
            if acl_id:
                payload["ID"] = acl_id

            if payload:
                data = json.dumps(payload)
            else:
                data = ""

            return self.agent.http.put(
                CB.json(is_id=True), path="/v1/acl/create", params=params, data=data
            )

        def update(self, acl_id, name=None, type=None, rules=None, token=None):
            warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
            params = []
            token = token or self.agent.token
            if token:
                params.append(("token", token))

            payload = {"ID": acl_id}
            if name:
                payload["Name"] = name
            if type:
                assert type in (
                    "client",
                    "management",
                ), "type must be client or management"
                payload["Type"] = type
            if rules:
                assert isinstance(rules, str), (
                    "Only HCL or JSON encoded strings" " supported for the moment"
                )
                payload["Rules"] = rules

            data = json.dumps(payload)

            return self.agent.http.put(
                CB.json(is_id=True), path="/v1/acl/update", params=params, data=data
            )

        def clone(self, acl_id, token=None):
            warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
            params = []
            token = token or self.agent.token
            if token:
                params.append(("token", token))
            return self.agent.http.put(
                CB.json(is_id=True), path="/v1/acl/clone/%s" % acl_id, params=params
            )

        def destroy(self, acl_id, token=None):
            """
                Returns *True* on success.
                """
            warnings.warn("Consul 1.4.0 deprecated", DeprecationWarning)
            params = []
            token = token or self.agent.token
            if token:
                params.append(("token", token))
            return self.agent.http.put(
                CB.bool(), path="/v1/acl/destroy/%s" % acl_id, params=params
            )

    class Policy(object):
        def __init__(self, agent=None):
            self.agent = agent

        def create(
            self, name, description=None, rules=None, datacenters=None, token=None
        ):

            payload = {"Name": name}
            if description:
                payload["Description"] = description
            if rules:
                payload["Rules"] = rules
            if datacenters:
                payload["Datacenters"] = datacenters

            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.put(
                CB.json(),
                path="/v1/acl/policy",
                headers=headers,
                data=json.dumps(payload),
            )

        def get(self, policy_id=None, name=None, token=None):
            path = "/v1/acl/policy/%s" % (policy_id or "name/" + name)
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def update(
            self,
            policy_id,
            name,
            description=None,
            rules=None,
            datacenters=None,
            token=None,
        ):

            payload = {"Name": name}
            if description:
                payload["Description"] = description
            if rules:
                payload["Rules"] = rules
            if datacenters:
                payload["Datacenters"] = datacenters

            path = "/v1/acl/policy/%s" % policy_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(), path=path, headers=headers, data=json.dumps(payload)
            )

        def delete(self, policy_id, token=None):
            path = "/v1/acl/policy/%s" % policy_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.delete(CB.bool(), path=path, headers=headers)

        def list(self, token=None):
            path = "/v1/acl/policies"
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

    class Roles(object):
        def __init__(self, agent=None):
            self.agent = agent

        def create(self, payload, token=None):
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(),
                path="/v1/acl/role",
                headers=headers,
                data=json.dumps(payload),
            )

        def get(self, role_id, token=None):
            path = "/v1/acl/role/%s" % role_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def get_by_name(self, role_name, token=None):
            path = "/v1/acl/role/name/%s" % role_name
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def update(self, payload, role_id, token=None):
            path = "/v1/acl/role/%s" % role_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(), path=path, headers=headers, data=json.dumps(payload)
            )

        def delete(self, role_id, token=None):
            path = "/v1/acl/role/%s" % role_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.delete(CB.bool(), path=path, headers=headers)

        def list(self, policy=None, token=None):
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token

            return self.agent.http.get(CB.json(), path="/v1/acl/roles", headers=headers)

    class AuthMethod(object):
        def __init__(self, agent=None):
            self.agent = agent

        def create(self, payload, token=None):
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(),
                path="/v1/acl/auth-method",
                headers=headers,
                data=json.dumps(payload),
            )

        def get(self, auth_method_name, token=None):
            path = "/v1/acl/auth-method/%s" % auth_method_name
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def update(self, payload, name, token=None):
            path = "/v1/acl/auth-method/%s" % name
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(), path=path, headers=headers, data=json.dumps(payload)
            )

        def delete(self, name, token=None):
            path = "/v1/acl/auth-method/%s" % name
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.delete(CB.bool(), path=path, headers=headers)

        def list(self, token=None):
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(
                CB.json(), path="/v1/acl/auth-methods", headers=headers
            )

    class BindingRule(object):
        def __init__(self, agent=None):
            self.agent = agent

        def create(self, payload, token=None):
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(),
                path="/v1/acl/binding-rule",
                headers=headers,
                data=json.dumps(payload),
            )

        def get(self, binding_rule_id, token=None):
            path = "/v1/acl/binding-rule/%s" % binding_rule_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(CB.json(), path=path, headers=headers)

        def update(self, payload, binding_rule_id, token=None):
            path = "/v1/acl/binding-rule/%s" % binding_rule_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.put(
                CB.json(), path=path, headers=headers, data=json.dumps(payload)
            )

        def delete(self, binding_rule_id, token=None):
            path = "/v1/acl/binding-rule/%s" % binding_rule_id
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.delete(CB.bool(), path=path, headers=headers)

        def list(self, token=None):
            headers = {}
            token = token or self.agent.token
            if token:
                headers["X-Consul-Token"] = token
            return self.agent.http.get(
                CB.json(), path="/v1/acl/binding-rules", headers=headers
            )
