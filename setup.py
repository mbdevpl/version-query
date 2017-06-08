"""Build script for version_query package."""

import setuptools

import setup_boilerplate


def setup() -> None:
    """Run setuptools.setup() with correct arguments.

    List of valid project classifiers: https://pypi.python.org/pypi?:action=list_classifiers

    The extras_require is a dictionary which might have the following key-value pairs:
    'some_feature': ['requirement1', 'requirement2'],

    The entry_points is a dictionary which might have the following key-value pair:
    'console_scripts': ['script_name = package.subpackage:function']
    """
    name = 'version-query'
    description = 'Package version query toolkit for Python'
    url = 'https://mbdevpl.github.io/'
    download_url = 'https://github.com/mbdevpl/version-query'
    author = 'Mateusz Bysiek'
    author_email = 'mb@mbdev.pl'
    license_str = 'Apache License 2.0'
    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
        ]
    keywords = ['abstract syntax tree', 'ast', 'parser', 'xml']
    package_data = {}
    exclude_package_data = {}
    extras_require = {}
    entry_points = {}
    test_suite = 'test'

    setuptools.setup(
        name=name, version=setup_boilerplate.find_version(name), description=description,
        long_description=setup_boilerplate.parse_readme(), url=url, download_url=download_url,
        author=author, author_email=author_email,
        maintainer=author, maintainer_email=author_email,
        license=license_str, classifiers=classifiers, keywords=keywords,
        packages=setup_boilerplate.find_packages(), package_dir={'': setup_boilerplate.SRC_DIR},
        include_package_data=True, package_data=package_data,
        exclude_package_data=exclude_package_data,
        install_requires=setup_boilerplate.parse_requirements(), extras_require=extras_require,
        python_requires=setup_boilerplate.find_required_python_version(classifiers),
        entry_points=entry_points, test_suite=test_suite)


if __name__ == '__main__':
    setup_boilerplate.SRC_DIR = '.'
    setup_boilerplate.setup = setup
    setup_boilerplate.main()
