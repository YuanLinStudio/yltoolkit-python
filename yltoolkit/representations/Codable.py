#!/usr/bin/env python
# coding=utf-8


"""
Codable object.
"""

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname, join

    sys.path.insert(0, abspath(join(dirname(__file__), "../..")))


from abc import ABC
from dataclasses import InitVar, asdict, dataclass, field, fields
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypeVar

from yltoolkit.YLDatetime import TimeStandard, YLDatetime
from yltoolkit.YLDatetime.tools import format_as_excel
from yltoolkit.YLEnum import YLEnum

ID = TypeVar("ID", str, int)


@dataclass
class Codable(ABC):
    """
    Codable object.
    """

    id: ID = field(default=None, kw_only=True, repr=False)

    from_dict: InitVar[dict[str, str]] = None

    def __post_init__(self, from_dict: InitVar[dict[str, str]]):

        if from_dict is not None:

            for key, value in from_dict.items():

                key = key.lower().replace("-", "_")

                if isinstance(value, list | tuple | set):
                    value = [v for v in value if v != ""]
                else:
                    value = value if value != "" else None

                if isinstance(value, str) and value.lower() in ["true", "false"]:
                    if value.lower() == "true":
                        value = True
                    else:
                        value = False

                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    logger.warning(f"{key}: {value} not in implemented class.")

    @classmethod
    @property
    def fieldnames(cls) -> list[str]:
        return [field.name.lower().replace("_", "-")
                for field in fields(cls)]

    def to_dict(self) -> dict[str, str]:
        result = {key.lower().replace("_", "-"): value
                  for key, value in asdict(self).items()}

        # standardizer
        for key, value in result.items():

            if isinstance(value, YLDatetime):
                if value.tzinfo is not None:
                    result[key] = value.as_excel(standard=TimeStandard.CST)
                else:
                    result[key] = value.as_excel()

            elif isinstance(value, datetime):
                if value.tzinfo is not None:
                    result[key] = format_as_excel(
                        datetime=value, standard=TimeStandard.CST)
                else:
                    result[key] = format_as_excel(datetime=value)

            elif isinstance(value, timedelta):
                result[key] = round(value.total_seconds())

            elif isinstance(value, YLEnum):
                result[key] = value.as_encodable()

            elif isinstance(value, bool):
                result[key] = str(value).upper()

            elif isinstance(value, Path):
                result[key] = str(value)

        return result

    @staticmethod
    def ensure_datetime(obj: str | YLDatetime) -> YLDatetime:
        return YLDatetime.ensure(obj).replace_timestandard(standard=TimeStandard.CST)
