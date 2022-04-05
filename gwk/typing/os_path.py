# -*- coding: utf-8 -*-

from os.path import isfile, expanduser, join


class Path:
    def __init__(self, root: str = ''):
        self.path = expanduser(root)

    def __truediv__(self, other: str):
        self.path = join(self.path, other)
        return self

    def __str__(self):
        return self.path

    def is_file(self) -> bool:
        return isfile(self.path)
