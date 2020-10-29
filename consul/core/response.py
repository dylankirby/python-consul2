from collections import namedtuple

Response = namedtuple(
    'Response', ['code', 'headers', 'body', 'content'])