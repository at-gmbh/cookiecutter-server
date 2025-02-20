from importlib.metadata import metadata, version, PackageNotFoundError

try:
    __version__ = version("cookiecutter-server")
    meta = metadata("cookiecutter-server")
    __title__ = meta.get("Name", "cookiecutter-server")  # Fetch title from metadata
    package_summary = meta.get("Summary", "No description available")
    package_author = meta.get("Author", "Unknown")
except PackageNotFoundError:
    __version__ = "unknown"
    __title__ = "cookiecutter-server"
    package_summary = "unknown"
    package_author = "unknown"
