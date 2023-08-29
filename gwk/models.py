# -*- coding: utf-8 -*-
"""
GWK 模型包。主要包含对数据的抽象得到的模型类。
"""

from __future__ import annotations

from datetime import datetime

from constants import GachaType


class Item:
    """
    祈愿到（抽到）的角色、武器等。
    """

    def __init__(
            self,
            name: str,
            item_type: str,
            rank_type: int | str,
            item_id: str = '',
            lang: str = 'zh-cn',
            **_,
    ):
        self.id = item_id
        self.name = name
        self.rank = rank_type
        self.types = item_type
        self.lang = lang


class Record:
    """
    祈愿记录（抽卡记录）。
    """

    def __init__(
            self,
            id: str,
            item: Item,
            gacha_type: GachaType | str,
            time: datetime | str,
            count: int | str = 1,
            uid: str = None,
    ):
        self.id: str = id
        self.time: datetime | None = time
        self.item: Item = item
        self.count: int = count
        self.types: GachaType = gacha_type
        self.uid: str | None = uid


class GachaData(dict[GachaType, list[Record]]):
    """
    包含所有卡池的所有祈愿记录（抽卡记录）的类。
    """
    uid: str
    region: str = 'cn_gf01'
    language: str = 'zh-cn'
