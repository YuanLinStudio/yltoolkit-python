#!/usr/bin/env python
# coding=utf-8


"""
Date and time helpers for `datetime.datetime`.
"""

import datetime

from .TimeStandard import TimeStandard
from .YLDatetime import YLDatetime


def replace_timestandard(datetime: datetime.datetime, standard: TimeStandard) -> datetime.datetime:
    return YLDatetime.init_from_datetime(datetime).replace_timestandard(standard=standard)


def convert_timestandard(datetime: datetime.datetime, standard: TimeStandard) -> datetime.datetime:
    return YLDatetime.init_from_datetime(datetime).astimezone(tz=standard.tzinfo)


def convert_to_utc(datetime: datetime.datetime) -> datetime.datetime:
    return YLDatetime.init_from_datetime(datetime).to_utc()


def format_as_iso(datetime: datetime.datetime, standard: TimeStandard = None) -> str:
    return YLDatetime.init_from_datetime(datetime).as_iso(standard=standard)


def format_as_readable(datetime: datetime.datetime, standard: TimeStandard = None) -> str:
    return YLDatetime.init_from_datetime(datetime).as_readable(standard=standard)


def format_as_excel(datetime: datetime.datetime, standard: TimeStandard = None) -> str:
    return YLDatetime.init_from_datetime(datetime).as_excel(standard=standard)
