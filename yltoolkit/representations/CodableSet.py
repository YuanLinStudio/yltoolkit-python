#!/usr/bin/env python
# coding=utf-8


"""
Codable object set.
"""

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname, join

    sys.path.insert(0, abspath(join(dirname(__file__), "../..")))


import json
import re
from abc import ABC
from collections import Counter
from pathlib import Path
from typing import Generic, Self, Type, TypeVar

import flatten_dict

from yltoolkit.file_handlers import read_csv, write_csv
from yltoolkit.helpers import only_one_passed
from yltoolkit.logger import logger

from .Codable import ID, Codable

C = TypeVar("C", bound=Codable)


class CodableSet(ABC, Generic[C]):
    """
    Codable object set.
    """

    SUPPORTED_EXTENSION = ["csv", "json"]

    datasource: Path

    _object_type: Type[C]
    _object_dict: dict[ID, C]
    _id_sn: int

    def __init__(self, object_type: Type[C] = None) -> None:
        super().__init__()

        if object_type is not None:
            self._object_type = object_type

        self._object_dict = dict[ID, C]()

    @property
    def all(self) -> dict[ID, C]:
        return self._object_dict

    @property
    def next_id(self) -> str:
        if self._id_sn == -1:
            logger.warning(
                f"ID of {self.__class__} could not support id auto-increasing.")
            return "-1"
        else:
            self._id_sn += 1
            return f"{self._id_sn}"

    def update(self, item: C):
        self._object_dict[item.id] = item

    @only_one_passed
    def get_item_by_id(self, id: ID) -> list[C]:

        result = [item for item in self._object_dict.values()
                  if item.id == id or item.id == f"{id}"]
        return result

    def decode(self, filepath: Path, *args, **kwargs):

        self.datasource = filepath
        ext = filepath.suffix.lower().replace(".", "")

        match ext:
            case "csv":
                self.CSVCoding.decode(self, filepath, *args, **kwargs)
            case "json":
                self.JSONCoding.decode(self, filepath, *args, **kwargs)
            case _:
                raise NotImplementedError

        # set ID serialize number
        if len(self._object_dict) == 0:
            self._id_sn = 0
        else:
            try:
                self._id_sn = max(
                    [int(k) for k in self._object_dict.keys() if f"{k}".isdigit()])
            except:
                self._id_sn = -1

        logger.success(
            f"Finish decoding {self.__class__} from {filepath} with items count {len(self._object_dict)}.")

    def encode(self, filepath: Path = None, *args, **kwargs):

        if filepath is None:
            filepath = self.datasource

        ext = filepath.suffix.lower().replace(".", "")

        match ext:
            case "csv":
                self.CSVCoding.encode(self, filepath, *args, **kwargs)
            case "json":
                self.JSONCoding.encode(self, filepath, *args, **kwargs)
            case _:
                raise NotImplementedError

        logger.success(
            f"Finish encoding {self.__class__} into {filepath} with items count {len(self._object_dict)}.")

    @classmethod
    def init_from_serialized(cls, filepath: Path, object_type: Type[C] = None) -> Self:

        result = cls(object_type=object_type)
        result.decode(filepath=filepath)

        return result

    class CSVCoding:

        @classmethod
        def decode(cls, codable_set: "CodableSet[C]", filepath: Path, *args, **kwargs):

            use_flatten: bool = kwargs.get("use_flatten", True)

            def mapping_handler(mapping: dict[str, str]) -> None:
                if use_flatten:
                    mapping = cls.unflatten(mapping)

                object: Codable = codable_set._object_type(
                    from_dict=mapping)
                codable_set._object_dict[object.id] = object

            read_csv(filepath=filepath,
                     mapping_handler=mapping_handler)

            return codable_set

        @classmethod
        def encode(cls, codable_set: "CodableSet[C]", filepath: Path, *args, use_flatten: bool = True, **kwargs):

            fieldnames = codable_set._object_type.fieldnames

            if use_flatten:
                items = {k: cls.flatten(v.to_dict())
                         for k, v in codable_set._object_dict.items()}
                fieldnames = cls.update_fieldnames_if_flattened(
                    fieldnames=fieldnames, flattened_items=items)

            else:
                items = codable_set._object_dict.items()

            write_csv(items=items.values(),
                      filepath=filepath,
                      fieldnames=fieldnames)

        @staticmethod
        def flatten(mapping: dict) -> dict:
            return flatten_dict.flatten(mapping, reducer="double-colon", enumerate_types=(list, set), keep_empty_types=(dict, set))

        @staticmethod
        def unflatten(mapping: dict) -> dict:
            return flatten_dict.unflatten(mapping, splitter="double-colon")

        @staticmethod
        def update_fieldnames_if_flattened(fieldnames: list[str], flattened_items: dict[str, dict[str, str]]) -> list[str]:

            # get all field names without duplicate
            fieldnames_set = set[str](key for item in flattened_items.values()
                                      for key in item.keys())

            # get max number in `identifier::count`
            def get_fieldnames_count(fn_set: set[str]) -> dict[str, int]:

                pattern = "([a-zA-Z0-9_-]+)::([\d]+)"
                counter = Counter()

                for fn in fn_set:
                    match = re.search(pattern, fn, re.I)

                    if match is not None:
                        key = match.group(1)
                        index = int(match.group(2))

                        counter[key] = max(counter[key], index)

                return counter

            fieldnames_count = get_fieldnames_count(fieldnames_set)

            # generate lists and insert into field names list
            for k, v in fieldnames_count.items():
                index = fieldnames.index(k)
                fieldnames[index: index + 1] = [f"{k}::{i}"
                                                for i in range(v + 1)]

            return fieldnames

    class JSONCoding:

        @staticmethod
        def decode(codable_set: "CodableSet[C]", filepath: Path, *args, encoding="utf-8", newline="", **kwargs) -> "CodableSet[C]":

            with open(filepath, "r", encoding=encoding, newline=newline) as file:

                items: list = json.load(file)

                for item in items:
                    object: Codable = codable_set._object_type(from_dict=item)
                    codable_set._object_dict[item["id"]] = object

            return codable_set

        @staticmethod
        def encode(codable_set: "CodableSet[C]", filepath: Path, *args, encoding="utf-8", newline="", **kwargs):

            with open(filepath, "w", encoding=encoding, newline=newline) as file:

                items: list = [object.to_dict()
                               for object in codable_set._object_dict.values()]

                json.dump(items, file, indent=4)
