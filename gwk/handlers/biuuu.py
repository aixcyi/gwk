# -*- coding: utf-8 -*-
"""
面向 biuuu 作者的 `原神祈愿记录导出工具（Genshin Wish Export） <https://github.com/biuuu/genshin-wish-export>`_ 导出文件的支持。
"""
from __future__ import annotations

from datetime import datetime

from gwk.constants import DATETIME_FORMAT, GachaType
from gwk.handlers.base_json import MissingField, SingleGachaJsonHandler
from gwk.models import Item, Record
from gwk.utils import purify


class BiuuuJsonHandler(SingleGachaJsonHandler):
    """
    biuuu 作者的 `原神祈愿记录导出工具（Genshin Wish Export） <https://github.com/biuuu/genshin-wish-export>`_ 导出的JSON文件处理器。
    """

    exported_at: datetime

    def load(self, raw: dict):

        if 'uid' not in raw or not isinstance(raw['uid'], str):
            raise MissingField('uid', '玩家游戏ID', '字符串'),
        if 'time' not in raw or not isinstance(raw['time'], int):
            raise MissingField('time', '记录导出时间', '整数'),
        if 'result' not in raw or not isinstance(raw['result'], list):
            raise MissingField('result', '存放祈愿记录', '数组'),

        # --------------------------------

        self.data.uid = raw['uid']
        self.data.language = purify(raw.get('lang'), str)
        self.exported_at = datetime.fromtimestamp(raw['time'])

        # --------------------------------

        # 他是按不同卡池来存放的
        pools: list = raw['result']

        # 每个 pool 都是一个 [gacha_type, [...]]
        for pool in pools:
            try:
                gt, rows, *_ = pool
                gt = GachaType(gt)
            except ValueError:
                continue

            for row in rows:
                try:
                    record = self.parse_row(row, gt)
                except:
                    continue
                self.data[record.types].append(record)

    @staticmethod
    def parse_row(row: list, default_gacha_type: GachaType) -> Record:
        if len(row) >= 6:
            time, name, item_type, rank_type, gacha_type, rid, *_ = row
        else:
            time, name, item_type, rank_type, *_ = row
            gacha_type = default_gacha_type
            rid = ''

        item = Item(
            name=str(name),
            item_type=str(item_type),
            rank_type=str(rank_type),
        )
        return Record(
            types=gacha_type,
            item=item,
            id=rid,
            time=datetime.strptime(time, DATETIME_FORMAT),
        )

    def dump(self) -> dict:
        return {
            'uid': self.data.uid,
            'lang': self.data.language,
            'time': self.exported_at.timestamp(),
            'typeMap': [[t.value, t.label] for t in GachaType],
            'result': [
                [
                    gt.uigf_type,
                    list(map(self.serialize_record, records))
                ]
                for gt, records in self.data.items()
            ]
        }

    @staticmethod
    def serialize_record(record: Record) -> list:
        if record.id:
            return [
                record.time.strftime(DATETIME_FORMAT),
                record.item.name,
                record.item.item_type,
                int(record.item.rank_type),
                record.types.value,
                record.id,
            ]
        else:
            return [
                record.time.strftime(DATETIME_FORMAT),
                record.item.name,
                record.item.item_type,
                int(record.item.rank_type),
            ]
