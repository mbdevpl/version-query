"""Setup script for version_query package."""

import setup_boilerplate


class Package(setup_boilerplate.Package):

    """Package metadata."""

    name = 'version-query'
    description = 'Package version query toolkit for Python'
    url = 'https://github.com/mbdevpl/version-query'
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities']
    keywords = [
        'automation', 'continous integration', 'git', 'releasing', 'semantic versioning', 'tagging',
        'versioning']


if __name__ == '__main__':
    Package.setup()
