"""Tests for the version module."""

import unittest
import katversion.version as kv

class TestVersion(unittest.TestCase):

    def test_sane_version(self):
        t_ver = "v0.1.2"
        vertuple = kv._sane_version_list(t_ver.split("."))
        self.assertEquals(vertuple, ('0', '1', '2'))
