# -*- coding: utf-8 -*-

__all__ = [
    'Wish',
]

import json
from datetime import datetime
from typing import *

from gwk import UIGF_APP_NAME, UIGF_APP_VERSION, UIGF_VERSION
from gwk.constants import *
from gwk.throwables import *
from gwk.utils import classify, TNF


def _check_tnf(obj, attr: str, new_value):
    """
    使用TNF策略校验与合并对象属性。

    TNF决策值应当存在该对象名为 "merge_{attr}" 的属性中，
    如果缺少这个属性，将会引发异常。

    :param obj: 目标对象（类实例）
    :param attr: 属性名称。
    :param new_value: 新的值。
    """
    old_value = getattr(obj, attr)
    policy = getattr(obj, 'merge_' + attr)

    if old_value == new_value:
        return

    if policy is True:
        setattr(obj, attr, new_value)
    elif policy is None:
        pass
    elif policy is False:
        raise MergingException(
            attr, old_value, new_value, type(obj).__name__
        )


class Wish:

    def __init__(self, wish_type: WishType = None):
        """
        祈愿卡池。包含单个祈愿卡池的所有祈愿记录。

        :param wish_type: 卡池类型。
        """
        self._records = list()
        assert type(wish_type) is WishType or wish_type is None, \
            '不应该使用除 WishType 和 None 以外的类型来初始化 Wish 。'

        self.wish_type = wish_type
        """祈愿卡池类型。"""

        self.CEILING: Final[int] = CEILINGS[wish_type] if wish_type else 0
        """祈愿保底次数（抽出五星金色品质的最大抽取次数）。"""

        self.uid = ''
        """玩家在原神中的账号号码。"""

        self.language = ''
        """祈愿历史记录的语言文字。"""

        self.region = ''
        """游戏客户端所在地区。"""

        self.merging_check = True
        """
        - ``True`` 合并前使用 TNF 策略检查被合并对象的所有信息。（默认）
        - ``False`` 合并时一概接受，不使用 TNF 策略检查任何信息。
        """

        self.merge_uid: TNF = False
        """是否允许合并不同玩家的祈愿记录。遵循TNF策略。默认为 False 。"""

        self.merge_region: TNF = False
        """是否允许合并不同地区的祈愿记录。遵循TNF策略。默认为 False 。"""

        self.merge_lang: TNF = True
        """是否允许合并不同文字的祈愿记录。遵循TNF策略。默认为 True 。"""

    def __repr__(self) -> str:
        representations = [
            f'记录数: {len(self._records)}',
            f'保底: {self.CEILING}',
            f'玩家: {self.uid}',
            f'文字: {self.language}',
            f'地区: {self.region}',
        ]
        return '<Wish(%s) %s>' % (
            self.wish_type.label if self.wish_type else '*',
            ', '.join(representations)
        )

    def __eq__(self, o) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return o.wish_type == self.wish_type

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, k):
        assert isinstance(k, (int, slice)), '仅支持整数索引或切片访问。'
        return self._records[k]

    def __iadd__(self, o):
        if isinstance(o, (list, tuple)):
            self._records += o
            return self
        if not isinstance(o, self.__class__):
            raise TypeError(
                f'Wish 不能与 {type(o).__name__} 类型相加。'
            )
        if self.wish_type is not None:
            if o.wish_type != self.wish_type:
                raise TypeError(
                    f'{o.wish_type!s} 类型的 Wish 不能与 '
                    f'{self.wish_type!s} 类型的相加。'
                )
        if self.merging_check:
            _check_tnf(self, 'uid', o.uid)
            _check_tnf(self, 'region', o.region)
            _check_tnf(self, 'language', o.language)
        else:
            self.uid = o.uid
            self.region = o.region
            self.language = o.language
        self._records += o[:]
        return self

    def nonempty(self) -> bool:
        """只要有祈愿记录就会返回``True``，否则返回``False``。"""
        return len(self._records) > 0

    # 将此操作独立为一个公开函数是为了明确其含义，
    # 将此操作同步给魔术方法是为了兼容 Python 的编程思维。
    __bool__ = nonempty

    def set(self, records: Union[list, tuple]):
        """
        用一份新的祈愿记录覆盖到祈愿卡池中。
        注意：此方法不会检验卡池的祈愿类型跟记录是否匹配。
        """
        if not isinstance(records, (list, tuple)):
            return
        self._records = list(records)

    def clear(self):
        """
        清除卡池中的所有祈愿记录。
        """
        self._records.clear()

    def sort(
            self, *,
            key=lambda r: (r['time'], r['id']),
            reverse: bool = False
    ):
        """
        对祈愿历史记录排序。

        :param key: 排序依据。
        :param reverse: 是否倒序排列。
        """
        self._records.sort(key=key, reverse=reverse)

    def deduplicate(self):
        """
        使用 ``id`` 字段鉴别重复记录。如果其字段值相同，将会直接判定为重复并清除。
        """
        for i in range(len(self._records) - 1, 0, -1):
            # 注意range的区间是 (0, __len__]
            last_id = self._records[i - 1]['id']
            curr_id = self._records[i]['id']
            if last_id == curr_id:
                self._records.pop(i)

    def maps(self, mapping: Callable):
        """
        更改每一条祈愿历史记录的字段结构。

        :param mapping: 映射函数。其应当有且仅有一个参数和返回值，
                        负责单一一条记录的字段结构更改。
        """
        self._records = list(map(mapping, self._records))

    def pad(self, index: int = -1):
        """
        使用卡池中的某一条祈愿记录填充以下属性：

        - uid
        - region
        - language

        :param index: 所使用的祈愿记录的下标。负数表示倒数第几条。
        """
        try:
            record = self._records[index]
        except IndexError:
            return
        if type(record) is not dict:
            return
        # 如果祈愿记录中没有相应字段，那么不应覆盖原有值：
        if 'uid' in record:
            self.uid = record['uid']
        if 'lang' in record:
            self.language = record['lang']
        if 'region' in record:
            self.region = record['region']

    def has(self, *fields: str) -> bool:
        """
        检测是否所有祈愿记录都拥有指定的字段。

        :param fields: 一个或多个字段的名称。
        :return: 所有祈愿记录都拥有指定的所有字段
                 则为 ``True`` ，否则为 ``False`` 。
        """
        if len(fields) < 1:
            return True
        fs = set(fields)
        return all([
            len(fs - set(record.keys())) == 0
            for record in self._records
        ])

    def dump(
            self, fp: IO = None,
            export_time: datetime = None
    ) -> Optional[dict]:
        """
        将祈愿记录导出为dict，或导出到JSON文件。

        :param fp: 文件对象。
        :param export_time: 导出时间。默认为此时此刻。
        :return: None。当不提供fp时返回一个dict。
        """
        export_at = export_time if export_time else datetime.now()
        content = {
            "info": {
                "uid": self.uid,
                "lang": self.language,
                "region": self.region,
                "export_time": export_at.strftime(UNIFORM_TIME_FORMAT),
                "export_timestamp": int(export_at.timestamp()),
                "export_app": UIGF_APP_NAME,
                "export_app_version": UIGF_APP_VERSION,
                "uigf_version": UIGF_VERSION,
            },
            "list": self._records[:],
        }
        if not fp:
            return content
        json.dump(
            content, fp, ensure_ascii=False,
            indent=None, separators=(',', ':')
        )
        return None

    def load(self, fp: IO = None) -> dict:
        """
        从文件中载入祈愿记录。

        :param fp: 包含JSON的文件对象。
        :return: ``info`` 部分。若文件为空或解析失败，将返回空字典。
        :raise UnsupportedJsonStruct:
        """
        try:
            content = json.load(fp)
        except json.decoder.JSONDecodeError:
            # 1、空文件也会引发这个错误。
            # 2、因为self在创建时已经初始化好各个卡池对象，
            #    因此这里可以直接返回空字典，而不进行其它操作。
            return {}

        # 基础检查：
        ot = type(content)
        if ot is not dict:
            raise UnsupportedJsonStruct(0x01, ot)
        surplus = {'info', 'list'} - set(content.keys())
        if len(surplus) > 0:
            raise UnsupportedJsonStruct(0x02, surplus)

        # 反序列化：
        self.uid = content['info'].get('uid', '')
        self.language = content['info'].get('lang', '')
        self.region = content['info'].get('region', '')
        self._records.clear()
        self._records = content.pop('list', [])

        # 返回文件头部信息：
        return content['info']

    def group_by_time(self) -> Dict[str, List[dict]]:
        """将祈愿记录按照 **祈愿时间** 分组。

        请确保所有祈愿记录中都有以下字段：

        - time

        因为一次性祈愿十次所产生的祈愿时间是一样的，
        因而可以通过祈愿时间区分祈愿记录属于十连还是单抽。

        :return: 一个以祈愿时间为键、祈愿记录列表为值的字典。
                 祈愿时间是一个字符串，格式为 “YYYY-mm-dd HH:MM:SS”。
        """
        return classify(self._records, 'time')

    def group_by_day(self) -> Dict[str, List[dict]]:
        """将祈愿记录按照 **祈愿日期** 分组。

        请确保所有祈愿记录中都有以下字段：

        - time

        :return: 一个以祈愿时间为键、祈愿记录列表为值的字典。
                 祈愿日期是一个字符串，格式为 “YYYY-mm-dd”。
        """
        return classify(self._records, ('time', lambda t: t[:10]))

    def group_by_all_type(self) -> dict:
        """将祈愿记录按照角色/武器的类型、星级、名称分组。

        请确保所有祈愿记录中都有以下字段：

        - item_type
        - rank_type
        - name

        :return: {'角色': {'5': {'甘雨': [单条祈愿记录, ...], }}}
        """
        return classify(self._records, 'item_type', 'rank_type', 'name')
