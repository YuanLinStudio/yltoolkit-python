#!/usr/bin/env python
# coding=utf-8


"""
Time Standard.
"""


if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname, join

    sys.path.insert(0, abspath(join(dirname(__file__), "../..")))


import datetime
from zoneinfo import ZoneInfo

from YLEnum import YLEnum, auto


class TimeStandard(YLEnum):

    UTC = auto()
    CST = auto()
    LOCAL = auto()

    @property
    def tzinfo(self):
        return tzinfos[self]


local_tzinfo = datetime.datetime.now().astimezone().tzinfo


tzinfos: dict[TimeStandard, datetime.tzinfo] = {
    TimeStandard.UTC: datetime.timezone.utc,
    TimeStandard.CST: ZoneInfo("Asia/Shanghai"),
    TimeStandard.LOCAL: local_tzinfo
}
