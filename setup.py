from setuptools import setup, find_packages

setup(
    name='bandersnatch_filters',
    version='0.1.2',
    entry_points={
        'bandersnatch_filter_plugins.v2.release': [
            'whitelist_pyversion = whitelist_pyversion:WhitelistReleasePyVersion',
            'filter_release = filter_release:ReleaseFilter',
        ],
    },
    py_modules=['whitelist_pyversion', 'filter_release'],
    install_requires=['bandersnatch'],
)
