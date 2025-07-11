from importlib.metadata import PackageNotFoundError, version


def get_version() -> str:
    """ Returns the current version. """
    try:
        return version("grabbit")
    except PackageNotFoundError:
        return "unknown"
