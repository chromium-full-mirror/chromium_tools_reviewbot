# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from google.appengine.ext import ndb


class AppConfig(ndb.Model):
  """Application configuration data."""
  client_id = ndb.TextProperty()
  service_account_key = ndb.TextProperty()
  server_url = ndb.TextProperty()
  nickname = ndb.TextProperty()


def get():
  config = ndb.Key(AppConfig, 'config').get()
  if config is None:
    config = AppConfig(id = 'config')
  return config
