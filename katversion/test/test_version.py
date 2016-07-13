################################################################################
# Copyright (c) 2014-2016, National Research Foundation (Square Kilometre Array)
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at
#
#   https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

"""Tests for the version module."""

import unittest
import katversion.version as kv


class TestVersion(unittest.TestCase):

    def test_sane_version(self):
        t_ver = {"v0.1.2": [0, 1, '2'],
                 "99.88.dev1234+345.678": [99, 88, "dev1234+345.678"],
                 "foo.bar": [0, 0, "foo", "bar"]}
        for ver, test_verlist in t_ver.items():
            verlist = kv._sane_version_list(ver.split(".", 2))
            self.assertEquals(verlist, test_verlist)
