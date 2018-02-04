.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python


========================================
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

.. image:: https://codecov.io/gh/mbdevpl/version-query/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mbdevpl/version-query
    :alt: test coverage from Codecov

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

    from version_query import predict_version_str

    __version__ = predict_version_str()

.. contents::
    :backlinks: none


overview
========

At development time, the current version number is automatically generated based on:

*   tags
*   current commit SHA
*   index status

in your git repository. Therefore the package can be built and shipped to PyPI based only on status
of the git repository. When there is no git repository (this might be the case at installation time
or at runtime) then the script relies on metadata generated at packaging time.

That's why, regardless if package is installed from PyPI (from source or wheel distribution)
or cloned from GitHub, the version query will work.

Additionally, version numbers in version-query are mutable objects and they can be conveniently
incremented, compared with each other, as well as converted to/from other popular
versioning formats.

versioning scheme
=================

Version scheme used by version-query is a relaxed mixture of:

*   `Semantic Versioning 2.0.0 <http://semver.org/>`_ and

*   `PEP 440 -- Version Identification and Dependency Specification <https://www.python.org/dev/peps/pep-0440/>`_.

These two rulesets are mostly compatible. When they are not, a more relaxed approach of the two
is used. Details follow.

Version has one of the following forms:

*   ``<release>``
*   ``<release><pre-release>``
*   ``<release>+<local>``
*   ``<release><pre-release>+<local>``

A release version identifier ``<release>`` has one of the following forms:

*   ``<major>``
*   ``<major>.<minor>``
*   ``<major>.<minor>.<patch>``

And the pre-release version identifier ``<pre-release>`` has one of the following forms:

*   ``<pre-type>``
*   ``<pre-type><pre-patch>``
*   ``<pre-separator><pre-type>``
*   ``<pre-separator><pre-patch>``
*   ``<pre-separator><pre-type><pre-patch>``
*   ... and any of these forms can be repeated arbitrary number of times.

And finally the local version identifier ``<local>`` has one of the forms:

*   ``<local-part>``
*   ``<local-part><local-separator><local-part>``
*   ``<local-part><local-separator><local-part><local-separator><local-part>``
*   ... and so on.

Each version component has a meaning and constraints on its contents:

*   ``<major>`` - a non-negative integer, increments when backwards-incompatible changes are made
*   ``<minor>`` - a non-negative integer, increments when backwards-compatible features are added
*   ``<patch>`` - a non-negative integer, increments when backwards-compatible bugfixes are made

*   ``<pre-separator>`` - dot or dash, separates release version information from pre-release
*   ``<pre-type>`` - a string of lower-case alphabetic characters, type of the pre-release
*   ``<pre-patch>`` - a non-negative integer, revision of the pre-release

*   ``<local-part>`` - a sequence of alphanumeric characters, stores arbitrary information
*   ``<local-separator>`` - a dot or dash, separates parts of local version identifier


how exactly the version number is determined
--------------------------------------------

The version-query package has two modes of operation:

*   *query* - only currently available explicit information is used to determine the version number
*   *prediction* - this applies only to determining version number from git repository, and means
    that in addition to explicit version information, git repository status can be used
    to get very fine-grained version number which will be unique for every repository snapshot


version query from package metadata file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The metadata file (``PKG-INFO`` or ``metadata.json``) is automatically generated whenever a Python
distribution file is built. Which one, depends on your method of building, but in any case,
the file is then packaged into distributions, and when uploaded to PyPI that metadata file is used
to populate the package page - therefore all Python packages on PyPI should have it.

Additionally, source code folder of any package using setuptools, in which ``setup.py <build>``
was executed, contains metadata file -- even if distribution file was not built.

The version identifier is contained verbatim in the metadata file, therefore version query
in this case boils down to simply reading the metadata file.

Information about Python metadata files:

*   `PEP 345 -- Metadata for Python Software Packages 1.2 <https://www.python.org/dev/peps/pep-0345/>`_,
    which replaced `PEP 314 -- Metadata for Python Software Packages v1.1 <https://www.python.org/dev/peps/pep-0314/>`_,
    which in turn replaced `PEP 241 -- Metadata for Python Software Packages <https://www.python.org/dev/peps/pep-0241/>`_;

*   PEP 345 might be at some point in time replaced by
    `PEP 426 -- Metadata for Python Software Packages 2.0 <https://www.python.org/dev/peps/pep-0426/>`_,
    but for now PEP 345 is the current standard.


version query from git repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The version number is equal to the version contained in the most recent version tag.

version tags
````````````

Any git tag that is a valid version (matching the rules above) is considered a version tag.
Version number can be prefixed with ``v`` or ``ver``. Other tags are ignored.

Examples of valid version tags:

*   ``v1.0``
*   ``v0.16.0``
*   ``v1.0.dev3``
*   ``ver0.5.1-4.0.0+a1de3012``
*   ``42.0``
*   ``3.14-15``


most recent version tag
```````````````````````

The most recent tag is found based on repository history and version precedence.

Search for version tags starts from current commit, and goes backwards in history (towards initial
commit). Therefore, commits after current one as well as not-merged branches are ignored in the
version tag search.

If there are several version tags on one commit, then highest version number is used.

If there are version tags on several merged branches, then the highest version number is used.

If there are no version tags in the repository, you'll get an error - so version cannot be queried
from git repository without any version tags.

But in such case, version can still be *predicted*, as described below.


version prediction from git repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In version prediction mode, first of all, a most recent version tag is found, as above.
If there are no version tags in the repo, then the initial commit is assumed to have tag
``v0.1.0.dev0``.

Then, the new commits are counted. Then, the repository index status is queried. All the results
are combined to form the predicted version number. Procedure is described in detail below.


counting new commits
````````````````````

If after the commit with the most recent tag there are any new commits, a suffix ``.dev#``
is appended to the version identifier, where ``#`` is the number of commits between
the current commit and the most recent version tag.

Additionally, the ``<patch>`` version component is incremented by ``1``.

Additionally, a plus (``+``) character and the first 8 characters of SHA of the latest commit
are appended to version identifier, e.g. ``+a3014fe0``.


repository index status
```````````````````````

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


how exactly version numbers are compared
----------------------------------------

The base specification of the comparison scheme is:

*   `PEP 508 -- Dependency specification for Python Software Packages <https://www.python.org/dev/peps/pep-0508/>`_ as well as

*   `Semantic Versioning 2.0.0 <http://semver.org/>`_.

With the notable difference to both that all version components are taken into account when
establishing version precedence.

When being compared, ``<major>``, ``<minor>`` and ``<patch>`` are assumed equal to ``0`` if they
are not present. In ``<pre-release>``, the ``<pre-patch>`` is assumed to be ``0`` if not present.

Examples of comparison results:

*   ``0.3-4.4-2.9`` < ``0.3-4.4-2.10``
*   ``0.3dev`` < ``0.3dev1``
*   ``0.3rc2`` < ``0.3``
*   ``0.3`` < ``0.3-2``
*   ``1.0.0`` < ``1.0.0+blahblah``
*   ``1.0.0+aa`` < ``1.0.0+aaa``
*   ``1.0.0`` = ``1.0.0``
*   ``1`` = ``1.0.0``
*   ``1.0`` = ``1.0.0.0``
*   ``1.0.0-0.0.DEV42`` = ``1.0.0.0.0.dev42``


how exactly version number is incremented
-----------------------------------------

Some version components have assumed value ``0`` if they are not present, please see section above
for details.

Incrementing any version component clears all existing following components.

Examples of how version is incremented:

*   for ``1.5``, incrementing ``<major>`` results in ``2.0``;
*   for ``1.5.1-2.4``, ``<minor>``++ results in ``1.6``;
*   ``1.5.1-2.4``, ``<patch>``++, ``1.5.2``;
*   ``1.5.1``, ``<major>``+=3, ``4.0.0``.


limitations
===========

Either git repository or metadata file must be present for the script to work. When, for example,
zipped version of repository is downloaded from GitHub, the resulting archive contains neither
metadata files nor repository data.

It is unclear what happens if the queried repository is bare.

The implementation is not fully compatible with Python versioning. Especially,
in current implementation at most one of:
alpha ``a`` / beta ``b`` / release candidate ``rc`` / development ``dev`` suffixes
can be used in a version identifier.

And the format in which
alpha ``a``, beta ``b`` and release candidate ``rc`` suffixes
are to be used does not match exactly the conditions defined in PEP 440.

Script might feel a bit slow when attempting to find a version tag in a git repository with a very
large history and no version tags. It is designed towards packages with short release cycles
-- in long release cycles the overhead of manual versioning is small anyway.

Despite above limitations, version-query itself (as well as growing number of other packages) are
using version-query without any issues.


requirements
============

Python version >= 3.4.

Python libraries as specified in `<requirements.txt>`_.

Building and running tests additionally requires packages listed in `<test_requirements.txt>`_.

Tested on Linux, OS X and Windows.
