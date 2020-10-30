from .callback import CB

class Snapshot(object):
    def __init__(self, agent):
        self.agent = agent

    def get(self, dc=None, stale=None, token=None):
        """
            *dc* Specifies the datacenter to query. This will default
             to the datacenter of the agent being queried.
            *stale* Specifies that any follower may reply. By default
             requests are forwarded to the leade
            Returns gzipped snapshot of current consul cluster
            """
        params = []
        headers = {}
        dc = dc or self.agent.dc
        token = token or self.agent.token

        if dc:
            params.append(("dc", dc))
        if stale:
            params.append(("stale", stale))
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.get(
            CB.binary(), path="/v1/snapshot", params=params, headers=headers
        )

    def put(self, data_binary, dc=None, token=None):
        params = []
        headers = {}
        dc = dc or self.agent.dc
        token = token or self.agent.token

        if dc:
            params.append(("dc", dc))
        if token:
            headers["X-Consul-Token"] = token
        return self.agent.http.put(
            CB.binary(),
            path="/v1/snapshot",
            params=params,
            headers=headers,
            data=data_binary,
        )

    def save(self, file_path):
        """
            Backup snapshot in a file
            """
        backup_file = open(file_path, "w+b")
        backup_file.write(self.get())
        backup_file.close()
        return True

    def restore(self, file_path):
        """
            Restore from snapshot file
            """
        backup_file = open(file_path, "rb")
        data_binary = backup_file.read()
        self.put(data_binary)
        backup_file.close()
        return True
