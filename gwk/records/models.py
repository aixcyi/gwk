# -*- coding: utf-8 -*-

__all__ = [
    'Wish',
    'map_raw_to_uigf_j2',
    'map_raw_to_basic',
]

from datetime import datetime
from typing import Callable

from gwk.constants import *


def map_raw_to_uigf_j2(record: dict) -> dict:
    del record['uid']
    del record['lang']
    record['uigf_gacha_type'] = {
        '100': WishType.BEGINNERS_WISH,
        '200': WishType.WANDERLUST_INVOCATION,
        '301': WishType.CHARACTER_EVENT_WISH,
        '302': WishType.WEAPON_EVENT_WISH,
        '400': WishType.CHARACTER_EVENT_WISH,
    }[record['gacha_type']].value
    return record


def map_raw_to_basic(record: dict) -> dict:
    del record['uid']
    del record['gacha_type']
    del record['item_id']
    del record['count']
    del record['lang']
    return record


def map_fix_time(record: dict) -> dict:
    """
    【映射函数】为祈愿记录添加 ``time`` 字段（祈愿时间）。

    - 添加的祈愿时间不一定为精确值。
    - 使用此函数前需要确保祈愿记录拥有 ``id`` 字段。
    - 已有的 ``time`` 字段值将会被覆盖。
    """
    dt_obj = datetime.fromtimestamp(int(record['id'][:10]))
    record['time'] = dt_obj.strftime(TF_RECORD_HMS)
    return record


class Wish(list):
    """
    祈愿卡池历史记录。
    """

    def __init__(self, wish_type: WishType):
        super().__init__()

        self.wish_type = wish_type
        """祈愿卡池类型。"""

        self.CEILING = CEILINGS[wish_type]
        """祈愿保底次数（抽出五星金色品质的最大抽取次数）。"""

    def __repr__(self) -> str:
        return '<%s(%s) %s，历史记录：%d，语言文字：%s>' % (
            self.__class__.__name__, self.wish_type, self.wish_type.label,
            len(self), self.language,
        )

    def __eq__(self, o) -> bool:
        if type(o) is not self.__class__:
            return False
        return o.wish_type == self.wish_type

    @property
    def uid(self) -> str:
        """玩家在原神中的账号号码。"""
        return self._uid_ if hasattr(self, '_uid_') else ''

    @property
    def language(self) -> str:
        """祈愿历史记录的语言文字。"""
        return self._lang_ if hasattr(self, '_lang_') else ''

    def sort(self, key=lambda r: (r['time'], r['id']), reverse: bool = False):
        """
        对祈愿历史记录排序，然后去除重复项。

        - 使用 ``id`` 字段鉴别重复记录。如果其字段值相同，将会直接判定为重复并清除。
        - 默认的排序依据为 ``time``、``id`` 两个字段。

        :param key: 排序依据。
        :param reverse: 是否倒序排列。
        """
        super().sort(key=key, reverse=reverse)
        for i in range(len(self) - 1, 0, -1):
            # 注意range的区间是 (0, __len__]
            if self[i]['id'] == self[i - 1]['id']:
                self.pop(i)

    def maps(self, mapping: Callable):
        """
        更改每一条祈愿历史记录的字段结构。

        :param mapping: 映射函数。其应当有且仅有一个参数和返回值，负责单一一条记录的字段结构更改。
        """
        records = list(map(mapping, self))
        self.clear()
        self.insert(0, records)

    def touch(self):
        """
        根据祈愿记录获取相关信息，并填充到以下属性：

        - ``self.uid``
        - ``self.language``
        """
        if self.__len__() > 0:
            try:
                self._uid_ = self[0]['uid']
                self._lang_ = self[0]['lang']
            except IndexError:
                pass
