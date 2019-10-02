import logging
from typing import List

from packaging.requirements import Requirement
from packaging.version import InvalidVersion, Version

from bandersnatch.filter import FilterReleasePlugin

logger = logging.getLogger("bandersnatch")

class WhitelistReleasePyVersion(FilterReleasePlugin):
    name = "whitelist_release_pyversion"
    # Requires iterable default
    whitelist_pyversions: List[Requirement] = []

    def initialize_plugin(self):
        """
        Initialize the plugin
        """
        # Generate a list of whitelisted python version from the configuration and
        # store it into self.whitelist_pyversions attribute so this
        if not self.whitelist_pyversions:
            self.whitelist_pyversions = (
                self._determine_unfiltered_python_versions()
            )
            logger.info(
                f"Initialized release plugin {self.name}, filtering "
                + f"{self.whitelist_pyversions}"
            )

    def _determine_unfiltered_python_versions(self):
        """
        Parse the configuration file for [whitlist] python_versions

        Returns
        -------
        list of python versions
        """
        unfiltered_pyversions = set()
        try:
            lines = self.configuration["whitelist"]["python_versions"]
            version_lines = lines.split("\n")
        except KeyError:
            version_lines = []
        for version_line in version_lines:
            version_line = version_line.strip()
            if not version_line or version_line.startswith("#"):
                continue
            unfiltered_pyversions.add(version_line)   
        return list(unfiltered_pyversions)

    def filter(self, info, releases):
        name = info["name"]
        for version in list(releases.keys()):
            releases[version] = [f for f in releases[version] if self._check_match(name, f['python_version'])]
            if len(releases[version]) == 0:
                del releases[version]

    def _check_match(self, name, python_version) -> bool:
        """
        Check if the release python version matches against a whitelisted
        python version specifier.

        Parameters
        ==========
        name: str
            Package name

        python_version: str
            Python version specifier

        Returns
        =======
        bool:
            True if it matches, False otherwise.
        """
        if not python_version:
            return False

        for whitelisted_version in self.whitelist_pyversions: 
            if python_version == whitelisted_version:
                logger.debug(
                    f"MATCH: Release {name} with python_version = {python_version} matches specifier "
                    f"{whitelisted_version}"
                ) 
                return True           

        return False
