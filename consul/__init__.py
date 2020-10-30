__version__ = '0.1.4'

from .core.exceptions import ConsulException  # noqa
from .core.exceptions import ACLDisabled  # noqa
from .core.exceptions import ACLPermissionDenied  # noqa
from .core.exceptions import NotFound  # noqa
from .core.exceptions import Timeout  # noqa
from .core.exceptions import BadRequest  # noqa
from .core.exceptions import ClientError  # noqa
from consul.std import Consul  # noqa
# from consul.tornado import Consul  # noqa
# from consul.twisted import Consul  # noqa
# from consul.aio import Consul  # noqa
