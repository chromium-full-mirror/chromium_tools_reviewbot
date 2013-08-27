# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Request handler for the /admin/app_config page.

Allows admins to set configuration parameter via the appengine admin console.
"""

import cgi
import webapp2

import third_party  # pylint: disable=W0611

import model.app_config
import rietveld


FIELDS = ('client_id', 'service_account_key', 'server_url', 'nickname')


class AppConfigHandler(webapp2.RequestHandler):
  """Handles /admin/appconfig."""

  def post(self):
    """Handles POST requests to update app config.

    Parses the request data, writes it to the data store entity, and sends a
    request to rietveld to update the app's nickname.
    """
    app_config = model.app_config.get()
    for field in FIELDS:
      setattr(app_config, field, self.request.get(field, None))
    app_config.put()

    # Set the nickname with rietveld.
    rv = rietveld.Rietveld()
    settings_payload = {
        'column_width': 80,  # required field
        'nickname': app_config.nickname,
    }

    try:
      rv.post_data('settings', settings_payload)
    except rietveld.RietveldRequestError as e:
      # Redirect indicates success.
      if e[1].status != 302:
        raise e

    self.RenderForm()

  def get(self):
    """Handles GET requests."""
    self.RenderForm()

  def RenderForm(self):
    """Renders the app config form to the client."""
    app_config = model.app_config.get()
    self.response.write('<html><body><form action="%s" method="post"><table>' %
                        self.request.path)
    for field in FIELDS:
      self.response.write(
          '<tr><td>%s</td><td><textarea name="%s">%s</textarea></td></tr>' %
          (field, field, cgi.escape(getattr(app_config, field) or '')))
    self.response.write('<tr><td><input type="submit" value="Set"></td></tr>')
    self.response.write('</table><form></body></body>')


app = webapp2.WSGIApplication([('/admin/app_config', AppConfigHandler)])
