# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re

import model.app_config
import util


POLICY_TEMPLATES_FILE = 'chrome/app/policy/policy_templates.json'
ID_LINE_COMMENT = 'For your editing convenience: highest ID currently used:'
CONTEXT_THRESHOLD = 12
PROPERTY_NAME_RE = re.compile('\'(\\w+)\'\\s*:')
MAX_LINE = 1000000

REVIEW_MESSAGE = '''
Thanks for helping improve Chromium's enterprise policy support. Policy
review bot has automatically added checklists for the author and
reviewers to go through in order to catch common pitfalls.

Send complaints and feedback about this to mnissler@chromium.org.
'''

ADDITION_COMMENT = '''
You have a policy addition here! Beware!
'''

MODIFICATION_COMMENT = '''
Ah, so you mess with stuff that's already there.
'''


def nmin(*args):
  """Calculates the minimum of |args|, ignoring None entries."""
  try:
    return min(v for v in args if v is not None)
  except ValueError:
    return None


def nmax(*args):
  """Calculates the maximum of |args|, ignoring None entries."""
  try:
    return max(v for v in args if v is not None)
  except ValueError:
    return None


def nsub(a, b):
  """Calculates a - b, returning None if either a or b is None"""
  return None if (a is None or b is None) else a - b


def indent(line):
  """Returns the indent level (number of leading spaces) for |line|."""
  nspaces = len(line) - len(line.lstrip(' '))
  return None if nspaces == 0 else nspaces


class PolicyChangeParser(object):
  def __init__(self, lines):
    self.lines = lines
    self.chunks_list = []
    self.reset()

  def run(self):
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
      match = PROPERTY_NAME_RE.search(line)
      if match:
        keyword = match.group(1).lower()


      # Check whether the current block closes.
      line_indent = indent(line)
      if (self.block_indent is not None and
            line_indent is not None and
            line_indent < self.block_indent):
        self.block_closed = True

      if (keyword == 'name' and self.block_closed):
        # If we see the 'name' property, that likely indicates the start of a
        # new policy. Start a new chunk.
        self.flush_chunk()

      # Update various cursors.
      cursor = [nmax(a_line, cursor[0]), nmax(b_line, cursor[1])]
      offset = nmin(nsub(cursor[0], self.last_change[0]),
                    nsub(cursor[1], self.last_change[1]))

      if a_line > 0 and b_line == 0:
        self.removals = True
        self.last_change[0] = a_line
      elif a_line == 0 and b_line > 0:
        self.additions = True
        self.last_change[1] = b_line

      if (offset is not None and
          (offset > CONTEXT_THRESHOLD or
           (offset > 1 and self.block_closed))):
        # If the last chunk is too far away, assume a new one starts.
        self.flush_chunk()

      # Try to figure out block indent from properties exclusively used for
      # policy definitions.
      if keyword in ('id', 'schema', 'future', 'items', 'features',
                     'supported_on', 'example_value', 'deprecated'):
        self.block_indent = line_indent

      # Prefer the comment on the policy name property if we see it fly by.
      if keyword == 'name':
        # Attempt to filter out name labels on enum items.
        if self.block_indent is not None and self.block_indent != line_indent:
          pass
        elif a_line > 0 and b_line == 0:
          self.comment_pos[0] = a_line
        elif a_line == 0 and b_line > 0:
          self.comment_pos[1] = b_line

      self.chunk_start = [nmin(self.last_change[0], self.chunk_start[0]),
                          nmin(self.last_change[1], self.chunk_start[1])]

    # Flush the last chunk.
    if self.chunk_start != [None, None]:
      self.flush_chunk()

  @property
  def chunks(self):
    return self.chunks_list

  def flush_chunk(self):
    self.comment_pos = [nmax(self.chunk_start[0], self.comment_pos[0]),
                        nmax(self.chunk_start[1], self.comment_pos[1])]
    self.chunks_list.append(
        util.ObjectDict(
            { 'start': self.chunk_start,
              'end': self.last_change,
              'comment_pos': self.comment_pos,
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


def process(addr, message, review, rietveld):
  """Handles reviews for chrome/app/policy/policy_templates.json.

  This looks at the patch to identify additions/modifications to policy
  definitions and posts comments with a checklist intended for the author and
  reviewer to go through in order to catch common mistakes.
  """

  if POLICY_TEMPLATES_FILE not in review.latest_patchset.files:
    return

  # Only process the change if the mail is directly to us or we haven't
  # processed this review yet.
  client_id = model.app_config.get().client_id
  if (not addr in util.get_emails(getattr(message, 'to', '')) and
      client_id in [m.sender for m in review.issue_data.messages]):
    return

  # Don't process reverts.
  if 'revert' in review.issue_data.description.lower():
    return

  # Parse the patch, look at the chunks and generate inline comments.
  parser = PolicyChangeParser(
      review.latest_patchset.files[POLICY_TEMPLATES_FILE].patch.lines)
  parser.run()
  for chunk in parser.chunks:
    if chunk.additions and not chunk.removals:
      message = ADDITION_COMMENT
    else:
      message = MODIFICATION_COMMENT

    if chunk.comment_pos[1] is not None:
      line, side = chunk.comment_pos[1], 'b'
    elif chunk.comment_pos[0] is not None:
      line, side = chunk.comment_pos[0], 'a'
    else:
      # No suitable position?
      continue

    rietveld.add_inline_comment(
        review.issue_id, review.latest_patchset.patchset,
        review.latest_patchset.files[POLICY_TEMPLATES_FILE].id,
        line, side, message)

  # Finally, post all inline comments.
  if len(parser.chunks) > 0:
    rietveld.post_comment(review.issue_id, REVIEW_MESSAGE, True)
