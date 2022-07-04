# -*- coding: utf-8 -*-

__all__ = [
    'classify',
    'strptz',
    'earliest',
]

from datetime import datetime, timedelta
from typing import *


def classify(seq: List[dict], *keys: Union[str, Callable]):
    if len(keys) < 1:
        return seq
    key = keys[0]
    topdict = dict()
    for item in seq:
        k = key(item) if callable(key) else item[key]
        if k not in topdict:
            topdict[k] = list()
        topdict[k].append(item)

    if len(keys) > 1:
        for k in topdict:
            topdict[k] = classify(topdict[k], *keys[1:])

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


if __name__ == '__main__':
    a = [
        {"category": "对象", "label": "景区", "biz_id": "0c0fa0e8e91ce800"},
        {"category": "对象", "label": "商户", "biz_id": "dd8fb16aeb1ce800"},
        {"category": "对象", "label": "酒店", "biz_id": "bad16d8feb1ce800"},
        {"category": "分类", "label": "卫生", "biz_id": "1f967953eb1ce800"},
        {"category": "分类", "label": "发票", "biz_id": "34d54653eb1ce800"},
        {"category": "分类", "label": "服务", "biz_id": "294f2856eb1ce800"},
        {"category": "分类", "label": "治安", "biz_id": "5c2c7056eb1ce800"},
    ]
    print(classify(a, 'category'))
    print(classify(a, lambda item: item.pop('category')))
