"""Setup script for version_query package."""

import setup_boilerplate


class Package(setup_boilerplate.Package):
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
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
        'Typing :: Typed']
    keywords = [
        'automation', 'continous integration', 'git', 'releasing', 'semantic versioning', 'tagging',
        'versioning']


if __name__ == '__main__':
    Package.setup()
