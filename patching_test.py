#!/usr/bin/env python
# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

import patching


class TestParsePatchToLines(unittest.TestCase):
  def test_empty(self):
    self.assertEquals([], patching.ParsePatchToLines([]))

  def test_prelude(self):
    self.assertEquals([], patching.ParsePatchToLines("""
Here goes some prelude.
And it continues on for some while.

--- file
+++ file
""".splitlines()))

  def test_bad_hunk_header(self):
    with self.assertRaises(patching.PatchParseError):
      patching.ParsePatchToLines("""
--- file
+++ file
@@ bad
""".splitlines())

  def test_multiple_files(self):
    with self.assertRaises(patching.PatchParseError):
      patching.ParsePatchToLines("""
diff -urN test1/bar test2/bar
--- test1/bar	2013-08-08 14:15:46.604119530 +0200
+++ test2/bar	2013-08-08 14:15:49.814145535 +0200
@@ -1 +1 @@
-foo
+bar
diff -urN test1/foo test2/foo
--- test1/foo	2013-08-08 14:15:36.044033982 +0200
+++ test2/foo	2013-08-08 14:15:42.204083886 +0200
@@ -1 +1 @@
-foo
+bar
""".splitlines())

  def test_simple(self):
    self.assertEquals([
        (1, 1, 'common line'),
        (2, None, 'old line'),
        (None, 2, 'new line'),
        (3, 3, 'common line'),
        ], patching.ParsePatchToLines("""
--- old	2013-08-08 14:05:18.539090366 +0200
+++ new	2013-08-08 14:05:18.539090366 +0200
@@ -1,3 +1,3 @@
 common line
-old line
+new line
 common line
""".splitlines()))

  def test_multiple_hunks(self):
    self.assertEquals([
        (None, 1, 'prepended line'),
        (1, 2, ''),
        (2, 3, ''),
        (3, 4, ''),
        (8, 9, ''),
        (9, 10, ''),
        (10, 11, ''),
        (None, 12, 'appended line'),
        ], patching.ParsePatchToLines("""
--- old	2013-08-08 14:10:10.391408985 +0200
+++ new	2013-08-08 14:10:15.511449623 +0200
@@ -1,3 +1,4 @@
+prepended line
 
 
 
@@ -8,3 +9,4 @@
 
 
 
+appended line
""".splitlines()))

if __name__ == '__main__':
  unittest.main()
