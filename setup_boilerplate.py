"""Below code is generic boilerplate and normally should not be changed.

See the implementation of setup_boilerplate.Package for available options.
Also, some fields have default values. See DEFAULT_* constants below for those values.

To avoid setup script boilerplate, create "setup.py" file with the minimal contents as given
below and modify it according to the specifics of your package.
Note: string limiters need to be adjusted.

"" "Setup script." ""

import setup_boilerplate


class Package(setup_boilerplate.Package):
    "" "Package metadata." ""

    name = ''
    description = ''
    url = 'https://github.com/mbdevpl/...'
    classifiers = [
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only']
    keywords = []


if __name__ == '__main__':
    Package.setup()
"""

import logging
import pathlib
import runpy
import sys
import typing as t

import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import setuptools

__version__ = '2023.03.09'

_LOG = logging.getLogger(__name__)

HERE = pathlib.Path(__file__).resolve().parent

DEFAULT_URL = 'https://github.com/mbdevpl'
DEFAULT_AUTHOR = 'Mateusz Bysiek'
DEFAULT_AUTHOR_EMAIL = 'mateusz.bysiek@gmail.com'
DEFAULT_LICENSE_STR = 'Apache License 2.0'


def find_version(
        package_name: str, version_module_name: str = '_version',
        version_variable_name: str = 'VERSION') -> str:
    """Simulate behaviour of "from package_name._version import VERSION", and return VERSION.

    To avoid importing whole package only to read the version, just module containing the version
    is imported. Therefore relative imports in that module will break the setup.

    :param package_name: name of the package
    :param version_module_name: name of the module containing the version
    :param version_variable_name: name of the variable containing the version
    :return: version string
    """
    version_module_path = f'{package_name.replace("-", "_")}/{version_module_name}.py'
    version_module_vars = runpy.run_path(version_module_path)
    return version_module_vars[version_variable_name]


def find_packages(root_directory: str = '.') -> t.List[str]:
    """Find packages to pack.

    :param root_directory: directory to start searching from
    :return: list of packages
    """
    exclude = ['test', 'test.*'] if ('bdist_wheel' in sys.argv or 'bdist' in sys.argv) else []
    packages_list = setuptools.find_packages(root_directory, exclude=exclude)
    return packages_list


def parse_requirements(
        requirements_path: str = 'requirements.txt') -> t.List[str]:
    """Read contents of requirements.txt file and return data from its relevant lines.

    Only non-empty and non-comment lines are relevant.

    :param requirements_path: path to the requirements file if custom one is used
    :return: list of requirements
    """
    requirements = []
    with HERE.joinpath(requirements_path).open(encoding='utf-8') as requirements_file:
        for requirement in [line.strip() for line in requirements_file.read().splitlines()]:
            if not requirement or requirement.startswith('#'):
                continue
            requirements.append(requirement)
    return requirements


def partition_version_classifiers(
        classifiers: t.Sequence[str], version_prefix: str = 'Programming Language :: Python :: ',
        only_suffix: str = ' :: Only'
        ) -> t.Tuple[t.List[t.Tuple[int, ...]], t.List[t.Tuple[int, ...]]]:
    """Find version number classifiers in given list and partition them into 2 groups.

    The 2 groups being:
    1. minimum versions, any version at least as high this is compatible
    2. only versions, this specific version is compatible, but nothing is said about other versions

    :param classifiers: sequence of trove classifiers to be analysed
    :param version_prefix: prefix that identifies a version classifier
    :param only_suffix: prefix that identifies an "only version" classifier
    :return: parsed and partitioned version tuples
    """
    versions_min: t.List[t.Tuple[int, ...]] = []
    versions_only: t.List[t.Tuple[int, ...]] = []
    for classifier in classifiers:
        version = classifier.replace(version_prefix, '')
        versions = versions_min
        if version.endswith(only_suffix):
            version = version.replace(only_suffix, '')
            versions = versions_only
        try:
            versions.append(tuple(int(_) for _ in version.split('.')))
        except ValueError:
            pass
    return versions_min, versions_only


def find_required_python_version(
        classifiers: t.Sequence[str], version_prefix: str = 'Programming Language :: Python :: ',
        only_suffix: str = ' :: Only') -> t.Optional[str]:
    """Determine the minimum required Python version.

    :param classifiers: sequence of trove classifiers to be analysed
    :param version_prefix: prefix that identifies a version classifier
    :param only_suffix: prefix that identifies an "only version" classifier
    :return: minimum required Python version string, if any
    """
    versions_min, versions_only = partition_version_classifiers(
        classifiers, version_prefix, only_suffix)
    if len(versions_only) > 1:
        raise ValueError(f'more than one "{only_suffix}" version encountered in {versions_only}')
    only_version = None
    if len(versions_only) == 1:
        only_version = versions_only[0]
        for version in versions_min:
            if version[:len(only_version)] != only_version:
                raise ValueError(f'the "{only_suffix}" version {only_version}'
                                 f' is inconsistent with version {version}')
    min_supported_version = None
    for version in versions_min:
        if min_supported_version is None or \
                (len(version) >= len(min_supported_version) and version < min_supported_version):
            min_supported_version = version
    if min_supported_version is None:
        if only_version is not None:
            return '.'.join([str(_) for _ in only_version])
    else:
        return '>=' + '.'.join([str(_) for _ in min_supported_version])
    return None


def parse_rst(text: str) -> docutils.nodes.document:
    """Parse text assuming it's an RST markup."""
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(components=components).get_default_values()
    document = docutils.utils.new_document('<rst-doc>', settings=settings)
    parser.parse(text, document)
    return document


class RelativeRefFinder(docutils.nodes.NodeVisitor):
    """Find all relative references in a given docutils document that point to existing files."""

    def __init__(self, root_dir: pathlib.Path, *args, **kwargs):
        """Initialize the RelativeRefFinder object."""
        super().__init__(*args, **kwargs)
        self.root_dir = root_dir
        self.references: t.List[docutils.nodes.reference] = []

    def visit_reference(self, node: docutils.nodes.reference) -> None:
        """Call for "reference" nodes."""
        assert isinstance(node, docutils.nodes.TextElement), type(node)
        _LOG.debug('RelativeRefFinder: examining reference %s', node)
        if len(node.children) != 1 or 'refuri' not in node.attributes \
                or node.attributes['refuri'].startswith(('http://', 'https://')):
            return
        # _LOG.debug('  RelativeRefFinder: reference passed initial check')
        path = pathlib.Path(node.attributes['refuri'])
        if path.is_absolute():
            return
        if '#' in path.name:
            # reference points to a section in a file
            # we ignore the section part when checking if file exists
            path = path.with_name(path.name[:path.name.index('#')])
        try:
            self.root_dir.joinpath(path).resolve(strict=True)
        except FileNotFoundError:
            return
        _LOG.debug('RelativeRefFinder: reference points to existing file')
        self.references.append(node)

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Call for unknown node types."""
        return


def resolve_relative_rst_links(text: str, base_link: str) -> str:
    """Resolve all relative links in a given string representing an RST document.

    Links are resolved only if they point to files existing in the project's working directory.

    All links of form `link`_ become `link <absolute_link>`_.

    And all link of the form :target: link become :target: absolute_link.

    Where absolute_link is made by concatenating base_link to link with no separator added
    in between. So in most cases base_link should end with a slash.
    """
    document = parse_rst(text)
    finder = RelativeRefFinder(HERE, document)
    document.walk(finder)
    for target in finder.references:
        _LOG.info('resolve_relative_rst_links: resolving reference %s', target)
        assert isinstance(target, docutils.nodes.TextElement), type(target)
        refuri = target.attributes['refuri']
        if 'name' in target.attributes:
            name = target.attributes['name']
            if name == refuri:
                old_link = f'`<{refuri}>`_'
            else:
                old_link = f'`{name} <{refuri}>`_'
            new_link = f'`{name} <{base_link}{refuri}>`_'
        else:
            old_link = f' :target: {refuri}'
            new_link = f' :target: {base_link}{refuri}'
        text = text.replace(old_link, new_link)
        _LOG.info('resolve_relative_rst_links: replaced "%s" with "%s"', old_link, new_link)
    return text


class Package:
    """Default metadata and behaviour for a Python package setup script."""

    root_directory: str = '.'
    """Root directory of the source code of the package, relative to the setup.py file location."""

    name: str
    """Package name."""

    version: str
    """Package version as string.

    If None, it will be obtained from "package_name._version.VERSION" variable.
    """

    description: str
    """One line of text that shortly describes the package."""

    long_description: str
    """Full description of the package, can be arbitrarily long.

    If not set, it will be generated from readme.
    """

    long_description_content_type: str
    """Content type of the long description.

    Usually one of 'text/x-rst', 'text/markdown' or 'text/plain'.

    If not set, it will be set according to readme file extension.
    For this field to be automatically set, also long_description field cannot be set.
    """

    url: str = DEFAULT_URL
    download_url: str = ''
    author: str = DEFAULT_AUTHOR
    author_email: str = DEFAULT_AUTHOR_EMAIL
    maintainer: str
    maintainer_email: str
    license_str: str = DEFAULT_LICENSE_STR

    classifiers: t.List[str] = []
    """List of trove classifiers for the package.

    List of valid classifiers: https://pypi.org/pypi?:action=list_classifiers
    """

    keywords: t.List[str] = []

    packages: t.List[str]
    """List of Python packages to be included in the distributed file.

    Usually it's just one package per distributed file, but any number is supported.

    If not set, determined with help of setuptools.
    """

    package_data: t.Dict[str, t.List[str]] = {}
    exclude_package_data: t.Dict[str, t.List[str]] = {}

    install_requires: t.Optional[t.List[str]] = None
    """If None, determined using requirements.txt."""

    extras_require: t.Mapping[str, t.List[str]] = {}
    """A dictionary containing entries of type 'some_feature': ['requirement1', 'requirement2']."""

    python_requires: t.Optional[str] = None
    """If None, determined from provided classifiers."""

    entry_points: t.Mapping[str, t.List[str]] = {}
    """A dictionary used to enable automatic creation of console scripts, gui scripts and plugins.

    Example entry:
    'console_scripts': ['script_name = package.subpackage:function']
    """

    test_suite: str = 'test'

    @classmethod
    def try_fields(cls, *names) -> t.Optional[t.Any]:
        """Return first existing of given class field names."""
        for name in names:
            if hasattr(cls, name):
                return getattr(cls, name)
        raise AttributeError((cls, names))

    @classmethod
    def parse_readme(cls, readme_filename: str = 'README.rst',
                     encoding: str = 'utf-8') -> t.Tuple[str, str]:
        """Parse readme and resolve relative links in it if it is feasible.

        Links are resolved if readme is in rst format and the package is hosted on GitHub.
        """
        readme_path = HERE.joinpath(readme_filename)
        with readme_path.open(encoding=encoding) as readme_file:
            long_description: str = readme_file.read()

        if readme_path.suffix.lower() == '.rst' and cls.url.startswith('https://github.com/'):
            base_url = f'{cls.url}/blob/v{cls.version}/'
            long_description = resolve_relative_rst_links(long_description, base_url)

        long_description_content_type = {'.rst': 'text/x-rst', '.md': 'text/markdown'}.get(
            readme_path.suffix.lower(), 'text/plain')
        long_description_content_type += '; charset=UTF-8'

        return long_description, long_description_content_type

    @classmethod
    def prepare(cls) -> None:
        """Fill in possibly missing package metadata."""
        if not hasattr(cls, 'version'):
            cls.version = find_version(cls.name)
        if not hasattr(cls, 'long_description'):
            cls.long_description, cls.long_description_content_type = cls.parse_readme()
        if not hasattr(cls, 'maintainer'):
            cls.maintainer = cls.author
        if not hasattr(cls, 'maintainer_email'):
            cls.maintainer_email = cls.author_email
        if not hasattr(cls, 'packages'):
            cls.packages = find_packages(cls.root_directory)
        if cls.install_requires is None:
            cls.install_requires = parse_requirements()
        if cls.python_requires is None:
            cls.python_requires = find_required_python_version(cls.classifiers)

    @classmethod
    def setup(cls) -> None:
        """Call setuptools.setup with correct arguments."""
        cls.prepare()
        setuptools.setup(
            name=cls.name, version=cls.version, description=cls.description,
            long_description=cls.long_description,
            long_description_content_type=cls.long_description_content_type,
            url=cls.url, download_url=cls.download_url,
            author=cls.author, author_email=cls.author_email,
            maintainer=cls.maintainer,
            maintainer_email=cls.maintainer_email,
            license=cls.license_str, classifiers=cls.classifiers, keywords=cls.keywords,
            packages=cls.packages, package_dir={'': cls.root_directory},
            include_package_data=True,
            package_data=cls.package_data, exclude_package_data=cls.exclude_package_data,
            install_requires=cls.install_requires, extras_require=cls.extras_require,
            python_requires=cls.python_requires,
            entry_points=cls.entry_points, test_suite=cls.test_suite)
