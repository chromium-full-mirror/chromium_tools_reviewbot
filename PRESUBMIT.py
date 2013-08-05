# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Top-level presubmit script for reviewbot.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts for
details on the presubmit API built into gcl.
"""


def CommonChecks(input_api, output_api):
  output = []

  join = input_api.os_path.join
  root = input_api.PresubmitLocalPath()
  while True:
    if input_api.os_path.isfile(join(root, 'google_appengine', 'VERSION')):
      break
    next_root = input_api.os_path.dirname(root)
    if next_root == root:
      return [output_api.PresubmitError('Failed to find Google AppEngine SDK')]
    root = next_root
  input_api.logging.debug('Found GAE SDK in %s' % root)

  import sys
  sys_path_backup = sys.path
  try:
    sys.path = [
        join(root, 'google_appengine'),
        join(root, 'google_appengine', 'lib'),
        join(root, 'google_appengine', 'lib', 'webapp2-2.5.2'),
        join(root, 'google_appengine', 'lib', 'webob-1.2.3'),
        join('third_party', 'google-api-python-client'),
    ] + sys.path
    output.extend(input_api.canned_checks.RunPylint(
        input_api,
        output_api))
  finally:
    sys.path = sys_path_backup

  return output


def CheckChangeOnUpload(input_api, output_api):
  return CommonChecks(input_api, output_api)


def CheckChangeOnCommit(input_api, output_api):
  return CommonChecks(input_api, output_api)
