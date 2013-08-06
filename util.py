# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import email.utils


def lazy_property(func):
  """A decorator for lazy properties."""
  name = '__lazy_' + func.__name__

  def get_property(self, *args, **kwargs):
    if not hasattr(self, name):
      setattr(self, name, func(self, *args, **kwargs))
    return getattr(self, name)

  return property(get_property)


class LazyDict(object):
  """A simple immutable and lazy dictionary.

  This looks up the actual key values on first access to the key and caches the
  value to speed up subsequent accesses.
  """

  def __init__(self, lookup_fn):
    self.items = {}
    self.lookup = lookup_fn

  def __getitem__(self, name):
    if name not in self.items.keys():
      self.items[name] = self.lookup(name)
    return self.items[name]


class ObjectDict(object):
  """Wraps a dictionary to allow value retrieval in dot notation."""

  def __init__(self, data):
    self.data = data

  def __getitem__(self, name):
    val = self.data[name]
    if type(val) == dict:
      return ObjectDict(val)
    return val

  def __getattr__(self, name):
    try:
      return self[name]
    except KeyError as e:
      raise AttributeError(e)

  def __iter__(self):
    return self.data.iterkeys()


def get_emails(string):
  """Normalizes a string containing a list of email recepients.

  Takes a string in the format present in mail headers and returns a list of
  email addresses. For example, the input
      'test@example.com, committers <committers@chromium.org>
  will produce this return value:
      [ 'test@example.com', 'committers@chromium.org' ]
  """
  return [entry[1] for entry in email.utils.getaddresses([string])]
