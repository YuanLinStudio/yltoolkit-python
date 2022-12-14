#!/usr/bin/env python
# coding=utf-8


"""
Datetime object.
"""


if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname, join

    sys.path.insert(0, abspath(join(dirname(__file__), "../..")))


import datetime
from typing import Self

from dateutil import parser

from yltoolkit.YLDatetime.TimeStandard import TimeStandard

READABLE_FORMAT = "{:%Y-%m-%d %a %H:%M:%S}"
EXCEL_FORMAT = "{:%Y-%m-%d %H:%M:%S}"


class YLDatetime(datetime.datetime):

    def replace_timestandard(self, standard: TimeStandard) -> Self:
        return self.replace(tzinfo=standard.tzinfo)

    def convert_timestandard(self, standard: TimeStandard) -> Self:
        return self.astimezone(tz=standard.tzinfo)

    def to_utc(self) -> Self:
        return self.convert_timestandard(standard=TimeStandard.UTC)

    def as_iso(self, standard: TimeStandard = None) -> str:
        if standard is not None:
            self = self.convert_timestandard(standard=standard)
        return self.isoformat(timespec="seconds")

    def as_readable(self, standard: TimeStandard = None) -> str:
        if standard is not None:
            self = self.convert_timestandard(standard=standard)
        return READABLE_FORMAT.format(self)

    def as_excel(self, standard: TimeStandard = None) -> str:
        if standard is not None:
            self = self.convert_timestandard(standard=standard)
        return EXCEL_FORMAT.format(self)

    def strftime(self, __format: str) -> str:
        return super().strftime(__format)

    @classmethod
    def init_from_datetime(cls, dt: datetime.datetime) -> Self:
        return YLDatetime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            tzinfo=dt.tzinfo,
            fold=dt.fold,
        )

    @classmethod
    def now(cls: type[Self], standard: TimeStandard = TimeStandard.UTC) -> Self:
        standard = TimeStandard.ensure(standard)
        return super().now(tz=standard.tzinfo)

    @classmethod
    def strptime(cls, __date_string: str, __format: str) -> Self:
        dt = super().strptime(__date_string, __format)
        return cls.init_from_datetime(dt)

    @classmethod
    def parse(cls, timestr: str, standard: TimeStandard = None) -> Self:
        """
        param standard: TimeStandard

        If a time zone info is parsable in timestr, the result will be *CONVERTED* to `standard` when `standard` is not None.
        If timestr doesn't include a time zone info, the result will be *FORCED / REPLACED* to `standard` when `standard` is not None.
        """

        dt = parser.parse(timestr)
        yl_dt = cls.init_from_datetime(dt)

        if standard is not None:

            if yl_dt.tzinfo is not None:
                yl_dt = yl_dt.convert_timestandard(standard)
            else:
                yl_dt = yl_dt.replace_timestandard(standard)

        return yl_dt

    @classmethod
    def load_date(cls, *, from_json: dict) -> datetime.date:
        """
        在 `visualizing.json` 查看示例
        """

        if "exactly" in from_json:
            source = from_json["exactly"]

            if source == "today":
                return cls.now().date()

            else:
                date_components = source["date"]
                try:
                    return datetime.date(**date_components)
                except:
                    raise ValueError(
                        f"Invalid date components: {date_components}.")

        elif "relevant" in from_json:
            source = from_json["relevant"]

            relevant_from = cls.load_date(from_json=source["from"])
            method: str = source["method"]
            method = method.lower()

            try:
                delta_components = source["timedelta"]
                delta = datetime.timedelta(**delta_components)
            except:
                raise ValueError(
                    f"Invalid date components: {delta_components}.")

            if method == "minus":
                return relevant_from - delta
            elif method == "add":
                return relevant_from + delta
            else:
                raise NotImplementedError()

        elif "replacing" in from_json:
            source = from_json["replacing"]

            replacing_from = cls.load_date(from_json=source["from"])

            try:
                replace_components = source["replace"]
                return replacing_from.replace(**replace_components)
            except:
                raise ValueError(
                    f"Cannot replace date object with: {replace_components}.")


if __name__ == "__main__":
    dt = YLDatetime.now(standard=TimeStandard.LOCAL)
    str_rep = dt.as_excel(standard=TimeStandard.CST)
    ndt = YLDatetime.parse(str_rep, standard=TimeStandard.CST)
    print(dt.to_utc(), ndt.to_utc())
    print(dt.as_excel(), ndt.as_excel())
