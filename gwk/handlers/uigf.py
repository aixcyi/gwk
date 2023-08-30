# -*- coding: utf-8 -*-
"""
面向 `统一可交换祈愿记录标准(UIGF) <https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat>`_ 格式文件的处理器。
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import NamedTuple

from gwk.constants import DATETIME_FORMAT, GachaType
from gwk.handlers.base_json import MissingField, SingleGachaJsonHandler, WrongFieldType
from gwk.models import Item, Record
from gwk.utils import purify


class ExporterInfo(NamedTuple):
    name: str | None
    version: str | None


class UigfJsonHandler(SingleGachaJsonHandler):
    """
    `统一可交换祈愿记录标准(UIGF) <https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat>`_ JSON格式文件处理器。
    """
    versions: list[str] = ['v2.0', 'v2.1', 'v2.2']

    version: str | None = None
    exporter: ExporterInfo
    exported_at: datetime | None = None

    def load(self, raw: dict):

        # ---------------- 校验文件结构 ----------------

        self.assert_datastructure(
            raw,
            MissingField('info', '存放文件信息'),
            MissingField('list', '存放祈愿记录'),
            WrongFieldType('info', '文件信息', dict, '对象'),
            WrongFieldType('list', '祈愿历史', list, '数组'),
        )
        info: dict = raw['info']
        records: list = raw['list']

        # ---------------- 读取信息字段 ----------------

        self.version = purify(info.get('uigf_version'), str)
        self.data.uid = purify(info.get('uid'), str)
        self.data.language = purify(info.get('lang'), str)
        self.exporter = ExporterInfo(
            purify(info.get('export_app'), str),
            purify(info.get('export_app_version'), str)
        )
        self._parse_export_time(info)

        # ---------------- 校验祈愿记录 ----------------

        for r in records:
            if not isinstance(r, dict):
                continue
            data = defaultdict(lambda: '', r)
            record = Record(
                id=data['id'],
                time=datetime.strptime(data['time'], DATETIME_FORMAT),
                item=Item(**data),
                count=int(data.get('count', 1)),
                gacha_type=GachaType(data['gacha_type']),
                uid=data['uid'],
            )
            self.data[record.types].append(record)

        # ---------------- 载入解析结束 ----------------

    def _parse_export_time(self, info: dict):
        """
        当 ``export_time`` 字段解析失败时自动使用 ``export_timestamp`` 字段的值，而不考虑版本。
        """
        export_time = info.get('export_time')
        if isinstance(export_time, str):
            try:
                self.exported_at = datetime.strptime(export_time, DATETIME_FORMAT)
                return
            except ValueError:
                pass

        export_timestamp = info.get('export_timestamp')
        try:
            stamp = float(export_timestamp)
        except ValueError:
            return

        self.exported_at = datetime.fromtimestamp(stamp)

    def dump(self) -> dict:
        now = datetime.now()
        info = {
            'uid': self.data.uid or '',
            'lang': self.data.language or '',
            'export_time': (self.exported_at or now).strftime(DATETIME_FORMAT),
            'export_timestamp': int((self.exported_at or now).timestamp()),
            'export_app': self.exporter.name or '',
            'export_app_version': self.exporter.version or '',
            'uigf_version': self.versions[-1],
        }
        data = [
            {
                "uid": record.uid,
                "gacha_type": record.types.value,
                "item_id": record.item.id,
                "count": str(record.count),
                "time": record.time.strftime(DATETIME_FORMAT),
                "name": record.item.name,
                "lang": record.item.lang,
                "item_type": record.item.types,
                "rank_type": str(record.item.rank),
                "id": record.id,
                "uigf_gacha_type": record.types.uigf_type,
            }
            for types, records in self.data.items()
            for record in records
        ]
        return {
            'info': info, 'list': data,
        }
