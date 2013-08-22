# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re

import util


CONTEXT_THRESHOLD = 12
PROPERTY_NAME_RE = re.compile(r"^\s*'(\w+)'\s*:")


def nmin(*args):
  """Calculates the minimum of |args|, ignoring None entries."""
  values = [v for v in args if v is not None]
  return None if len(values) == 0 else min(values)


def nmax(*args):
  """Calculates the maximum of |args|, ignoring None entries."""
  values = [v for v in args if v is not None]
  return None if len(values) == 0 else max(values)


def nadd(a, b):
  """Calculates a + b, returning None if either a or b is None"""
  return None if (a is None or b is None) else a + b


def nsub(a, b):
  """Calculates a - b, returning None if either a or b is None"""
  return None if (a is None or b is None) else a - b


def get_indentation_level(line):
  """Returns the indentation level (number of leading spaces) for |line|."""
  nspaces = len(line) - len(line.lstrip(' '))
  return None if nspaces == 0 else nspaces


class PolicyChangeParser(object):
  """Parses a policy_templates.json diff to identify logical changes.

  This takes a list of triples of the form (old_line, new_line, text) as
  returned by patching.ParsePatchToLines and produces a list of dictionaries
  describing the logical changes that have been made. The dictionaries contain
  these keys:
    * start: A pair (old_line, new_line) indicating where the change starts.
    * end: A pair (old_line, new_line) indicating where the change ends.
    * comment_pos: A pair (old_line, new_line), indicating a suitable place to
                   put an inline comment. This is typically the line where the
                   policy name is found in the diff.
    * additions: Whether there have been line additions.
    * removals: Whether there have been line removals.
  """

  def __init__(self, lines):
    self.lines = lines
    self.chunks_list = []
    self.reset()

  def run(self):
    """Main parsing function.

    The code goes over the diff line by line, keeping track of the current line.
    It keeps track of the current line numbers, and where the last changes
    happened in the old and new version of the file.

    Certain events trigger start of a new logical change. These are
    discontinuities in the cursor position and decreases of the indentation
    level. Once a block closes, the information for that block is recorded in
    the result list.
    """
    self.chunks_list = []
    self.last_change = [None, None]
    cursor = [None, None]
    self.reset()
    for (a_line, b_line, line) in self.lines:
      # Skip comment lines.
      if line.startswith('#'):
        continue

      # See whether the current line has a JSON property.
      keyword = None
      match = PROPERTY_NAME_RE.match(line)
      if match:
        keyword = match.group(1).lower()


      # Check whether the current block closes.
      line_indent = get_indentation_level(line)
      if (self.block_indent is not None and
            line_indent is not None and
            line_indent < self.block_indent):
        self.block_closed = True

      # Update various cursors.
      cursor = [nmax(a_line, cursor[0]), nmax(b_line, cursor[1])]
      offset = nmin(nsub(cursor[0], self.last_change[0]),
                    nsub(cursor[1], self.last_change[1]))

      # Update change tracking state.
      if a_line is not None and b_line is None:
        self.removals = True
        self.last_change[0] = a_line
        self.text_changed |= any([c.isalnum() for c in line])
      elif a_line is None and b_line is not None:
        self.additions = True
        self.last_change[1] = b_line
        self.text_changed |= any([c.isalnum() for c in line])

      # If the indentation block closes or the last chunk is too far away,
      # assume a new one starts.
      if (self.block_closed or
          (offset is not None and (offset > CONTEXT_THRESHOLD))):
        self.flush_chunk()

      # Try to figure out block indent from properties exclusively used for
      # policy definitions.
      if (self.block_indent is None and
          keyword in ('id', 'schema', 'future', 'features', 'supported_on',
                      'example_value', 'deprecated')):
        self.block_indent = line_indent

      # Put the comment on the policy name property if we see it fly by.
      if keyword == 'name':
        # Filter out name labels on enum items and schemas.
        if self.block_indent is not None and self.block_indent != line_indent:
          pass
        elif a_line is not None and b_line is None:
          self.comment_pos[0] = a_line
        elif a_line is None and b_line is not None:
          self.comment_pos[1] = b_line

      self.chunk_start = [nmin(self.last_change[0], self.chunk_start[0]),
                          nmin(self.last_change[1], self.chunk_start[1])]

    # Flush the last chunk.
    if self.chunk_start != [None, None]:
      self.flush_chunk()

  def flush_chunk(self):
    if self.text_changed:
      comment_pos = [nmax(self.chunk_start[0], self.comment_pos[0]),
                     nmax(self.chunk_start[1], self.comment_pos[1])]
      self.chunks_list.append(
          util.ObjectDict(
              { 'start': self.chunk_start,
                'end': [nadd(self.last_change[0], 1),
                        nadd(self.last_change[1], 1)],
                'comment_pos': comment_pos,
                'additions': self.additions,
                'removals': self.removals }))
    self.reset()

  def reset(self):
    # This is called from __init__.
    # pylint: disable=W0201
    self.chunk_start = [None, None]
    self.last_change = [None, None]
    self.comment_pos = [None, None]
    self.block_indent = None
    self.block_closed = False
    self.additions = False
    self.removals = False
    self.text_changed = False


def parse(lines):
  """Helper function to parse lines to a list of chunks directly."""
  parser = PolicyChangeParser(lines)
  parser.run()
  return parser.chunks_list
