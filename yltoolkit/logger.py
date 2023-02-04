#!/usr/bin/env python
# coding=utf-8


"""
Logger.
"""

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname, join

    sys.path.insert(0, abspath(join(dirname(__file__), "../..")))


from loguru import logger

"""
Credit: https://github.com/Delgan/loguru
Credit: https://loguru.readthedocs.io/en/stable/api/logger.html
Credit: https://betterstack.com/community/guides/logging/loguru/
"""
