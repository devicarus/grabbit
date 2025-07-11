from pathlib import Path
from typing import Optional
import importlib
import pkgutil

from grabbit.typing_custom import MediaType


class MediaSource:
    _sources: dict[str, type['MediaSource']] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "domain") and cls.domain:
            MediaSource._sources[cls.domain] = cls

    @classmethod
    def get(cls, domain: str) -> type['MediaSource']:
        return MediaSource._sources.get(domain)

    domain: str

    @staticmethod
    def download(url: str, target: Path) -> (Optional[MediaType], Optional[Path]):
        raise NotImplementedError("This method should be overridden by subclasses")

for _, module_name, is_pkg in pkgutil.iter_modules(__path__):
    if not is_pkg:
        importlib.import_module(f"{__name__}.{module_name}")
