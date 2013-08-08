# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import sys

def add_import_path(*args):
  sys.path.append(os.path.join(*((os.path.dirname(__file__),) + args)))

add_import_path('third_party', 'google-api-python-client')
