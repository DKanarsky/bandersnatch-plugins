import os
from collections import defaultdict
from tempfile import TemporaryDirectory
import unittest
from unittest import TestCase

import bandersnatch.filter
from bandersnatch.configuration import BandersnatchConfig
from bandersnatch.master import Master
from bandersnatch.mirror import Mirror
from bandersnatch.package import Package

TEST_CONF = "test.conf"

class TestPlugins(TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.tempdir = TemporaryDirectory()
        bandersnatch.filter.loaded_filter_plugins = defaultdict(list)
        os.chdir(self.tempdir.name)

    def tearDown(self):
        if self.tempdir:
            os.chdir(self.cwd)
            self.tempdir.cleanup()
            self.tempdir = None

    def test__plugin__loads__explicitly_enabled(self):
        with open(TEST_CONF, "w") as testconfig_handle:
            testconfig_handle.write(
                """\
[plugins]
enabled =
    whitelist_release_pyversion
"""
            )
        instance = BandersnatchConfig()
        instance.config_file = TEST_CONF
        instance.load_configuration()

        plugins = bandersnatch.filter.filter_release_plugins()
        names = [plugin.name for plugin in plugins]
        self.assertListEqual(names, ["whitelist_release_pyversion"])
        self.assertEqual(len(plugins), 1)

    def test__plugin__loads__default(self):
        with open(TEST_CONF, "w") as testconfig_handle:
            testconfig_handle.write(
                """\
[plugins]
"""
            )
        instance = BandersnatchConfig()
        instance.config_file = TEST_CONF
        instance.load_configuration()

        plugins = bandersnatch.filter.filter_project_plugins()
        names = [plugin.name for plugin in plugins]
        self.assertNotIn("whitelist_release_pyversion", names)

    def test__filter__matches__package(self):
        with open(TEST_CONF, "w") as testconfig_handle:
            testconfig_handle.write(
                """\
[plugins]
enabled =
    whitelist_release_pyversion

[whitelist]
python_versions =
    foo
"""
            )
        instance = BandersnatchConfig()
        instance.config_file = TEST_CONF
        instance.load_configuration()

        mirror = Mirror(".", Master(url="https://foo.bar.com"))
        pkg = Package("foo", 1, mirror)
        pkg.info = {"name": "foo"}
        pkg.releases = {"1.2.0": [{'python_version': 'foo'}, {'python_version': 'foo2'}], "1.2.1": [{'python_version': 'foo2'}]}

        pkg._filter_releases()

        self.assertListEqual(list(pkg.releases.keys()), ["1.2.0"])
        self.assertEqual(len(pkg.releases["1.2.0"]), 1)
        self.assertEqual(pkg.releases["1.2.0"][0], {'python_version': 'foo'})


if __name__ == '__main__':
    unittest.main()