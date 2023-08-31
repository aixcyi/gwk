# -*- coding: utf-8 -*-
"""
面向 `统一可交换祈愿记录标准(UIGF) <https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat>`_ 格式文件的处理器。
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from gwk.constants import DATETIME_FORMAT, GachaType
from gwk.handlers.base_json import MissingField, SingleGachaJsonHandler
from gwk.models import Item, Record
from gwk.utils import purify


class UigfJsonHandler(SingleGachaJsonHandler):
    """
    `统一可交换祈愿记录标准(UIGF) <https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat>`_ JSON格式文件处理器。
    """
    abstract = False
    versions: list[str] = ['v2.0', 'v2.1', 'v2.2']
    description = (
        '统一可交换祈愿记录标准JSON格式（UIGF.J）处理器。'
    )

    version: str = None
    exported_at: datetime = None
    exporter_name: str = None
    exporter_version: str = None

    def dump(self) -> dict:
        now = datetime.now()
        return {
            'info': {
                'uid': self.data.uid or '',
                'lang': self.data.language or 'zh-cn',
                'export_time': (self.exported_at or now).strftime(DATETIME_FORMAT),
                'export_timestamp': int((self.exported_at or now).timestamp()),
                'export_app': self.exporter_name or '',
                'export_app_version': self.exporter_version or '',
                'uigf_version': self.versions[-1],
            },
            'list': [
                {
                    "uid": record.uid,
                    "gacha_type": record.types.value,
                    "item_id": record.item.id,
                    "count": str(record.count),
                    "time": record.time.strftime(DATETIME_FORMAT),
                    "name": record.item.name,
                    "lang": record.item.language,
                    "item_type": record.item.item_type,
                    "rank_type": str(record.item.rank_type),
                    "id": record.id,
                    "uigf_gacha_type": record.types.uigf_type,
                }
                for types, records in self.data.items()
                for record in records
            ],
        }

    def load(self, raw: dict):

        if 'info' not in raw or not isinstance(raw['info'], dict):
            raise MissingField('info', '存放文件信息', '对象')
        if 'list' not in raw or not isinstance(raw['list'], list):
            raise MissingField('list', '存放祈愿记录', '数组')

        # --------------------------------

        headers = defaultdict(lambda: None, raw['info'])

        self.data.uid = purify(headers['uid'], str)
        self.data.language = purify(headers['lang'])

        self.version = purify(headers['uigf_version'])
        self.exported_at = self.parse_export_time(headers)
        self.exporter_name = purify(headers['export_app'])
        self.exporter_version = purify(headers['export_app_version'])

        # --------------------------------

        rows: list = raw['list']

        for row in rows:
            self.rows_total_read += 1
            if not isinstance(row, dict):
                continue
            try:
                record = self.parse_row(row)
            except:
                continue
            self.data[record.types].append(record)
            self.rows_total_loaded += 1

        self.data.sort()

    @staticmethod
    def parse_export_time(headers: dict) -> datetime | None:
        try:
            return datetime.strptime(headers['export_time'], DATETIME_FORMAT)
        except ValueError:
            pass
        try:
            return datetime.fromtimestamp(int(headers['export_timestamp']))
        except (ValueError, OSError):
            pass
        return None

    def parse_row(self, row: dict) -> Record:
        item = Item(
            name=str(row['name']),
            item_type=str(row['item_type']),
            rank_type=str(row['rank_type']),
        )
        if 'lang' in row:
            item.language = str(row['lang'])

        record = Record(
            types=GachaType(row['gacha_type']),
            time=datetime.strptime(row['time'], DATETIME_FORMAT),
            item=item,
            id=row['id'] if 'id' in row else None,
            uid=row['uid'] if 'uid' in row else self.data.uid,
            count=int(row['count']) if 'count' in row else None,
        )
        return record
