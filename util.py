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
  def __init__(self, lookup):
    self.items = {}
    self.lookup = lookup

  def __getitem__(self, name):
    if name not in self.items.keys():
      self.items[name] = self.lookup(name)
    return self.items[name]


class ObjectDict(object):
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
  return [entry[1] for entry in email.utils.getaddresses([string])]
