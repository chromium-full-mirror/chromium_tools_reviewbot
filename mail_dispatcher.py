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


HANDLERS = {
    'policy_checklist': handlers.policy_checklist.process
}


class MailDispatcher(webapp2.RequestHandler):
  """Dispatches mail to handlers based on email addresses."""

  def post(self):
    """Handles POST requests.

    Parses the incoming mail message. Dispatches to interested handlers based on
    the list of mail recipients.
    """

    # Singleton Rietveld interface for this request.
    rietveld = Rietveld()

    # Parse the message and instantiate the review interface.
    message = mail.InboundEmailMessage(self.request.body)
    match = re.search(r'\(issue *(?P<id>\d+)\)$', message.subject)
    if match is None:
      raise webob.exc.HTTPBadRequest('Failed to parse issue id: %s' %
                                     message.subject)
    review = Review(match.groupdict()['id'], rietveld)

    # Determine recipients and run the handlers one by one.
    recipients = set(util.get_emails(getattr(message, 'to', '')) +
                     util.get_emails(getattr(message, 'cc', '')))
    addr_re = re.compile('^([^@]+)@%s.appspotmail.com$' %
                         app_identity.get_application_id())
    for addr in recipients:
      match = addr_re.match(addr)
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
