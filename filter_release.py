import logging
from operator import itemgetter

from packaging.requirements import Requirement
from packaging.version import parse, Version

from bandersnatch.filter import FilterReleasePlugin

logger = logging.getLogger("bandersnatch")


class ReleaseFilter(FilterReleasePlugin):
    """
    Plugin to download only latest releases
    """

    name = "filter_release"
    keep = 0  # by default, keep 'em all

    def initialize_plugin(self):
        """
        Initialize the plugin reading patterns from the config.
        """
        if self.keep:
            return

        self.whitelisted_releases = []

        try:
            self.keep = int(self.configuration["filter_release"]["keep"])
            self.whitelisted_releases = self._determine_filtered_package_requirements()
        except KeyError:
            return
        except ValueError:
            return
        if self.keep > 0:
            logger.info(f"Initialized latest releases plugin with keep={self.keep} "
                        f"with whitelisted releases = {self.whitelisted_releases}")

    def filter(self, info, releases):
        """
        Keep the latest releases
        """

        if self.keep == 0:
            return

        name = info["name"]

        versions = list(releases.keys())
        before = len(versions)

        if before <= self.keep:
            # not enough releases: do nothing
            return

        versions_pair = map(lambda v: (parse(v), v), versions)
        latest = sorted(versions_pair)[-self.keep :]  # noqa: E203
        latest = list(map(itemgetter(1), latest))

        current_version = info.get("version")
        if current_version and (current_version not in latest):
            # never remove the stable/official version
            latest[0] = current_version

        logger.debug(f"old {versions}")
        logger.debug(f"new {latest}")

        after = len(latest)
        latest = set(latest)
        for version in list(releases.keys()):
            if version not in latest:
                if not self._whitelisted_release(name, version):
                    del releases[version]

        logger.debug(f"{self.name}: releases removed: {before - after}")

    def _whitelisted_release(self, name, version):
        """
        Check if the package name and version matches against a whitelisted
        package version specifier.

        Parameters
        ==========
        name: str
            Package name

        version: str
            Package version

        Returns
        =======
        bool:
            True if it matches, False otherwise.
        """

        for release in self.whitelisted_releases:
            if name != release.name:
                continue
            if Version(version) in release.specifier:
                logger.debug(
                    f"MATCH: Release {name}=={version} matches specifier "
                    f"{release.specifier}"
                )
                return True
        return False

    def _determine_filtered_package_requirements(self):
        """
        Parse the configuration file for specific packages versions

        Returns
        -------
        list of packaging.requirements.Requirement
            For all PEP440 package specifiers
        """
        filtered_requirements = set()
        try:
            lines = self.configuration["filter_release"]["releases"]
            package_lines = lines.split("\n")
        except KeyError:
            package_lines = []
        for package_line in package_lines:
            package_line = package_line.strip()
            if not package_line or package_line.startswith("#"):
                continue
            filtered_requirements.add(Requirement(package_line))
        
        return list(filtered_requirements)
