""" This module contains the main entry point for the Grabbit CLI. """

from grabbit.cli import cli

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    # Pylint doesn't know the click library supplies the parameters in a decorator.
    cli()
