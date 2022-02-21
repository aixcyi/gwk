# -*- coding: utf-8 -*-

__all__ = [
    'WishType',
    'CEILINGS',
    'TF_RECORD_HMS',
    'DT_STAMP_OFFSET_CHANGE',
    'DT_VERSION_START_2_3',
]

from datetime import datetime

from gwk.typing import Choices


class WishType(Choices):
    """祈愿卡池类型。"""

    BEGINNERS_WISH = '100', '新手祈愿'
    WANDERLUST_INVOCATION = '200', '常驻祈愿'
    CHARACTER_EVENT_WISH = '301', '角色活动祈愿'
    WEAPON_EVENT_WISH = '302', '武器活动祈愿'
    # CHARACTER_EVENT_WISH_2 = '400', '角色活动祈愿-2'


CEILINGS = {
    WishType.BEGINNERS_WISH: 90,  # 新手祈愿
    WishType.WANDERLUST_INVOCATION: 90,  # 常驻祈愿
    WishType.CHARACTER_EVENT_WISH: 90,  # 角色活动祈愿
    WishType.WEAPON_EVENT_WISH: 80,  # 武器活动祈愿
    # WishType.CHARACTER_EVENT_WISH_2: 90,  # 角色活动祈愿-2
}


# Time Format
TF_RECORD_HMS = '%Y-%m-%d %H:%M:%S'

# Datetime
DT_STAMP_OFFSET_CHANGE = datetime(2020, 12, 31)
DT_VERSION_START_2_3 = datetime(2021, 11, 24, 7, 0, 0)
