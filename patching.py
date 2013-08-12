# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# Copyright 2008 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility for parsing patches, originally inspired by rietveld source."""

import re


_CHUNK_RE = re.compile(r"""
  @@
  \s+
  -
  (?: (\d+) (?: , (\d+) )?)
  \s+
  \+
  (?: (\d+) (?: , (\d+) )?)
  \s+
  @@
""", re.VERBOSE)


class PatchParseError(Exception):
  """Raised on parse errors."""
  pass


def ParsePatchToLines(lines):
  """Parses a patch from an iterable type.

  Args:
    lines: The lines to parse.

  Returns:
    None on error, otherwise a list of 3-tuples:
    (old_line_no, new_line_no, line)

    A line number can be None if it doesn't exist in the old/new file.
  """
  # Helper function that matches a hunk header and returns line numbers.
  def match_hunk_start(line):
    match = _CHUNK_RE.match(line)
    if not match:
      raise PatchParseError(line)
    return (int(match.groups()[0]), int(match.groups()[2]))

  iterator = lines.__iter__()
  try:
    # Skip leading lines until after we've seen one starting with '+++'.
    while not iterator.next().startswith('+++'):
      pass

    # Parse first hunk header.
    old_ln, new_ln = match_hunk_start(iterator.next())
  except StopIteration:
    return []

  # Process the actual patch lines.
  result = []
  for line in iterator:
    if line[0] == '@':
      old_ln, new_ln = match_hunk_start(line)
    elif line[0] == '-':
      result.append((old_ln, None, line[1:]))
      old_ln += 1
    elif line[0] == '+':
      result.append((None, new_ln, line[1:]))
      new_ln += 1
    elif line[0] == ' ':
      result.append((old_ln, new_ln, line[1:]))
      old_ln += 1
      new_ln += 1
    else:
      raise PatchParseError(line)

  return result
