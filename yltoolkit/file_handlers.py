#!/usr/bin/env python
# coding=utf-8


"""
File handlers.
"""

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname, join

    sys.path.insert(0, abspath(join(dirname(__file__), "..")))


import csv
import hashlib
import shutil
from functools import reduce
from pathlib import Path
from typing import Any, Callable, Literal

from PIL import Image

from yltoolkit.YLDatetime import TimeStandard, YLDatetime


def read_csv(filepath: Path, *,
             fieldnames_recognizer: dict[str, str] = None,
             fieldnames_handler: Callable[[list[str]],
                                          list[str]] = None,
             pairing_handler: Callable[[list[str], list[str]],
                                       dict[str, Any]] = None,
             mapping_handler: Callable[[dict[str, Any]], None]
             ):
    """
    CSV file read in as a dictionary.
    @param fieldnames_recognizer: dict[str, str]
    @param fieldnames_handler: (fieldnames: list[str]) -> list[str]
    @param pairing_handler: (fieldnames: list[str], values: list[str]) -> dict[str, Any]
    @param mapping_handler: (mapping: dict[str, Any]) -> None
    fieldnames_recognizer first, and then fieldnames_handler
    """

    if fieldnames_recognizer is None  \
            and fieldnames_handler is None   \
            and pairing_handler is None:

        # simple csv dict reader
        with open(filepath, "r", encoding="utf-8-sig", newline="") as file:

            reader = csv.DictReader(file)

            for row in reader:

                row.pop("", None)  # remove empty key-value pairs
                mapping_handler(row)

    else:
        # use reader and customize reading handlers
        with open(filepath, "r", encoding="utf-8-sig", newline="") as file:

            reader = csv.reader(file)

            # first row are field names
            fieldnames = next(reader)

            if fieldnames_recognizer is not None:
                fieldnames = [fieldnames_recognizer.get(name, name)
                              for name in fieldnames]

            if fieldnames_handler is not None:
                fieldnames = fieldnames_handler(fieldnames)

            for row in reader:

                if pairing_handler is not None:
                    mapping = pairing_handler(fieldnames, row)
                else:
                    mapping = dict(zip(fieldnames, row))

                mapping.pop("", None)  # remove empty key-value pairs
                mapping_handler(mapping)


def read_csv_to_list(filepath: Path, *,
                     fieldnames_recognizer: dict[str, str] = None,
                     fieldnames_handler: Callable[[list[str]],
                                                  list[str]] = None,
                     pairing_handler: Callable[[list[str], list[str]],
                                               dict[str, Any]] = None) -> list[dict[str, Any]]:
    result = list[dict[str, Any]]()

    read_csv(filepath=filepath,
             fieldnames_recognizer=fieldnames_recognizer,
             fieldnames_handler=fieldnames_handler,
             pairing_handler=pairing_handler,
             mapping_handler=lambda mapping: result.append(mapping)
             )

    return result


def read_csv_with_duplicated_fieldnames(filepath: Path, *, fieldnames_recognizer: dict[str, str] = None, duplication_handler: Literal["remap", "tolist", "do_nothing"] = "remap") -> list[dict[str, str]]:

    def remap_fieldnames_handler(fieldnames: list[str]) -> list[str]:

        result = list[str]()
        counts = dict[str, int]()

        for fieldname in fieldnames:
            if fieldname not in counts:
                counts[fieldname] = 0
            else:
                counts[fieldname] += 1

            result.append(f"{fieldname}::{counts[fieldname]}")

        for fieldname, count in counts.items():
            if count == 0:
                index = result.index(f"{fieldname}::0")
                result[index] = f"{fieldname}"

        return result

    def tolist_pairing_handler(fieldnames: list[str], row: list[str]) -> dict[str, str]:

        result = dict[str, str | list[str]]()

        for fieldname, value in zip(fieldnames, row):
            if fieldname not in result:
                result[fieldname] = value
            else:
                if not isinstance(result[fieldname], list):
                    result[fieldname] = [result[fieldname],]

                result[fieldname].append(value)

        return result

    duplication_handler = duplication_handler.lower()
    assert duplication_handler in ["remap", "tolist", "do_nothing"]

    result = list[dict[str, str]]()
    def mapping_handler(mapping): return result.append(mapping)

    if duplication_handler == "remap":
        read_csv(filepath,
                 fieldnames_recognizer=fieldnames_recognizer,
                 fieldnames_handler=remap_fieldnames_handler,
                 pairing_handler=None,
                 mapping_handler=mapping_handler)

    elif duplication_handler == "tolist":
        read_csv(filepath,
                 fieldnames_recognizer=fieldnames_recognizer,
                 fieldnames_handler=None,
                 pairing_handler=tolist_pairing_handler,
                 mapping_handler=mapping_handler)

    else:
        read_csv(filepath,
                 fieldnames_recognizer=fieldnames_recognizer,
                 mapping_handler=mapping_handler)

    return result


def write_csv(items: list[dict[str, str]],
              filepath: Path, *,
              fieldnames: list[str] = None,
              fieldnames_adapter: dict[str, str] = None
              ):
    """
    Write a dictionary into a CSV file.
    @param fieldnames_adapter: dict[str, str]
    fieldnames_recognizer first, and then fieldnames_handler
    """

    if fieldnames is None:
        fieldnames: list[str] = reduce(lambda x, y: x | y, items).keys()

    if fieldnames_adapter is None:
        # simple csv dict reader
        with open(filepath, "w", encoding="utf-8-sig", newline="") as file:

            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()

            for item in items:
                writer.writerow(item)

    else:
        # use reader and customize reading handlers

        if fieldnames_adapter is not None:
            adapted_fieldnames = [fieldnames_adapter.get(name, name)
                                  for name in fieldnames]

        with open(filepath, "w", encoding="utf-8-sig", newline="") as file:

            writer = csv.writer(file)

            writer.writerow(adapted_fieldnames)

            for item in items:
                row = [item.get(name, None) for name in fieldnames]
                writer.writerow(row)


def ensure_directory(path: Path):
    """
    Create a directory if it doesn't exist.
    """

    path.mkdir(parents=True, exist_ok=True)
    return path


def map_files_in_directory(directory: Path) -> dict[str, Path]:

    return {filepath.name: filepath
            for filepath in directory.glob("**/*.*")
            if filepath.is_file()}


def copy_and_paste(source: Path, destination: Path):
    if destination.exists():
        raise FileExistsError

    shutil.copy(source, destination)


def move(source: Path, destination: Path):
    source.rename(destination)


def archive(output_filepath: Path, root_filepath: Path):

    assert output_filepath.suffix.lower() == ".zip"

    output_filepath = str(output_filepath).replace(output_filepath.suffix, "")

    shutil.make_archive(output_filepath, "zip", root_filepath)


def get_filesize(filepath: Path, formatter: Literal["kB", "MB", "GB"] | None = None) -> int:

    filesize = filepath.stat().st_size

    if formatter is None:
        return filesize
    else:
        return format_filesize(filesize, unit=formatter)


def format_filesize(size_in_byte: Path, unit: Literal["kB", "MB", "GB"]) -> float:
    match unit:
        case "kB":
            return size_in_byte / 1024
        case "MB":
            return size_in_byte / 1024 / 1024
        case "GB":
            return size_in_byte / 1024 / 1024 / 1024


def get_file_hash(filepath: Path) -> str:
    """
    General-purpose solution that can process large files.

    Credit: https://stackoverflow.com/a/64994148
    Credit: https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    """

    md5 = hashlib.md5()

    with open(filepath, "rb") as f:

        while True:
            # arbitrary number to reduce RAM usage
            data = f.read(65536)

            if not data:
                break

            md5.update(data)

    return md5.hexdigest()


def get_exif_datetime(filepath: Path) -> YLDatetime:
    """
    Get datetime generated/taken of an image continuing EXIF.
    EXIF Tags code: https://exiv2.org/tags.html
    """

    EXIF_IMAGE_DATETIMEORIGINAL = 36867
    EXIF_IMAGE_DATETIME = 306

    im = Image.open(filepath)
    exif = im.getexif()
    im.close()

    time_str = exif.get(EXIF_IMAGE_DATETIMEORIGINAL)

    if time_str is None:
        time_str = exif.get(EXIF_IMAGE_DATETIME)

    if time_str is not None:
        time = YLDatetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
        return time.replace_timestandard(standard=TimeStandard.CST)
    else:
        return None


"""
import string
import shortuuid

alphabet = string.ascii_uppercase + string.digits
su = shortuuid.ShortUUID(alphabet=alphabet)

def get_uuid(length: int = 8) -> str:

    result = su.random(length=length)
    return f"{result[:4]}-{result[4:]}"
"""
