#!/usr/bin/env python
# coding=utf-8


"""
Hashable object set.
"""

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname, join

    sys.path.insert(0, abspath(join(dirname(__file__), "../..")))


from abc import ABC
from typing import Generic, Self, TypeVar

from yltoolkit.representations import ID, HashableMixin

H = TypeVar("H", bound=HashableMixin)


class HashableSetMixin(ABC, Generic[H]):
    """
    Hashable object set.
    """

    _hashes: set[str]
    _object_dict: dict[ID, H]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def decode(self, *args, **kwargs):
        super().decode(*args, **kwargs)
        self.refresh_hashes()

    @property
    def all(self) -> dict[ID, H]:
        return super().all

    @property
    def hashes(self) -> set[str]:
        return self._hashes

    def update(self, item: H):
        self._hashes.add(item.hash)
        super().update(item)

    def refresh_hashes(self):
        self._hashes = {item.hash for item in self.all.values()}
