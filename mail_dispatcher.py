# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Main app that handles incoming mail and dispatches it to handlers."""

import logging
import re

import webapp2
import webob.exc

from google.appengine.api import app_identity
from google.appengine.api import mail

import third_party  # pylint: disable=W0611

import handlers.policy_checklist
from review import Review
from rietveld import Rietveld
import util


# Lists the handlers served by the review bot app. The local part of email
# addresses the app receives email on is used as a key into the handler map.
# Each handler is just a function that gets called with the email address, the
# email message, a Review object and a Rietveld interface.
#
# New handlers can be added by adding the code in handlers/<handler_name>.py,
# importing the module and adding an entry to the HANDLERS map.
HANDLERS = {
    'policy_checklist': handlers.policy_checklist.process
}


# Regular expression that matches email addresses belonging to the review bot
# app and extracts the handler name.
REVIEW_BOT_RECIPIENT_RE = re.compile('^([^@]+)@%s.appspotmail.com$' %
                                     app_identity.get_application_id())


# This is the regular expression that rietveld uses to extract the issue number
# from the mail subject at the time of writing this. This code needs to be kept
# up-to-date with the mechanism rietveld uses so the tools don't confuse issues.
RIETVELD_ISSUE_NUMBER_RE = re.compile(r'\(issue *(?P<id>\d+)\)$')


class MailDispatcher(webapp2.RequestHandler):
  """Dispatches mail to handlers as indicated by email addresses."""

  def post(self):
    """Handles POST requests.

    Parses the incoming mail message. Dispatches to interested handlers based on
    the list of mail recipients.
    """

    # Singleton Rietveld interface for this request.
    rietveld = Rietveld()

    # Parse the message and instantiate the review interface.
    message = mail.InboundEmailMessage(self.request.body)
    match = RIETVELD_ISSUE_NUMBER_RE.search(message.subject)
    if match is None:
      raise webob.exc.HTTPBadRequest('Failed to parse issue id: %s' %
                                     message.subject)
    review = Review(rietveld, match.groupdict()['id'])

    # Determine recipients and run the handlers one by one.
    recipients = set(util.get_emails(getattr(message, 'to', '')) +
                     util.get_emails(getattr(message, 'cc', '')))
    for addr in recipients:
      match = REVIEW_BOT_RECIPIENT_RE.match(addr)
      if not match:
        continue

      try:
        handler = HANDLERS[match.group(1)]
      except KeyError:
        continue

      try:
        handler(addr, message, review, rietveld)
      except:  # pylint: disable=W0702
        logging.exception('Handler %s failed!', match.group(1))

  def handle_exception(self, exception, debug):
    """Handles exceptions to print HTTP error details.

    Args:
      exception: The exception.
      debug: Whether we're in debug mode.
    """
    if isinstance(exception, webob.exc.HTTPException):
      logging.warning('Request %s failed: %d - %s',
                      self.request.url, exception.code, exception.detail)

    webapp2.RequestHandler.handle_exception(self, exception, debug)


app = webapp2.WSGIApplication([('/_ah/mail/.*', MailDispatcher)])
