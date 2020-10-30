import os

from .acl import ACL
from .agent import Agent
from .catalog import Catalog
from .config import Config
from .connect import Connect
from .coordinate import Coordinate
from .discovery_chain import DiscoveryChain
from .event import Event
from .exceptions import ConsulException
from .health import Health
from .kv import KV
from .operator import Operator
from .query import Query
from .session import Session
from .snapshot import Snapshot
from .status import Status
from .transaction import Txn


class BaseConsul(object):
    def __init__(
            self,
            host='127.0.0.1',
            port=8500,
            token=None,
            scheme='http',
            consistency='default',
            dc=None,
            verify=True,
            cert=None,
            **kwargs):
        """
        *token* is an optional `ACL token`_. If supplied it will be used by
        default for all requests made with this client session. It's still
        possible to override this token by passing a token explicitly for a
        request.

        *consistency* sets the consistency mode to use by default for all reads
        that support the consistency option. It's still possible to override
        this by passing explicitly for a given request. *consistency* can be
        either 'default', 'consistent' or 'stale'.

        *dc* is the datacenter that this agent will communicate with.
        By default the datacenter of the host is used.

        *verify* is whether to verify the SSL certificate for HTTPS requests

        *cert* client side certificates for HTTPS requests
        """

        # TODO: Status

        if os.getenv('CONSUL_HTTP_ADDR'):
            try:
                host, port = os.getenv('CONSUL_HTTP_ADDR').split(':')
                scheme = 'http'
            except ValueError:
                try:
                    scheme, host, port = \
                        os.getenv('CONSUL_HTTP_ADDR').split(':')
                    host = host.lstrip('//')
                except ValueError:
                    raise ConsulException('CONSUL_HTTP_ADDR (%s) invalid, '
                                          'does not match <host>:<port> or '
                                          '<protocol>:<host>:<port>'
                                          % os.getenv('CONSUL_HTTP_ADDR'))
        use_ssl = os.getenv('CONSUL_HTTP_SSL')
        if use_ssl == 'true':
            scheme = 'https'
        if os.getenv('CONSUL_HTTP_SSL_VERIFY') is not None:
            verify = os.getenv('CONSUL_HTTP_SSL_VERIFY') == 'true'

        self.acl = ACL(self)
        self.agent = Agent(self)
        self.catalog = Catalog(self)
        self.config = Config(self)
        self.connect = Connect(self)
        assert consistency in ('default', 'consistent', 'stale'), \
            'consistency must be either default, consistent or state'
        self.consistency = consistency
        self.coordinate = Coordinate(self)
        self.dc = dc
        self.discovery_chain = DiscoveryChain(self)
        self.event = Event(self)
        self.health = Health(self)
        self.http = self.http_connect(host,
                                      port,
                                      scheme,
                                      verify,
                                      cert,
                                      **kwargs)
        self.kv = KV(self)
        self.operator = Operator(self)
        self.query = Query(self)
        self.scheme = scheme
        self.session = Session(self)
        self.snapshot = Snapshot(self)
        self.status = Status(self)
        self.token = os.getenv('CONSUL_HTTP_TOKEN', token)
        self.txn = Txn(self)
