import os
from collections import defaultdict
from tempfile import TemporaryDirectory
import unittest
import json
from unittest import TestCase

import bandersnatch.filter
from bandersnatch.configuration import BandersnatchConfig
from bandersnatch.master import Master
from bandersnatch.mirror import Mirror
from bandersnatch.package import Package

TEST_CONF = "test.conf"
TEST_JSON = "tesedml.json"

class TestPlugins(TestCase):
    def test__filter__pyversions(self):
        instance = BandersnatchConfig()
        instance.config_file = TEST_CONF
        instance.load_configuration()

        with open(TEST_JSON) as json_file:
            package_json = json.load(json_file)

        mirror = Mirror(".", Master(url="https://foo.bar.com"))
        pkg = Package("foo", 1, mirror)
        pkg.info = package_json["info"]
        pkg.releases = package_json["releases"]

        pkg._filter_releases()

        self.assertEqual(set([v['python_version'] for v in pkg.releases["0.4.3"]]), set(['cp35', 'cp36']))


if __name__ == '__main__':
    unittest.main()