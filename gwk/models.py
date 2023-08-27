# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime

from constants import DATETIME_FORMAT, GachaType


@dataclass
class Item:
    """
    抽到的角色、武器等。
    """
    id: str
    name: str
    rank: int
    types: str
    lang: str = 'zh-cn'


@dataclass
class Record:
    """
    抽卡记录。
    """
    id: str
    time: datetime
    item: Item
    count: int
    types: GachaType

    uid: str
    region: str = "cn_gf01"

    def to_uigf(self) -> dict:
        return {
            "uid": self.uid,
            "gacha_type": self.types.value,
            "item_id": self.item.id,
            "count": str(self.count),
            "time": self.time.strftime(DATETIME_FORMAT),
            "name": self.item.name,
            "lang": self.item.lang,
            "item_type": self.item.types,
            "rank_type": str(self.item.rank),
            "id": self.id,
            "uigf_gacha_type": self.types.uigf_type,
        }
