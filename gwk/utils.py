# -*- coding: utf-8 -*-

__all__ = [
    'classify',
    'strptz',
    'earliest',
]

from datetime import datetime, timedelta
from typing import *


def classify(
        listing: List[dict],
        *classifications: Union[str, Tuple[str, Callable]]
):
    if len(classifications) < 1:
        return listing
    if type(classifications[0]) is str:
        key, mapper = classifications[0], None
    elif type(classifications[0]) is tuple:
        key, mapper, *_ = classifications[0]
    else:
        raise TypeError()

    topdict = dict()
    for item in listing:
        k = mapper(item[key]) if callable(mapper) else item[key]
        if k not in topdict:
            topdict[k] = list()
        topdict[k].append(item)

    if len(classifications) > 1:
        for k in topdict:
            topdict[k] = classify(topdict[k], *classifications[1:])

    return topdict


def strptz(dt: datetime, default=None):
    offset = dt.utcoffset()
    if not offset:
        return default
    seconds = offset.seconds
    sign = '+' if seconds >= 0 else '-'
    seconds = abs(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f'UTC{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'


def earliest(fmt: str = '%Y-%m-%d') -> Union[str, datetime]:
    """
    原神只能获取最近六个月的祈愿历史记录。
    此方法用于计算最早可以获取到哪天的祈愿记录。

    :param fmt: 日期时间的字符串格式。若为None，则直接返回datetime对象。
    :return: 返回一个datetime或str，表示可能获取到的最早的记录的日期。
    """
    time = datetime.now() - timedelta(days=6 * 30 - 1)
    return time.strftime(fmt) if fmt else time
