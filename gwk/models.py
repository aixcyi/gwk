# -*- coding: utf-8 -*-
"""
GWK 模型包。主要包含对数据的抽象得到的模型类。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from gwk.constants import GachaType


@dataclass
class Item:
    """
    祈愿到（抽到）的角色、武器等。
    """
    name: str
    item_type: str
    rank_type: str
    language: str = 'zh-cn'
    id: str = ''


@dataclass
class Record:
    """
    祈愿记录（抽卡记录）。
    """
    types: GachaType
    time: datetime
    item: Item
    id: str = ''
    count: int = 1
    uid: str = ''


class GachaData(dict[GachaType, list[Record]]):
    """
    包含所有卡池的所有祈愿记录（抽卡记录）的类。
    """
    uid: str = ''
    region: str = 'cn_gf01'
    language: str = 'zh-cn'

    @property
    def total(self) -> int:
        return sum(len(value) for value in self.values())

    def __getitem__(self, key):
        if key not in self:
            self.__setitem__(key, list())
        return super().__getitem__(key)
