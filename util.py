# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import email.utils


def lazy_property(func):
  """A decorator for lazy properties."""
  name = '__lazy_' + func.__name__

  def get_property(self, *args, **kwargs):
    if not hasattr(self, name):
      setattr(self, name, func(self, *args, **kwargs))
    return getattr(self, name)

  return property(get_property)


class LazyDict(collections.Mapping):
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

  def __iter__(self):
    return self.items.iterkeys()

  def __len__(self):
    return len(self.items)

  def __repr__(self):
    return repr(self.items)


class ObjectDict(collections.Mapping):
  """Wraps a dictionary to allow value retrieval in dot notation."""

  def __init__(self, data):
    self.__data = data

  def __getitem__(self, name):
    val = self.__data[name]
    return ObjectDict.wrap(val)

  def __getattr__(self, name):
    try:
      return self[name]
    except KeyError as e:
      raise AttributeError(e)

  def __iter__(self):
    return self.__data.iterkeys()

  def __len__(self):
    return len(self.__data)

  def __repr__(self):
    return repr(self.__data)

  @staticmethod
  def wrap(val):
    if isinstance(val, dict):
      return ObjectDict(val)
    return val


def get_emails(string):
  """Normalizes a string containing a list of email recepients.

  Takes a string in the format present in mail headers and returns a list of
  email addresses. For example, the input
      'test@example.com, committers <committers@chromium.org>
  will produce this return value:
      [ 'test@example.com', 'committers@chromium.org' ]
  """
  return [entry[1] for entry in email.utils.getaddresses([string])]


def canonicalize_email(address):
  """Takes an email address and returns its canonicalized form."""
  emails = get_emails(address)
  assert len(emails) == 1
  return emails[0]
