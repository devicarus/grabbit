import json
import atexit
from collections import defaultdict
from pathlib import Path
from typing import Any

from .paths import get_data_path


class BranchCounter:
    def __init__(self, path: Path):
        self._counts = defaultdict(int)
        self._path = path

        self.load()  # Load counts if they exist
        atexit.register(self.save)  # Auto-save on shutdown

    def increment(self, *path: str):
        """
        Increment a count at a hierarchical path.
        E.g. increment("sources", "a")
        """
        key = tuple(path)
        self._counts[key] += 1

    def record(self, *path: str):
        """
        Decorator version. E.g. @counter.record("sources", "a")
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                self.increment(*path)
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def all_counts(self) -> dict[str, Any]:
        """
        Return counts as a nested tree, e.g.:
        {
            "sources": {
                "a": 2,
                "b": 3
            },
            "type": {
                "x": 1
            }
        }
        """
        tree = {}
        for key_tuple, count in self._counts.items():
            node = tree
            for part in key_tuple[:-1]:
                node = node.setdefault(part, {})
            node[key_tuple[-1]] = count
        return tree

    def save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self.all_counts(), f, indent=4)

    def load(self):
        if self._path.exists():
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._counts.clear()
                self._counts.update(self._flatten_tree(data))

    def _flatten_tree(self, node, prefix=()):
        """
        Helper to flatten nested dicts back to (tuple keys -> count).
        """
        flat = {}
        for k, v in node.items():
            if isinstance(v, dict):
                flat.update(self._flatten_tree(v, prefix + (k,)))
            else:
                flat[prefix + (k,)] = v
        return flat

    def __str__(self):
        return json.dumps(self.all_counts(), indent=4)


branch_counter = BranchCounter(get_data_path("grabbit", "branch_counter.json"))
