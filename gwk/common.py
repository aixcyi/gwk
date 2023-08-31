from itertools import groupby

from gwk.models import GachaData


def patch_data(data: GachaData, uid: str = None):
    """
    模拟生成祈愿记录的ID。
    """
    rows_total_broken = len([0 for rows in data.values() for row in rows if not row.id])
    rows_total_effected = 0

    for gacha_type in data:

        results = list()

        for time, group in groupby(data[gacha_type], key=GachaData.key_):
            rows = list(sorted(group, key=lambda r: r.id))

            if not time:
                results.extend(rows)
                continue

            offset = 0
            for row in rows:
                if row.id:
                    continue
                offset += 1
                rows_total_effected += 1
                stamp = str(int(row.time.timestamp()))
                userid = (row.uid or data.uid or uid or '').rjust(9, '0')
                suffix = str(offset).rjust(2, '0')
                row.id = stamp + userid + suffix
            results.extend(rows)

        data[gacha_type] = results

    return rows_total_broken, rows_total_effected
