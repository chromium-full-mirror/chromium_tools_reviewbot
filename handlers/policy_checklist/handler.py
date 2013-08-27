# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Handler for chrome/app/policy/policy_templates.json

This handler examines changes to the policy_templates.json file and posts
comments with checklists for the patch author and reviewer to go through to
avoid common pitfalls.
"""

import os

import jinja2

import model.app_config
import util
import handlers.policy_checklist.parser


POLICY_TEMPLATES_FILE = 'chrome/app/policy/policy_templates.json'
MAX_INLINE_COMMENTS = 10


REVIEW_MESSAGE_TEMPLATE = 'review_message.txt'
ADDITION_COMMENT_TEMPLATE = 'addition_comment.txt'
MODIFICATION_COMMENT_TEMPLATE = 'modification_comment.txt'


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def prepare_address_list(addr, email_list):
  """Prepares |email_list| for use as rietveld query parameter.

  Canonicalizes the entries in |email_list|, removes any occurrences of |addr|,
  joins the entries with commas and returns the result.
  """
  return ','.join([util.canonicalize_email(entry)
                   for entry in email_list if entry != addr])


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
  chunks = handlers.policy_checklist.parser.parse(
      review.latest_patchset.files[POLICY_TEMPLATES_FILE].patch.lines)
  for chunk in chunks[0:MAX_INLINE_COMMENTS]:
    if chunk.additions and not chunk.removals:
      template = JINJA_ENVIRONMENT.get_template(ADDITION_COMMENT_TEMPLATE)
    else:
      template = JINJA_ENVIRONMENT.get_template(MODIFICATION_COMMENT_TEMPLATE)

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
        line, side, template.render(review=review, chunk=chunk))

  # Finally, post all inline comments.
  if len(chunks) > 0:
    template = JINJA_ENVIRONMENT.get_template(REVIEW_MESSAGE_TEMPLATE)
    rietveld.publish_inline_comments(
        review.issue_id, template.render(review=review),
        prepare_address_list(addr, review.issue_data.reviewers),
        prepare_address_list(addr, review.issue_data.cc))
