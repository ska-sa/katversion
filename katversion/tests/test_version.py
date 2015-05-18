"""Tests for the version module."""

import unittest
import katversion.version as kv


class TestVersion(unittest.TestCase):

    def test_sane_version(self):
        t_ver = {"v0.1.2": ['0', '1', '2'],
                 "99.88.dev1234+345.678": ["99", "88", "dev1234+345.678"]}
        for ver, test_verlist in t_ver.items():
            verlist = kv._sane_version_list(ver.split(".", 2))
            self.assertEquals(verlist, test_verlist)
