"""Entry point of the command-line interface of version_query package."""

import logging

import boilerplates.logging

from .main import main


class Logging(boilerplates.logging.Logging):
    """Logging configuration."""

    packages = ['version_query']
    level_package = logging.INFO


if __name__ == '__main__':
    Logging.configure()
    main()
