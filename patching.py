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

"""Utility for parsing patches, shamelessly stolen from rietveld."""

import logging
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


_NO_NEWLINE_MESSAGE = "\\ No newline at end of file"


def ParsePatchToLines(lines):
  """Parses a patch from a list of lines.

  Args:
    lines: The lines to parse.

  Returns:
    None on error, otherwise a list of 3-tuples:
    (old_line_no, new_line_no, line)

    A line number can be 0 if it doesn't exist in the old/new file.
  """
  result = []
  in_prelude = True
  for line in lines:
    if in_prelude:
      # Skip leading lines until after we've seen one starting with '+++'
      if line.startswith("+++"):
        in_prelude = False
    elif line.startswith("@"):
      match = _CHUNK_RE.match(line)
      if not match:
        logging.warn("ParsePatchToLines match failed on %s", line)
        return None
      old_ln = int(match.groups()[0])
      new_ln = int(match.groups()[2])
    else:
      if line[0] == "-":
        result.append((old_ln, 0, line[1:]))
        old_ln += 1
      elif line[0] == "+":
        result.append((0, new_ln, line[1:]))
        new_ln += 1
      elif line[0] == " ":
        result.append((old_ln, new_ln, line[1:]))
        old_ln += 1
        new_ln += 1
  return result
