# -*- coding: utf-8 -*-
"""
面向 `统一可交换祈愿记录标准(UIGF) <https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat>`_ 格式文件的处理器。
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import NamedTuple

from gwk.constants import DATETIME_FORMAT, GachaType
from gwk.handlers.abs import SingleGachaJsonHandler, UnsupportedFormat
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

    uid: str | None
    language: str | None
    version: str | None = None
    exporter: ExporterInfo
    exported_at: datetime | None = None

    def load(self, raw: dict):

        # ---------------- 校验文件结构 ----------------

        if 'info' not in raw:
            raise UnsupportedFormat('缺少存放文件信息的 info 字段。')
        if 'list' not in raw:
            raise UnsupportedFormat('缺少存放祈愿记录的 list 字段。')
        if not isinstance(raw['info'], dict):
            raise UnsupportedFormat('存放文件信息的 dict 字段应当是一个对象。')
        if not isinstance(raw['list'], list):
            raise UnsupportedFormat('存放祈愿记录的 list 字段应当是一个数组。')

        info: dict = raw['info']
        records: list = raw['list']

        # ---------------- 读取信息字段 ----------------

        self.version = purify(info.get('uigf_version'), str)
        self.uid = purify(info.get('uid'), str)
        self.language = purify(info.get('lang'), str)
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
                item=Item(
                    id=data['item_id'],
                    name=data['name'],
                    types=data['item_type'],
                    rank=int(data.get('rank_type', 3)),
                    lang=data['lang'],
                ),
                count=int(data.get('count', 1)),
                types=GachaType(data['gacha_type']),
                uid=data['uid'],
            )
            self.records[record.types].append(record)

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
        # todo
        pass
