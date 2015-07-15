# -*- coding: utf-8 -*-
import unittest

from fixtures.fakes import InvalidEndpoint, FakeView, FakeGetView, FakeEndpoint

from aiorest_ws.exceptions import EndpointValueError, NotSpecifiedURL
from aiorest_ws.routers import RestWSRouter


class RestWSRouterTestCase(unittest.TestCase):

    def setUp(self):
        super(RestWSRouterTestCase, self).setUp()
        self.router = RestWSRouter()

    def test_correct_path(self):
        broken_path = 'api'
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, 'api/')

        broken_path = ' api  '
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, 'api/')

        correct_path = 'api/'
        fixed_path = self.router._correct_path(broken_path)
        self.assertEqual(fixed_path, correct_path)

    def test_get_argument(self):
        request = {'args': {'param': 'test'}}
        self.assertEqual(self.router.get_argument(request, 'param'), 'test')

        request = {'args': {}}
        self.assertIsNone(self.router.get_argument(request, 'param'), None)

        request = {}
        self.assertIsNone(self.router.get_argument(request, 'param'))

    def test_register(self):
        self.router.register('/api', FakeView, 'GET')
        self.assertEqual(FakeView, self.router._urls[0].handler)

    def test_extract_url(self):
        request = {}
        self.assertRaises(NotSpecifiedURL, self.router.extract_url, request)

        request = {'url': '/api'}
        self.assertEqual(self.router.extract_url(request), '/api/')

        request = {'url': '/api/'}
        self.assertEqual(self.router.extract_url(request), '/api/')

    def test_search_handler(self):
        self.router.register('/api/', FakeView, 'GET')
        self.router.register('/api/{version}/', FakeView, 'GET')

        request = {}
        url = '/api/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {})

        request = {}
        url = '/api/v1/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ('v1',))
        self.assertEqual(kwargs, {})

        request = {'args': {'format': 'json'}}
        url = '/api/v2/'
        handler, args, kwargs = self.router.search_handler(request, url)
        self.assertIsInstance(handler, FakeView)
        self.assertEqual(args, ('v2',))
        self.assertEqual(kwargs, {'params': {'format': 'json'}})

    def test_dispatch(self):
        self.router.register('/api/get/', FakeGetView, 'GET')

        request = {'method': 'GET', 'url': '/api/get/'}
        self.assertEqual(self.router.dispatch(request), b'"fake"')

        request = {'method': 'GET', 'url': '/api/get/',
                   'args': {'format': 'xml'}}
        self.assertEqual(self.router.dispatch(request), b'"fake"')

        request = {'method': 'GET', 'url': '/api/invalid/'}
        self.assertEqual(
            self.router.dispatch(request),
            b'{"details": "For URL, typed in request, handler not specified."}'
        )

        request = {'method': 'GET'}
        self.assertEqual(
            self.router.dispatch(request),
            b'{"details": "In query not specified `url` argument."}'
        )

    def test_register_url(self):
        endpoint = InvalidEndpoint
        self.assertRaises(TypeError, self.router._register_url, endpoint)

        endpoint = FakeEndpoint('/api/', None, 'GET', 'good')
        self.router._register_url(endpoint)
        self.assertRaises(EndpointValueError, self.router._register_url,
                          endpoint)

        endpoint.name = None
        self.router._register_url(endpoint)