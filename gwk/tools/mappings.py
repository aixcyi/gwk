# -*- coding: utf-8 -*-

__all__ = [
    'map_raw_to_uigf_j2',
    'map_raw_to_basic',
    'map_fix_time',
]

from datetime import datetime

from gwk.constants import *


def map_raw_to_uigf_j2(record: dict) -> dict:
    """
    【映射函数】删除祈愿记录中的以下字段：

    - uid
    - lang

    并将根据 gacha_type 字段生成 uigf_gacha_type 字段。
    """
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
    """
    【映射函数】删除祈愿记录中的以下字段：

    - uid
    - item_id
    - count
    - lang
    """
    del record['uid']
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
    record['time'] = dt_obj.strftime(UNIFORM_TIME_FORMAT)
    return record
