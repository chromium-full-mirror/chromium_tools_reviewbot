# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from oauth2client.client import SignedJwtAssertionCredentials
import httplib2
import model.app_config
import urllib
import util


EMAIL_SCOPE = 'https://www.googleapis.com/auth/userinfo.email'


class RietveldRequestError(Exception):
  """Raised on request errors."""


class Rietveld(object):
  def __init__(self):
    self.app_config = model.app_config.get()

  @util.lazy_property
  def http(self):
    http = httplib2.Http()

    creds = SignedJwtAssertionCredentials(self.app_config.client_id,
                                          self.app_config.service_account_key,
                                          EMAIL_SCOPE)
    creds.authorize(http)
    return http

  @util.lazy_property
  def xsrf_token(self):
    return self.make_request('xsrf_token',
                             headers = {'X-Requesting-XSRF-Token': 1})

  def make_request(self, req, *args, **kwargs):
    resp, response = self.http.request(
        '%s/%s' % (self.app_config.server_url, req), *args, **kwargs)
    if resp.status != 200:
      raise RietveldRequestError(
          'Rietveld %s request failed: %s\n%s' %
          (req, resp.status, str(resp)), resp, response)

    return response

  def post_data(self, req, payload = None):
    actual_payload = dict(payload or {})
    actual_payload['xsrf_token'] = self.xsrf_token

    return self.make_request(req, method = 'POST',
                             body = urllib.urlencode(actual_payload))

  def post_issue_data(self, issue, req, payload):
    return self.post_data('%s/%s' % (issue, req), payload)

  def post_comment(self, issue, comment, submit_inline_comments = False):
    publish_payload = {
        'message_only': 0 if submit_inline_comments else 1,
        'send_mail': 1,
        'add_as_reviewer': 0,
        'message': comment,
        'no_redirect': 1,
    }
    self.post_issue_data(issue, 'publish', publish_payload)

  def add_inline_comment(self, issue_id, patchset_id, patch_id, line, a_or_b,
                         comment):
    comment_payload = {
        'snapshot': 'old' if a_or_b is 'a' else 'new',
        'lineno': line,
        'side': a_or_b,
        'issue': issue_id,
        'patchset': patchset_id,
        'patch': patch_id,
        'text': comment,
    }
    self.post_data('inline_draft', comment_payload)
