__version__ = "0.1.0"
benchpark_version = __version__


def __try_int(v):
    try:
        return int(v)
    except ValueError:
        return v


benchpark_version_info = tuple([__try_int(v) for v in __version__.split(".")])


__all__ = ["benchpark_version_info", "benchpark_version"]
