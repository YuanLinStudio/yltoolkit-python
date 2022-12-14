#!/usr/bin/env python
# coding=utf-8


"""
Enumeration extension.
"""


from enum import Enum
from typing import Self


class YLEnum(Enum):
    """
    The value of the enum will be the lowercased and JSON-parsable string of the member's name.
    If collaborate with JSON, The enum should be in the same layer with the JSON files. All underscores (`_`) will be replaced by dashes (`-`). No dots will be accessible.
    Example: `YLEnum.DEFAULT_VERSION.value = default-version`
    """

    def __repr__(self):
        # cls_name = self.__class__.__name__
        # return f"{cls_name}.{self.name}"
        return self.name

    def as_encodable(self) -> str:
        return self.value

    def _generate_next_value_(name, start, count, last_values):
        if isinstance(name, str):
            return name.lower().replace("_", "-")
        else:
            return name

    @classmethod
    @property
    def all_members(cls) -> list[Self]:
        return [member for member in cls]

    @classmethod
    @property
    def all_values(cls) -> list[str]:
        return [member.value for member in cls]

    @classmethod
    def ensure(cls, obj: str | Self, case_sensitive: bool = False) -> Self:
        if not isinstance(obj, cls):

            if isinstance(obj, str) and not case_sensitive:
                obj = obj.lower()

            try:
                obj = cls(obj)
            except Exception as e:
                """
                import sources.DelMar.public.logging.LogSetup as LogSetup
                logger = LogSetup.initLogger(__name__)
                logger.exception(
                    f"Cannot enumeration-ize {obj} as {cls}.", e)
                """
                raise e

        return obj
