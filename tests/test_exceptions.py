# -*- coding: utf-8 -*-
import unittest

from aiorest_ws.exceptions import BaseAPIException


class BaseAPIExceptionTestCase(unittest.TestCase):

    def test_init(self):
        exception = BaseAPIException()
        self.assertEqual(exception.detail, exception.default_detail)

        exception = BaseAPIException("Some exception.")
        self.assertNotEqual(exception.detail, exception.default_detail)

    def test_str_output(self):
        exception = BaseAPIException()
        self.assertEqual(str(exception), exception.detail)
