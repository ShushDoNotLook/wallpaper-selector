"""Color generator plugins"""

from pathlib import Path
from .base import ColorGenerator
from .dms import DmsColorGenerator

# Registry of available backends
BACKENDS = {
    "dms": DmsColorGenerator,
}


def get_backend(name: str, **kwargs) -> ColorGenerator | None:
    """Get a backend instance by name with given config"""
    backend_class = BACKENDS.get(name)
    if backend_class:
        return backend_class(**kwargs)
    return None


__all__ = ["ColorGenerator", "DmsColorGenerator", "get_backend"]
