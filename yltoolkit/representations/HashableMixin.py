#!/usr/bin/env python
# coding=utf-8


"""
Hashable object.
"""

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname, join

    sys.path.insert(0, abspath(join(dirname(__file__), "../..")))


from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class HashableMixin(ABC):
    """
    Hashable object.
    """

    hash: str = field(default=None, kw_only=True, repr=False)

    def __post_init__(self, from_dict: dict[str, str] = None):
        super().__post_init__(from_dict)

        if self.hash is None:
            self.hash = self.hash_generator()

    @abstractmethod
    def hash_generator(self) -> str:
        pass
