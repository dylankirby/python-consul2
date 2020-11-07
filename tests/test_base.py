import collections
import json
import os
import sys

import pytest

from consul.core import exceptions
from consul.core.consul import BaseConsul
from consul.core.check import Check
from consul.core.http import BaseHTTPClient
from consul.core.callback import CB
from consul.core.response import Response

Request = collections.namedtuple(
    'Request', ['method', 'path', 'params', 'data', 'headers'])


class HTTPClient(object):
    def __init__(self, host=None, port=None, scheme=None,
                 verify=True, cert=None, timeout=None, headers=None):
        pass

    def get(self, callback, path, params=None, headers=None):
        return Request('get', path, params, None, headers)

    def put(self, callback, path, params=None, data='', headers=None):
        return Request('put', path, params, data, headers)

    def delete(self, callback, path, params=None, headers=None):
        return Request('delete', path, params, None, headers)


class Consul(BaseConsul):
    def http_connect(self, host, port, scheme, verify=True, cert=None,
                     timeout=None):
        return HTTPClient(host, port, scheme, verify=verify, cert=None,
                          timeout=None)


def _should_support(c):
    return (
        # kv
        lambda **kw: c.kv.get('foo', **kw),
        # catalog
        c.catalog.nodes,
        c.catalog.services,
        lambda **kw: c.catalog.node('foo', **kw),
        lambda **kw: c.catalog.service('foo', **kw),
        # session
        c.session.list,
        lambda **kw: c.session.info('foo', **kw),
        lambda **kw: c.session.node('foo', **kw),
    )


def _should_support_node_meta(c):
    return (
        # catalog
        c.catalog.nodes,
        c.catalog.services,
        lambda **kw: c.catalog.service('foo', **kw),

        # health
        lambda **kw: c.health.service('foo', **kw),
        lambda **kw: c.health.checks('foo', **kw),
        lambda **kw: c.health.state('unknown', **kw),
    )


def _should_support_meta(c):
    return (
        # agent
        lambda **kw: c.agent.service.register('foo', **kw),
        lambda **kw: c.agent.service.register('foo', 'bar', **kw),
    )


class TestIndex(object):
    """
    Tests read requests that should support blocking on an index
    """

    def test_index(self):
        c = Consul()
        for r in _should_support(c):
            assert r().params == []
            assert r(index='5').params == [('index', '5')]


class TestConsistency(object):
    """
    Tests read requests that should support consistency modes
    """

    def test_explict(self):
        c = Consul()
        for r in _should_support(c):
            assert r().params == []
            assert r(consistency='default').params == []
            assert r(consistency='consistent').params == [('consistent', '1')]
            assert r(consistency='stale').params == [('stale', '1')]

    def test_implicit(self):
        c = Consul(consistency='consistent')
        for r in _should_support(c):
            assert r().params == [('consistent', '1')]
            assert r(consistency='default').params == []
            assert r(consistency='consistent').params == [('consistent', '1')]
            assert r(consistency='stale').params == [('stale', '1')]


class TestNodemeta(object):
    """
    Tests read requests that should support node_meta
    """

    def test_node_meta(self):
        c = Consul()
        for r in _should_support_node_meta(c):
            assert r().params == []
            r1 = sorted(r(node_meta={'env': 'prod', 'net': 1}).params)
            r2 = sorted([('node-meta', 'net:1'), ('node-meta', 'env:prod')])
            assert r1 == r2
            data = c.catalog.register('foo', 'bar',
                                      node_meta={'env': 'prod', 'net': 1}).data
            r1 = json.loads(data)["NodeMeta"]
            r2 = {'net': 1, 'env': 'prod'}

            assert r1 == r2


class TestMeta(object):
    """
    Tests read requests that should support meta
    """

    def test_meta(self):
        c = Consul()
        for r in _should_support_meta(c):
            d = json.loads(r(meta={'env': 'prod', 'net': 1}).data)
            assert sorted(d['meta']) == sorted({'env': 'prod', 'net': 1})


class TestCB(object):

    def test_status_200_passes(self):
        response = Response(200, None, None, None)
        CB._status(response)

    @pytest.mark.parametrize(
        'response, expected_exception',
        [
            (Response(400, None, None, None), exceptions.BadRequest),
            (Response(401, None, None, None), exceptions.ACLDisabled),
            (Response(403, None, None, None), exceptions.ACLPermissionDenied),
        ])
    def test_status_4xx_raises_error(self, response, expected_exception):
        with pytest.raises(expected_exception):
            CB._status(response)

    def test_status_404_allow_404(self):
        response = Response(404, None, None, None)
        CB._status(response, allow_404=True)

    def test_status_404_dont_allow_404(self):
        response = Response(404, None, None, None)
        with pytest.raises(exceptions.NotFound):
            CB._status(response, allow_404=False)

    def test_status_405_raises_generic_ClientError(self):
        response = Response(405, None, None, None)
        with pytest.raises(exceptions.ClientError):
            CB._status(response)

    @pytest.mark.parametrize(
        'response',
        [
            Response(500, None, None, None),
            Response(599, None, None, None),
        ])
    def test_status_5xx_raises_error(self, response):
        with pytest.raises(exceptions.ConsulException):
            CB._status(response)


class TestChecks(object):
    """
    Check constructor helpers return valid check configurations.
    """

    @pytest.mark.parametrize(
        'url, interval, timeout, deregister, header, want', [
            ('http://example.com', '10s', None, None, None, {
                'http': 'http://example.com',
                'interval': '10s',
            }),
            ('http://example.com', '10s', '1s', None, None, {
                'http': 'http://example.com',
                'interval': '10s',
                'timeout': '1s',
            }),
            ('http://example.com', '10s', None, '1m', None, {
                'http': 'http://example.com',
                'interval': '10s',
                'DeregisterCriticalServiceAfter': '1m',
            }),
            ('http://example.com', '10s', '1s', '1m', None, {
                'http': 'http://example.com',
                'interval': '10s',
                'timeout': '1s',
                'DeregisterCriticalServiceAfter': '1m',
            }),
            ('http://example.com', '10s', '1s', '1m',
             {'X-Test-Header': ['TestHeaderValue']},
             {
                 'http': 'http://example.com',
                 'interval': '10s',
                 'timeout': '1s',
                 'DeregisterCriticalServiceAfter': '1m',
                 'header': {'X-Test-Header': ['TestHeaderValue']}
             }
             ),
        ])
    def test_http_check(self, url, interval, timeout, deregister, header,
                        want):
        ch = Check.http(url, interval, timeout=timeout,
                                    deregister=deregister, header=header)
        assert ch == want

    @pytest.mark.parametrize(
        'host, port, interval, timeout, deregister, want',
        [
            ('localhost', 1234, '10s', None, None, {
                'tcp': 'localhost:1234',
                'interval': '10s',
            }),
            ('localhost', 1234, '10s', '1s', None, {
                'tcp': 'localhost:1234',
                'interval': '10s',
                'timeout': '1s',
            }),
            ('localhost', 1234, '10s', None, '1m', {
                'tcp': 'localhost:1234',
                'interval': '10s',
                'DeregisterCriticalServiceAfter': '1m',
            }),
            ('localhost', 1234, '10s', '1s', '1m', {
                'tcp': 'localhost:1234',
                'interval': '10s',
                'timeout': '1s',
                'DeregisterCriticalServiceAfter': '1m',
            }),
        ])
    def test_tcp_check(self, host, port, interval, timeout, deregister, want):
        ch = Check.tcp(host, port, interval, timeout=timeout,
                                   deregister=deregister)
        assert ch == want

    @pytest.mark.parametrize(
        'container_id, shell, script, interval, deregister, want',
        [
            ('wandering_bose', '/bin/sh', '/bin/true', '10s', None, {
                'docker_container_id': 'wandering_bose',
                'shell': '/bin/sh',
                'script': '/bin/true',
                'interval': '10s',
            }),
            ('wandering_bose', '/bin/sh', '/bin/true', '10s', '1m', {
                'docker_container_id': 'wandering_bose',
                'shell': '/bin/sh',
                'script': '/bin/true',
                'interval': '10s',
                'DeregisterCriticalServiceAfter': '1m',
            }),
        ])
    def test_docker_check(self, container_id, shell, script, interval,
                          deregister, want):
        ch = Check.docker(container_id, shell, script, interval,
                                      deregister=deregister)
        assert ch == want

    def test_ttl_check(self):
        ch = Check.ttl('1m')
        assert ch == {'ttl': '1m'}

    def test_http_imp(self):
        error = TypeError
        if sys.version_info[0] >= 3:
            error = NotImplementedError
        pytest.raises(error,
                      BaseHTTPClient.get, HTTPClient(), 'b', 'c')
        pytest.raises(error,
                      BaseHTTPClient.post, HTTPClient(), 'b', 'c')
        pytest.raises(error,
                      BaseHTTPClient.put, HTTPClient(), 'b', 'c')
        pytest.raises(error,
                      BaseHTTPClient.delete, HTTPClient(), 'b', 'c')
        pytest.raises(TypeError, BaseHTTPClient)

    def test_env(self):
        os.environ['CONSUL_HTTP_ADDR'] = 'foo'
        pytest.raises(exceptions.ConsulException, BaseConsul)

        os.environ['CONSUL_HTTP_ADDR'] = 'localhost:8080'
        os.environ['CONSUL_HTTP_SSL'] = 'true'
        os.environ['CONSUL_HTTP_SSL_VERIFY'] = 'true'
        pytest.raises(AttributeError, BaseConsul)
        os.environ['CONSUL_HTTP_ADDR'] = ''
        os.environ['CONSUL_HTTP_SSL'] = ''
        os.environ['CONSUL_HTTP_SSL_VERIFY'] = ''
