# coding=utf-8
"""Useful stuff for tests."""
# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast
import unittest

from six.moves import zip


class TestCase(unittest.TestCase):

  def checkAstsEqual(self, a, b):
    """Compares two ASTs and fails if there are differences.

    Ignores `ctx` fields and formatting info.
    """
    try:
      for node_a, node_b in zip(ast.walk(a), ast.walk(b)):
        self.assertEqual(type(node_a), type(node_b))
        for field in type(node_a)()._fields:
          a_val = getattr(node_a, field, None)
          b_val = getattr(node_b, field, None)

          if isinstance(a_val, list):
            for item_a, item_b in zip(a_val, b_val):
              self.checkAstsEqual(item_a, item_b)
          elif isinstance(a_val, ast.AST) or isinstance(b_val, ast.AST):
            if (not isinstance(a_val, (ast.Load, ast.Store, ast.Param)) and
                not isinstance(b_val, (ast.Load, ast.Store, ast.Param))):
              self.assertIsNotNone(a_val)
              self.assertIsNotNone(b_val)
              self.checkAstsEqual(a_val, b_val)
          else:
            self.assertEqual(a_val, b_val)
    except AssertionError as ae:
      self.fail('ASTs differ:\n%s\n  !=\n%s\n\n%s' % (
          ast.dump(a), ast.dump(b), ae))


if not hasattr(TestCase, 'assertItemsEqual'):
  setattr(TestCase, 'assertItemsEqual', TestCase.assertCountEqual)


def requires_features(*features):
  return unittest.skipIf(
      any(not supports_feature(feature) for feature in features),
      'Tests features which are not supported by this version of python. '
      'Missing: %r' % [f for f in features if not supports_feature(f)])


def supports_feature(feature):
  if feature == 'type_annotations':
    try:
      ast.parse('def foo(bar: str=123) -> None: pass')
    except SyntaxError:
      return False
    return True
  return False
