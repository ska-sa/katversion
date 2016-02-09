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

    def test_next_version(self):
        t_ver = {"v0.1.2": "v0.1.3",
                 "karoocamv9": "karoocamv10",
                 "1.2": "1.3"}
        for ver, test_nextver in t_ver.items():
            nextver = kv._next_version(ver)
            self.assertEquals(nextver, test_nextver)
