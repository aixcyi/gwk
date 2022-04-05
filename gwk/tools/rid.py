# -*- coding: utf-8 -*-

__all__ = [
    'fit_id',
    'make_id',
]

from datetime import datetime

from gwk.constants import *


def fit_id(time: str, offset: int, uid: int) -> str:
    """
    祈愿历史记录ID拟合函数。（更贴近原始ID）

    :param time: 祈愿时间。字符串格式应为 "yyyy-MM-dd HH:mm:ss"
    :param offset: 偏移量。用于当祈愿时间相同时生成不同的ID，
                   取值范围为0到999,9999。
    :param uid: 玩家账号号码。
    :return: 19位纯数字组成的字符串。
    """
    wish_time = datetime.strptime(time, UNIFORM_TIME_FORMAT)
    tt = list(wish_time.timetuple())
    if wish_time <= DT_STAMP_OFFSET_CHANGE:
        tt[4], tt[5] = 0, 0
    else:
        tt[4], tt[5] = 6, 0
    record_time = datetime(*tt[:6])
    left = str(int(record_time.timestamp())).rjust(10, '0')

    if wish_time >= DT_VERSION_START_2_3:
        offset = offset * 100 + uid % 100
    right = str(offset % 1000000000).rjust(9, '0')

    return left + right


def make_id(
        time: str,
        generator: int,
        player: int,
        offset: int = 0
) -> str:
    """
    高精度祈愿历史记录ID生成函数。（编码空间更大，墙裂推荐）

    :param time: 祈愿时间。字符串格式应为 "yyyy-MM-dd HH:mm:ss"
    :param generator: 生成器标识。用于标记不同应用或中间件生成的ID。
                    取值范围[0,16383]。
    :param player: 玩家标识。用于标记不同玩家。取值范围为[0,4095]。
    :param offset: 偏移量。用于当祈愿时间相同时生成不同的ID，
                   取值范围为[0,15]。
    :return: 19位纯数字组成的字符串。
    """
    wish_time = datetime.strptime(time, UNIFORM_TIME_FORMAT)
    wish_stamp = int(wish_time.timestamp())
    return str(
        (0x7FFFFFFFC0000000 & wish_stamp << 30) +
        (0x000000003FFF0000 & generator << 16) +
        (0x000000000000FFF0 & player << 4) +
        (0x000000000000000F & offset)
    )
