# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Top-level presubmit script for reviewbot.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts for
details on the presubmit API built into gcl.
"""

def GetUnitTests(input_api, output_api, pythonpath):
  """Finds all unit tests to run within the source tree."""
  tests = []
  for root, dirs, files in input_api.os_walk(input_api.PresubmitLocalPath()):
    # Don't recurse in blacklisted directories.
    blacklist = ['.svn', '.git', 'third_party']
    dirs[:] = filter(lambda d : d not in blacklist, dirs)

    # Add all files ending in _test.py to the list of tests.
    test_files = filter(lambda f: f.endswith('_test.py'), files)
    tests.extend([input_api.os_path.join(root, f) for f in test_files])

  # A helper to augment PYTHONPATH in the unit test command environment.
  def augment_pythonpath_in_environment(cmd):
    env = cmd.kwargs.get('env', {})
    new_env_path = input_api.os_path.pathsep.join(pythonpath)
    if 'PYTHONPATH' in env:
      new_env_path += input_api.os_path.pathsep + env['PYTHONPATH']
    env['PYTHONPATH'] = new_env_path
    cmd.kwargs['env'] = env
    return cmd

  # Create the commands.
  return map(
      augment_pythonpath_in_environment,
      input_api.canned_checks.GetUnitTests(input_api, output_api, tests))


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
        input_api.PresubmitLocalPath(),
    ] + sys.path

    output.extend(input_api.RunTests(
        input_api.canned_checks.GetPylint(
            input_api,
            output_api) +
        GetUnitTests(input_api, output_api, sys.path)))
  finally:
    sys.path = sys_path_backup

  return output


def CheckChangeOnUpload(input_api, output_api):
  return CommonChecks(input_api, output_api)


def CheckChangeOnCommit(input_api, output_api):
  return CommonChecks(input_api, output_api)
