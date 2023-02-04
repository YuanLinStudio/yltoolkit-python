#!/usr/bin/env python
# coding=utf-8


"""
Helper functions.
"""


import hashlib
from functools import wraps
from typing import Callable, Collection, ParamSpec, TypeVar

from sequoia.settings import TEMP_DIR
from yltoolkit.file_handlers import ensure_directory

P = ParamSpec('P')
R = TypeVar("R")
S = TypeVar("S")


class Singleton(type):
    """
    Credit: https://stackoverflow.com/a/6798042/14640876
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def temp_directory_required(func: Callable[P, R]) -> Callable[P, R]:
    """
    Make sure temp directory is accessible.
    """
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        ensure_directory(TEMP_DIR)
        return func(*args, **kwargs)
    return inner


def only_one_passed(func: Callable[P, Collection[S]]) -> Callable[P, S]:

    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> S:
        result = func(*args, **kwargs)

        if result is None or len(result) <= 0:
            raise LookupError("No item found with this criteria.")
        elif len(result) > 1:
            raise LookupError("More than 1 items found with this criteria.")
        else:
            return result[0]

    return inner


def filtered(attr_name: str, *allowed: list) -> Callable[P, R]:

    def wrapper(func: Callable[P, R]) -> Callable[P, R]:

        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)

            if isinstance(result, dict):
                return {k: v for k, v in result.items()
                        if getattr(v, attr_name) in allowed}

            return [item for item in result
                    if getattr(item, attr_name) in allowed]

        return inner
    return wrapper


def is_not_empty(content: str) -> bool:
    return content is not None and content != ""


def digits_only(content: str) -> str:
    return "".join(char for char in content
                   if char.isdigit())


def get_netstring(content: str) -> bytes:
    """
    Credit: https://pypi.org/project/pynetstring/
    """
    content = f"{content}"
    return bytes(f"{len(content)}:{content},", encoding="utf-8")


def get_hash(content: str | bytes) -> str:
    return hashlib.md5(content).hexdigest()
