# -*- coding: utf-8 -*-
"""
GWK 常量包。主要包含通用的常量和枚举。
"""
__all__ = [
    'DATETIME_FORMAT',
    'DT_DREAM_START',
    'DT_STAMP_OFFSET_CHANGE',
    'DT_VERSION_START_2_3',
    'GachaType'
]

from datetime import datetime

from gwk.utils import Items

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
"""
通用日期时间格式。
"""

DT_DREAM_START = datetime(2020, 9, 28)
"""
梦开始的时间。（该常量用于模拟祈愿记录ID，因为有的软件将祈愿记录的ID当作有符号64位整数读取，导致不得不以缩短时间戳长度为代价换取兼容）
"""

DT_STAMP_OFFSET_CHANGE = datetime(2020, 12, 31)
"""
从 2021 年开始，抽卡记录的 id 的时间戳部分分钟数固定为 6 。
"""

DT_VERSION_START_2_3 = datetime(2021, 11, 24, 7, 0, 0)
"""
从 2.3 版本开始，抽卡记录的自增id部分改为自增整数+玩家uid最后两位。
"""


class GachaType(Items):
    """
    祈愿的卡池类型。
    """
    BEGINNERS_WISH = '100', 90, '100', '新手祈愿'
    WANDERLUST_INVOCATION = '200', 90, '200', '常驻祈愿'
    CHARACTER_EVENT_WISH = '301', 90, '301', '角色活动祈愿'
    CHARACTER_EVENT_WISH_2 = '400', 90, '301', '角色活动祈愿-2'
    WEAPON_EVENT_WISH = '302', 80, '302', '武器活动祈愿'

    __properties__ = 'ceiling', 'uigf_type', 'label',

    @property
    def label(self) -> str:
        """
        卡池名称。
        """
        return self._label_

    @property
    def ceiling(self) -> int:
        """
        出金的保底抽卡次数。
        """
        return self._ceiling_

    @property
    def uigf_type(self):
        """
        对应的 `uigf_gacha_type <https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat#gachatype>`_ 。
        """
        return self._uigf_type_
