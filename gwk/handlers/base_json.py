# -*- coding: utf-8 -*-
"""
JSON文件处理器的抽象类。
"""
from __future__ import annotations

import json
from pathlib import Path

from gwk.handlers.abs import HandlingException, SingleGachaFileHandler


class UnsupportedFormat(HandlingException):
    pass


class MissingField(HandlingException):

    def __init__(self, field: str, usage: str, value_desc: str):
        self.field = field
        self.usage = usage
        self.msg = f'缺少{usage}的 {field} 字段，或该字段的值不是一个 {value_desc} 。'


class SingleGachaJsonHandler(SingleGachaFileHandler):
    """
    单个祈愿记录JSON文件的处理器抽象类。
    """
    supports: list[str] = ['.json']

    def read(self, fp: Path | str, encoding='UTF-8', *args, **kwargs):
        """
        从JSON文件中读取数据，并调用 ``.load()`` 进行解析。

        :param fp: 文件地址。
        :param encoding: 字符编码。默认是 UTF-8 。
        :raise HandlingException: 解析异常。
        """
        try:
            with open(fp, 'r', encoding=encoding) as f:
                raw = json.load(f)
        except json.JSONDecodeError:
            raise UnsupportedFormat('文件解析失败，可能不是JSON文件，或文件有损坏。')
        except UnicodeError:
            raise UnsupportedFormat(f'使用 {encoding} 读取时发生Unicode相关编码错误。')

        if not isinstance(raw, dict):
            raise UnsupportedFormat('JSON文件主体应当是一个对象。')

        self.load(raw)

    def load(self, raw: dict):
        """
        从原始数据中解析并读取数据。
        """
        raise NotImplementedError

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

    def dump(self) -> dict:
        """
        将数据整理成准备写到文件中的数据流。
        """
        raise NotImplementedError
