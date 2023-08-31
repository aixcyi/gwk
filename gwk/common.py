# -*- coding: utf-8 -*-
from itertools import groupby

from gwk.constants import DT_DREAM_START
from gwk.models import GachaData


def patch_id64(data: GachaData, uid: str = None) -> tuple[int, int]:
    """
    模拟生成祈愿记录的ID，并补充到数据集中。

    模拟ID在设计上保证是一个有符号64位整数：
      - 祈愿时间戳，以原神开服当天的零点为起点。2023-11-29 9:46:40 以后是 9位。
      - 玩家UID，9位。
      - 用于区别十连祈愿产生相同时间的记录的偏移量，1位。

    以下两点需要注意：
      - 祈愿记录 ``time`` 字段不能为空，否则将会跳过填充。
      - 2049-12-20 4:46:43 以后的祈愿记录的模拟ID会超过有符号64位整数上限。

    :param data: 祈愿数据集。
    :param uid: 玩家ID。仅在 ``data.uid`` 和祈愿记录 ``uid`` 字段同时为空时使用。
    :return: 两个整数。前者是缺失 ``id`` 的祈愿记录的总数，后者是使用了模拟ID填充的记录总数。
    """
    rows_total_broken = len([0 for rows in data.values() for row in rows if not row.id])
    rows_total_effected = 0
    epoch = DT_DREAM_START.timestamp()

    for gacha_type in data:

        results = list()
        for time, group in groupby(data[gacha_type], key=GachaData.key_):
            rows = list(sorted(group, key=lambda r: r.id))

            if not time:
                results.extend(rows)
                continue

            offset = -1
            for row in rows:
                if row.id:
                    continue
                offset += 1
                rows_total_effected += 1
                stamp = str(int(row.time.timestamp() - epoch))
                userid = (row.uid or data.uid or uid or '').rjust(9, '0')
                suffix = str(offset)
                row.id = stamp + userid + suffix
            results.extend(rows)

        data[gacha_type] = results

    return rows_total_broken, rows_total_effected
