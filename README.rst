.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python


Package version query toolkit for Python
========================================

.. image:: https://img.shields.io/pypi/v/version-query.svg
    :target: https://pypi.python.org/pypi/version-query
    :alt: package version from PyPI

.. image:: https://travis-ci.org/mbdevpl/version-query.svg?branch=master
    :target: https://travis-ci.org/mbdevpl/version-query
    :alt: build status from Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/mbdevpl/version-query?branch=master&svg=true
    :target: https://ci.appveyor.com/project/mbdevpl/version-query
    :alt: build status from AppVeyor

.. image:: https://api.codacy.com/project/badge/Grade/437ab82bd6324530847fe8ed833f8d78
    :target: https://www.codacy.com/app/mbdevpl/version-query
    :alt: grade from Codacy

.. image:: https://coveralls.io/repos/github/mbdevpl/version-query/badge.svg?branch=master
    :target: https://coveralls.io/github/mbdevpl/version-query
    :alt: test coverage from Coveralls

.. image:: https://img.shields.io/pypi/l/version-query.svg
    :target: https://github.com/mbdevpl/version-query/blob/master/NOTICE
    :alt: license

This script is motivated by wish to avoid hardcoding the version number when maintaining
a Python package.

Instead of hardcoding:

.. code:: python

    __version__ = '1.5.0.dev2'

You can instead:

.. code:: python

    from version_query import generate_version_str

    __version__ = generate_version_str()


how does it work
----------------

At development time, this will automatically infer the current version number based on:

*   tags
*   current commit SHA
*   index status

in your git repository. Therefore the package can be built and shipped to PyPI based only on status
of the git repository.

If there is no git repository (this might be the case at installation time or at runtime)
the script relies on package metadata from its ``PKG-INFO`` file.

``PKG-INFO`` is a file that is automatically-generated when building a package and it is packaged
into source as well as binary distributions. It should be present for every Python 3 package.


how version is determined from git repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First of all, a most recent (based on commit tree) version tag is found. Version tag is a git tag
that starts with ``v`` or ``ver``, followed by a valid version identifier.

Examples of valid version tags:

*   ``v1.0``
*   ``v0.16.0``
*   ``v1.0.dev3``

The validity of the version identifier is determined by PEP 440.

If there are no version tags in the repo, the script simply assumes that initial commit
has tag ``v0.0.0``, and proceeds.


how version is incremented for a git repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If current commit is not the one with the latest version tag, a suffix ``.dev#`` is appended
to the version identifier, where ``#`` is the distance (number of commits) between
the current commit and the latest version tag.

Additionally, the release number is incremented by 1. Release number here is defined
as in ``major.minor.release``, e.g. for version ``1.2.3`` release number is ``3`` and it would be
assumed equal to ``0`` if not present.

Additionally, a plus (``+``) character and the first 8 characters of SHA of the latest commit
are appended to version identifier, e.g. ``+a3014fe0``.

Additionally, if there are any uncommitted changes in the repository (i.e. the repo is *dirty*),
the suffix ``.dirty`` followed by current date and time in format ``YYYYMMDDhhmmss`` are appended
to the identifier.

Example of how the final version identifier looks like, depending on various conditions
of the repository:

*   Most recent version tag is ``v0.4.5``, there were 2 commits since,
    latest having SHA starting with ``812f12ea``.
    Version identifier will be ``0.4.6.dev2+812f12ea``.

*   Most recent version tag is ``ver6.0``, and there was 1 commit since
    having SHA starting with ``e10ac365``.
    Version identifier will be ``6.0.1.dev1+e10ac365``.

*   Most recent version tag is ``v9``, there were 40 commit since,
    latest having SHA starting with ``1ad22355``, the repository has uncommitted changes and
    version was queried at 19:52.20, 8th June 2017.
    the result is ``9.0.1.dev40+1ad22355.dirty20170608195220``.


how version is determined from ``PKG-INFO`` file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The version identifier is simply read from the package metadata file
(i.e. the file named ``PKG-INFO``) which should be present for any:

*   installed package
*   source distribution
*   binary distribution
*   source code folder of any package using setuptools, in which ``setup.py <build>`` was executed


limitations
-----------

Either git repository or ``PKG-INFO`` file must be present for the script to work.

The current implementation aims at, but is not yet fully compatible with:

*   `PEP 440 -- Version Identification and Dependency Specification <https://www.python.org/dev/peps/pep-0440/>`_;

*   `PEP 508 -- Dependency specification for Python Software Packages <https://www.python.org/dev/peps/pep-0508/>`_;

*   `PEP 345 -- Metadata for Python Software Packages 1.2 <https://www.python.org/dev/peps/pep-0345/>`_,
    which replaced `PEP 314 -- Metadata for Python Software Packages v1.1 <https://www.python.org/dev/peps/pep-0314/>`_,
    which in turn replaced `PEP 241 -- Metadata for Python Software Packages <https://www.python.org/dev/peps/pep-0241/>`_;

*   PEP 345 might be at some point in time replaced by
    `PEP 426 -- Metadata for Python Software Packages 2.0 <https://www.python.org/dev/peps/pep-0426/>`_,
    but for now PEP 345 is the current standard.

Especially, in current implementation at most one of:
alpha ``a`` / beta ``b`` / release candidate ``rc`` / development ``dev`` suffixes
can be used in a version identifier.

And the format in which
alpha ``a``, beta ``b`` and release candidate ``rc`` suffixes
are to be used does not match exactly the conditions defined in PEP.


requirements
------------

Python version >= 3.3.

Python libraries as specified in `<requirements.txt>`_.

Building and running tests additionally requires packages listed in `<dev_requirements.txt>`_.

Tested on Linux, OS X and Windows.
