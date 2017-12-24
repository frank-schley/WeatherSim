# -*- coding: utf-8 -*-

from weather import helpers

import unittest

class FirstTest(unittest.TestCase):

    def test_first_failure(self):
        self.assertEqual(helpers.get_thought(),
                        'A beginning is a very delicate time')
