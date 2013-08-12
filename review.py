# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json

import patching
import util


class Patch(object):
  """Helper class for lazily loading and parsing patch data."""

  def __init__(self, rietveld, issue_id, patchset_id, patch_id):
    self.rietveld = rietveld
    self.issue_id = issue_id
    self.patchset_id = patchset_id
    self.patch_id = patch_id

  @util.lazy_property
  def raw(self):
    return self.rietveld.post_data(
        'download/issue%s_%s_%s.diff' %
        (self.issue_id, self.patchset_id, self.patch_id))

  @util.lazy_property
  def lines(self):
    return patching.ParsePatchToLines(self.raw.splitlines())


class Review(object):
  """Represents a code review.

  Information from rietveld can be obtained via the following properties:
   - |issue_id| is the issue identifier.
   - |issue_data| contains issue meta data as retrieved from rietveld. The data
     is pulled lazily from the rietveld API on first access.
   - |patchsets| has lazily-pulled patchset meta data, indexed by patchset IDa.

  The subclass may then do its processing and trigger any actions. In
  particular, the |rietveld| object may be used to update rietveld issue state.
  """
  def __init__(self, rietveld, issue_id):
    self.rietveld = rietveld
    self.issue_id = issue_id

  @util.lazy_property
  def issue_data(self):
    json_data = self.rietveld.post_data('api/%s?messages=true' % self.issue_id)
    data = json.loads(json_data)
    data['messages'] = [util.ObjectDict(msg) for msg in data['messages']]
    return util.ObjectDict(data)

  @util.lazy_property
  def patchsets(self):
    def retrieve_patchset(ps):
      json_patchset_data = self.rietveld.post_data('api/%s/%s' %
                                                   (self.issue_id, ps))
      patchset_data = json.loads(json_patchset_data)

      # Amend the files property so it can lazily load and return patch data.
      for file_data in patchset_data.get('files', {}).values():
        file_data['patch'] = Patch(self.rietveld, self.issue_id, ps,
                                   file_data['id'])

      return util.ObjectDict(patchset_data)

    return util.LazyDict(retrieve_patchset)

  @util.lazy_property
  def latest_patchset(self):
    return self.patchsets[self.issue_data.patchsets[-1]]
