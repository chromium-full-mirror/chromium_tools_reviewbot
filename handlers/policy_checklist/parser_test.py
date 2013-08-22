#!/usr/bin/env python
# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

import patching
import handlers.policy_checklist.parser


def parse_patch_to_chunks(text):
  lines = patching.ParsePatchToLines(text.splitlines())
  return handlers.policy_checklist.parser.parse(lines)


class PolicyChecklistParserTest(unittest.TestCase):
  def test_basic_addition(self):
    self.assertEquals([
        {
            'start': [None, 4985],
            'end': [None, 5003],
            'comment_pos': [None, 4986],
            'additions': True,
            'removals': False,
        }], parse_patch_to_chunks("""
Index: chrome/app/policy/policy_templates.json
diff --git a/chrome/app/policy/policy_templates.json b/chrome/app/policy/policy_templates.json
index 7fca71bb7cae78f36f65ec166671a9596cd63a4b..52680ca8ee898a0f1a81c00a7cef669e38fcac51 100644
--- a/chrome/app/policy/policy_templates.json
+++ b/chrome/app/policy/policy_templates.json
@@ -112,7 +112,7 @@
 #   persistent IDs for all fields (but not for groups!) are needed. These are
 #   specified by the 'id' keys of each policy. NEVER CHANGE EXISTING IDs,
 #   because doing so would break the deployed wire format!
-#   For your editing convenience: highest ID currently used: 218
+#   For your editing convenience: highest ID currently used: 219
 #
 # Placeholders:
 #   The following placeholder strings are automatically substituted:
@@ -4982,6 +4982,24 @@
 
           This policy is for internal use by Chrome itself.''',
         },
+        {
+          'name': 'SupervisedUsersEnabled',
+          'type': 'main',
+          'schema': { 'type': 'boolean' },
+          'supported_on': ['chrome_os:29-'],
+          'device_only': True,
+          'features': {
+            'dynamic_refresh': False,
+          },
+          'example_value': True,
+          'id': 219,
+          'caption': '''Enable supervised users.''',
+          'desc': '''If set to true, it is possible to create and log in as a supervised user.
+
+          If set to false or not configured, supervised users creation and login will be disabled. All existing supervised users will be hidden.
+
+          NOTE: The default behavior for consumer and enterprise devices differs: on consumer devices supervised users are enabled by default, but on enterprice devices they aren't.'''
+        },
       ],
     },
   ],
"""))

  def test_one_addition_shifted(self):
    self.assertEquals([
        {
            'start': [None, 4068],
            'end': [None, 4081],
            'comment_pos': [None, 4068],
            'additions': True,
            'removals': False,
        }], parse_patch_to_chunks("""
Index: chrome/app/policy/policy_templates.json
diff --git a/chrome/app/policy/policy_templates.json b/chrome/app/policy/policy_templates.json
index 1cc92452f6375b7b718c232c42f29d19816554aa..10ad804e04cdcec44eaee5438caa82435b799671 100644
--- a/chrome/app/policy/policy_templates.json
+++ b/chrome/app/policy/policy_templates.json
@@ -117,7 +117,7 @@
 #   persistent IDs for all fields (but not for groups!) are needed. These are
 #   specified by the 'id' keys of each policy. NEVER CHANGE EXISTING IDs,
 #   because doing so would break the deployed wire format!
-#   For your editing convenience: highest ID currently used: 235
+#   For your editing convenience: highest ID currently used: 236
 #
 # Placeholders:
 #   The following placeholder strings are automatically substituted:
@@ -4065,6 +4065,20 @@
       The format of the value follows the names of timezones in the "IANA Time Zone Database" (see "http://en.wikipedia.org/wiki/List_of_tz_database_time"). In particular, most timezones can be referred to by "continent/large_city" or "ocean/large_city".''',
     },
     {
+      'name': 'SystemUse24HourClock',
+      'type': 'main',
+      'schema': { 'type': 'boolean' },
+      'supported_on': ['chrome_os:30-'],
+      'device_only': True,
+      'features': {
+        'dynamic_refresh': True,
+      },
+      'example_value': True,
+      'id': 236,
+      'caption': '''Use 24 hour clock by default''',
+      'desc': '''Specifies the clock format be used for the device. Users can override clock format for the current session. However, on logout it is set back to the specified value. If an empty string is provided, device owner preference is used.''',
+    },
+    {
       'name': 'ShowLogoutButtonInTray',
       'type': 'main',
       'schema': { 'type': 'boolean' },
"""))

  def test_nested_blocks(self):
    self.assertEquals([
        {
            'start': [None, 5256],
            'end': [None, 5290],
            'comment_pos': [None, 5259],
            'additions': True,
            'removals': False,
        }], parse_patch_to_chunks("""
Index: chrome/app/policy/policy_templates.json
diff --git a/chrome/app/policy/policy_templates.json b/chrome/app/policy/policy_templates.json
index 86bc3ac3677d3405afdf39f17c7be373fc0fa0d1..3a32920b3d745fb50432cc15a11a45b8f88a95d8 100644
--- a/chrome/app/policy/policy_templates.json
+++ b/chrome/app/policy/policy_templates.json
@@ -5253,6 +5253,40 @@
         },
       ],
     },
+    # TODO(joaodasilva): replace the 'dict' type with a more generic
+    # 'json' type. The actual schema type for this should be 'array'.
+    {
+      'name': 'ManagedBookmarks',
+      'type': 'dict',
+      'schema': {
+        'type': 'object',
+        'items': {
+          'type': 'object',
+          'properties': {
+            'name': { 'type': 'string' },
+            'url': { 'type': 'string' },
+          },
+        },
+      },
+      'supported_on': ['android:30-'],
+      'features': {
+        'dynamic_refresh': True,
+        'per_profile': True,
+      },
+      'future': True,
+      'example_value': { "name": "Google", "url": "google.com" },
+      'id': 227,
+      'caption': '''Managed Bookmarks''',
+      'desc': '''Configures a list of managed bookmarks.
+
+      The policy is a list of bookmarks, and each bookmark is a dictionary containing the bookmark "name" and target "url".
+
+      These bookmarks are placed in a Managed bookmarks folder inside the Mobile bookmarks. These bookmarks can't be modified by the user.
+
+      When this policy is set then the Managed bookmarks are the default folder opened when the bookmarks view is opened in Chrome.
+
+      Managed bookmarks are not synced to the user account.''',
+    },
   ],
   'messages': {
     # Messages that are not associated to any policies.
"""))

  def test_two_additions(self):
    self.assertEquals([
        {
            'start': [None, 4502],
            'end': [None, 4525],
            'comment_pos': [None, 4503],
            'additions': True,
            'removals': False,
        }, {
            'start': [None, 4525],
            'end': [None, 4548],
            'comment_pos': [None, 4526],
            'additions': True,
            'removals': False,
        }], parse_patch_to_chunks("""
Index: chrome/app/policy/policy_templates.json
diff --git a/chrome/app/policy/policy_templates.json b/chrome/app/policy/policy_templates.json
index 3abaf03cb7529667e01472287eb56773bdcbfc69..fbd4a5bc36fc09825eb321ad100088416610b50a 100644
--- a/chrome/app/policy/policy_templates.json
+++ b/chrome/app/policy/policy_templates.json
@@ -112,7 +112,7 @@
 #   persistent IDs for all fields (but not for groups!) are needed. These are
 #   specified by the 'id' keys of each policy. NEVER CHANGE EXISTING IDs,
 #   because doing so would break the deployed wire format!
-#   For your editing convenience: highest ID currently used: 210
+#   For your editing convenience: highest ID currently used: 214
 #
 # Placeholders:
 #   The following placeholder strings are automatically substituted:
@@ -4499,6 +4499,52 @@
 
           If this policy is left unset, Accessibility options will not appear in the system tray menu, but the user can cause the Accessibility options to appear via the Settings page.'''
         },
+        {
+          'name': 'LargeCursorEnabled',
+          'type': 'main',
+          'schema': { 'type': 'boolean' },
+          'supported_on': ['chrome_os:29-'],
+          'features': {
+            'can_be_recommended': True,
+            'dynamic_refresh': True,
+            'per_profile': True,
+          },
+          'example_value': True,
+          'id': 211,
+          'caption': '''Enable large cursor''',
+          'desc': '''Enable the large cursor accessibility feature.
+
+          If this policy is set to true, the large cursor will always be enabled.
+
+          If this policy is set to false, the large cursor will always be disabled.
+
+          If you set this policy, users cannot change or override it.
+
+          If this policy is left unset, the large cursor is disabled initially but can be enabled by the user anytime.'''
+        },
+        {
+          'name': 'SpokenFeedbackEnabled',
+          'type': 'main',
+          'schema': { 'type': 'boolean' },
+          'supported_on': ['chrome_os:29-'],
+          'features': {
+            'can_be_recommended': True,
+            'dynamic_refresh': True,
+            'per_profile': True,
+          },
+          'example_value': True,
+          'id': 212,
+          'caption': '''Enable spoken feedback''',
+          'desc': '''Enable the spoken feedback accessibility feature.
+
+          If this policy is set to true, spoken feedback will always be enabled.
+
+          If this policy is set to false, spoken feedback will always be disabled.
+
+          If you set this policy, users cannot change or override it.
+
+          If this policy is left unset, spoken feedback is disabled initially but can be enabled by the user anytime.'''
+        },
       ],
     },
     {
"""))

  def test_group_additions(self):
    self.assertEquals([
        {
            'start': [None, 4523],
            'end': [None, 4545],
            'comment_pos': [None, 4530],
            'additions': True,
            'removals': False,
        }, {
            'start': [None, 4545],
            'end': [None, 4564],
            'comment_pos': [None, 4546],
            'additions': True,
            'removals': False,
        }], parse_patch_to_chunks("""
Index: chrome/app/policy/policy_templates.json
diff --git a/chrome/app/policy/policy_templates.json b/chrome/app/policy/policy_templates.json
index 6a1293696283e232070e61104a369e52a615cdf1..dad016adf0ae2055a6e7cb1275fb99d33c703ab2 100644
--- a/chrome/app/policy/policy_templates.json
+++ b/chrome/app/policy/policy_templates.json
@@ -112,7 +112,7 @@
 #   persistent IDs for all fields (but not for groups!) are needed. These are
 #   specified by the 'id' keys of each policy. NEVER CHANGE EXISTING IDs,
 #   because doing so would break the deployed wire format!
-#   For your editing convenience: highest ID currently used: 199
+#   For your editing convenience: highest ID currently used: 201
 #
 # Placeholders:
 #   The following placeholder strings are automatically substituted:
@@ -4520,6 +4520,49 @@
 
       If not specified, will not modify the Variations seed URL.''',
     },
+    {
+      'name': 'Attestation',
+      'type': 'group',
+      'caption': 'Remote Attestation',
+      'desc': 'Configure the remote attestation with TPM mechanism.',
+      'policies': [
+        {
+          'name': 'AttestationEnabledForUser',
+          'type': 'main',
+          'schema': { 'type': 'boolean' },
+          'supported_on': ['chrome_os:28-'],
+          'features': {
+            'dynamic_refresh': True,
+            'per_profile': True,
+          },
+          'example_value': True,
+          'id': 200,
+          'caption': '''Enable remote attestation for the user.''',
+          'desc': '''If true, the user can use the hardware on Chrome devices to remote attest its identity to the privacy CA via the Enterprise Platform Keys API chrome.enterprise.platformKeysPrivate.challengeUserKey().
+
+          If it is set to false, or if it is not set, calls to the API will fail with an error code.''',
+        },
+        {
+          'name': 'AttestationExtensionWhitelist',
+          'type': 'list',
+          'schema': {
+            'type': 'array',
+            'items': { 'type': 'string' },
+          },
+          'supported_on': ['chrome_os:28-'],
+          'features': {
+            'dynamic_refresh': True,
+            'per_profile': True,
+          },
+          'example_value': ['ghdilpkmfbfdnomkmaiogjhjnggaggoi'],
+          'id': 201,
+          'caption': '''Extensions allowed to to use the remote attestation API.''',
+          'desc': '''This policy specifies the allowed extensions to use Enterprise Platform Keys API chrome.enterprise.platformKeysPrivate.challengeUserKey() for remote attestation. Extensions must be added to this list to use the API.
+
+          If an extension is not in the list, or the list is not set, the call to the API will fail with an error code.''',
+        },
+      ],
+    },
   ],
   'messages': {
     # Messages that are not associated to any policies.
"""))

  def test_simple_edit(self):
    self.assertEquals([
        {
            'start': [300, 300],
            'end': [301, 301],
            'comment_pos': [300, 300],
            'additions': True,
            'removals': True,
        }], parse_patch_to_chunks("""
Index: chrome/app/policy/policy_templates.json
diff --git a/chrome/app/policy/policy_templates.json b/chrome/app/policy/policy_templates.json
index 02e1801f8906343b6168f86c45ae3b2c0c9f5363..86bc3ac3677d3405afdf39f17c7be373fc0fa0d1 100644
--- a/chrome/app/policy/policy_templates.json
+++ b/chrome/app/policy/policy_templates.json
@@ -297,7 +297,7 @@
       'name': 'DisableSpdy',
       'type': 'main',
       'schema': { 'type': 'boolean' },
-      'supported_on': ['chrome.*:8-', 'chrome_os:0.11-'],
+      'supported_on': ['chrome.*:8-', 'chrome_os:0.11-', 'android:30-'],
       'features': {
         'dynamic_refresh': True,
         'per_profile': False,
"""))

  def test_complex_edit(self):
    self.assertEquals([
        {
            'start': [328, 328],
            'end': [332, 335],
            'comment_pos': [328, 328],
            'additions': True,
            'removals': True,
        }], parse_patch_to_chunks("""
Index: chrome/app/policy/policy_templates.json
diff --git a/chrome/app/policy/policy_templates.json b/chrome/app/policy/policy_templates.json
index 602196317bd5bc00ed0884c2ef3e563910820686..c38156df31142a39a6b6fa215bc629f2ca0e7f94 100644
--- a/chrome/app/policy/policy_templates.json
+++ b/chrome/app/policy/policy_templates.json
@@ -325,10 +325,13 @@
         'dynamic_refresh': True,
         'per_profile': False,
       },
-      'example_value': ['file', 'mailto'],
+      'deprecated': True,
+      'example_value': ['file', 'https'],
       'id': 85,
       'caption': '''Disable URL protocol schemes''',
-      'desc': '''Disables the listed protocol schemes in <ph name="PRODUCT_NAME">$1<ex>Google Chrome</ex></ph>.
+      'desc': '''This policy is deprecated, please use URLBlacklist instead.
+
+      Disables the listed protocol schemes in <ph name="PRODUCT_NAME">$1<ex>Google Chrome</ex></ph>.
 
       URLs using a scheme from this list will not load and can not be navigated to.
"""))

  def test_enum_item_names_ignored_for_comment_pos(self):
    self.assertEquals([
        {
            'start': [None, 3323],
            'end': [None, 3363],
            'comment_pos': [None, 3324],
            'additions': True,
            'removals': False,
        }], parse_patch_to_chunks("""
Index: chrome/app/policy/policy_templates.json
diff --git a/chrome/app/policy/policy_templates.json b/chrome/app/policy/policy_templates.json
index c888dcbf4fc32656c048054ca149e245989281d5..7de3edae00f1e8ff5984be8f10091ee044655d8a 100644
--- a/chrome/app/policy/policy_templates.json
+++ b/chrome/app/policy/policy_templates.json
@@ -112,7 +112,7 @@
 #   persistent IDs for all fields (but not for groups!) are needed. These are
 #   specified by the 'id' keys of each policy. NEVER CHANGE EXISTING IDs,
 #   because doing so would break the deployed wire format!
-#   For your editing convenience: highest ID currently used: 165
+#   For your editing convenience: highest ID currently used: 166
 #
 # Placeholders:
 #   The following placeholder strings are automatically substituted:
@@ -3320,6 +3320,46 @@
 
       If this policy is left not set, the users will be able to change whether the built-in DNS client is used by editing chrome://flags or specifying a command-line flag.''',
     },
+    {
+      'name': 'ShelfAutoHideBehavior',
+      'type': 'string-enum',
+      'schema': {
+        'type': 'string',
+        'enum': [
+          'Always',
+          'Never'
+        ],
+      },
+      'items': [
+        {
+          'name': 'AlwaysAutoHideShelf',
+          'value': 'Always',
+          'caption': '''Always auto-hide the shelf''',
+        },
+        {
+          'name': 'NeverAutoHideShelf',
+          'value': 'Never',
+          'caption': '''Never auto-hide the shelf''',
+        },
+      ],
+      'supported_on': ['chrome_os:25-'],
+      'features': {
+        'dynamic_refresh': True,
+        'can_be_recommended': True,
+      },
+      'example_value': 'Always',
+      'id': 166,
+      'caption': '''Control shelf auto-hiding''',
+      'desc': '''Control auto-hiding of the <ph name="PRODUCT_OS_NAME">$2<ex>Google Chrome OS</ex></ph> shelf.
+
+      If this policy is set to 'AlwaysAutoHideShelf', the shelf will always auto-hide.
+
+      If this policy is set to 'NeverAutoHideShelf', the shelf never auto-hide.
+
+      If you set this policy, users cannot change or override it.
+
+      If the policy is left not set, users can choose whether the shelf should auto-hide.''',
+    },
   ],
   'messages': {
     # Messages that are not associated to any policies.
"""))


if __name__ == '__main__':
  unittest.main()
