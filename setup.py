"""Setup script for version_query package."""

import pathlib
import sys

import boilerplates.setup

_HERE = pathlib.Path(__file__).parent.resolve()


def allow_local_version_query() -> None:
    """Add folder of this setup.py to Python path to use packaged code when building the package."""
    sys.path.insert(0, str(_HERE))


class Package(boilerplates.setup.Package):
    """Package metadata."""

    name = 'version-query'
    description = 'Zero-overhead package versioning for Python.'
    url = 'https://github.com/mbdevpl/version-query'
    author = 'Mateusz Bysiek, John Vandenberg'
    maintainer = 'Mateusz Bysiek'
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3.15',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
        'Typing :: Typed']
    install_requires = []


if __name__ == '__main__':
    allow_local_version_query()
    # pylint: disable = wrong-import-position
    from version_query._version import VERSION
    Package.version = VERSION
    Package.setup()
