# -*- coding: utf-8 -*-
"""
处理器的抽象类。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gwk.constants import GachaType


class HandlingException(Exception):

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class UnsupportedFormat(HandlingException):
    pass


class SingleGachaFileHandler:
    """
    单个祈愿记录文件的处理器抽象类。
    """
    supports: list[str]
    records: dict[GachaType, list]

    def is_supported(self, fp: Path | str) -> bool:
        """
        当前处理器是否支持读取指定类型的文件。
        """
        if not isinstance(fp, Path):
            fp = Path(fp)
        return fp.suffix in self.supports

    def read(
            self,
            fp: Path | str,
            encoding='UTF-8',
            *args,
            **kwargs
    ):
        """
        从文件中读取数据。
        """
        raise NotImplementedError

    def write(
            self,
            fp: Path | str = None,
            encoding='UTF-8',
            *args,
            **kwargs
    ):
        """
        将数据导出到文件。
        """
        raise NotImplementedError

    def load(self, raw: Any):
        """
        从原始数据中解析并读取数据。
        """
        raise NotImplementedError

    def dump(self) -> Any:
        """
        将数据整理成准备写到文件中的数据流。
        """
        raise NotImplementedError


class SingleGachaJsonHandler(SingleGachaFileHandler):
    supports: list[str] = ['.json']

    def read(
            self,
            fp: Path | str,
            encoding='UTF-8',
            *args,
            **kwargs
    ):
        """
        从JSON文件中读取数据，并调用 ``.load()`` 进行解析。

        :param fp: 文件地址。
        :param encoding: 字符编码。默认是 UTF-8 。
        :raise HandlingException: 解析异常。
        """
        with open(fp, 'r', encoding=encoding) as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            raise UnsupportedFormat('JSON文件主体应当是一个对象。')
        self.load(raw)

    def write(
            self,
            fp: Path | str = None,
            encoding='UTF-8',
            minimum=True,
            *args,
            **kwargs
    ):
        """
        将 ``.dump()``  生成的数据写入到JSON文件中。

        :param fp: 文件地址。
        :param encoding: 字符编码。默认是 UTF-8 。
        :param minimum: 是否以最简格式写入（去除格式上的所有空格）。
        """
        with open(fp, 'r', encoding=encoding) as f:
            data = self.dump()
            if minimum:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            else:
                json.dump(data, f, ensure_ascii=False)

    def load(self, raw: dict):
        raise NotImplementedError

    def dump(self) -> dict:
        raise NotImplementedError
