# -*- coding: utf-8 -*-
"""
处理器的抽象类。
"""

from __future__ import annotations

from pathlib import Path

from gwk.models import GachaData


class HandlingException(Exception):

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class SingleGachaFileHandler:
    """
    单个祈愿记录文件的处理器抽象类。
    """
    supports: list[str] = []

    data: GachaData = GachaData()

    def is_supported(self, fp: Path | str) -> bool:
        """
        快速（初步）判断当前处理器是否支持读取指定类型的文件。
        """
        if not isinstance(fp, Path):
            fp = Path(fp)
        return fp.suffix in self.supports

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
