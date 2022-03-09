# -*- coding: utf-8 -*-

__all__ = [
    'Wish',
    'PlayerPool',
    'PlayerShelf',
]

import json
from datetime import datetime
from typing import Callable, Union, IO, Optional, Dict

from gwk import UIGF_APP_NAME, UIGF_APP_VERSION, UIGF_VERSION
from gwk.constants import *
from gwk.throwables import *
from gwk.utils import TNF


class Wish:

    def __init__(self, wish_type: WishType = None):
        """
        祈愿卡池。包含单个祈愿卡池的所有祈愿记录。

        :param wish_type: 卡池类型。
        """
        self._records = list()
        assert type(wish_type) in (WishType, None), \
            '不应该使用除 WishType 和 None 以外的类型来初始化 Wish 。'

        self.wish_type = wish_type
        """祈愿卡池类型。"""

        self.CEILING = CEILINGS[wish_type] if wish_type else 0
        """祈愿保底次数（抽出五星金色品质的最大抽取次数）。"""

        self.uid = ''
        """玩家在原神中的账号号码。"""

        self.language = ''
        """祈愿历史记录的语言文字。"""

        self.region = ''
        """游戏客户端所在地区。"""

    def __repr__(self) -> str:
        if self.wish_type:
            return '<Wish(%s) %s，记录数量：%d，语言文字：%s>' % (
                self.wish_type, self.wish_type.label,
                len(self._records), self.language,
            )
        else:
            return '<Wish(*) 记录数量：%d，语言文字：%s>' % (
                len(self._records), self.language,
            )

    def __eq__(self, o) -> bool:
        if type(o) is not self.__class__:
            return False
        return o.wish_type == self.wish_type

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, k):
        assert isinstance(k, (int, slice)), '仅支持整数索引或切片访问。'
        return self._records[k]

    def __iadd__(self, o):
        if not isinstance(o, (list, tuple, self.__class__)):
            raise TypeError(
                f'Wish 不能与 {type(o).__name__} 类型相加。'
            )
        if isinstance(o, (list, tuple)):
            self._records += o
            return self

        if self.wish_type is not None:
            if o.wish_type != self.wish_type:
                raise TypeError(
                    f'{o.wish_type!s} 类型的 Wish 不能与 '
                    f'{self.wish_type!s} 类型的相加。'
                )
        self.uid = o.uid
        self.region = o.region
        self.language = o.language
        self._records += o[:]
        return self

    def set(self, records: Union[list, tuple]):
        """
        用一份新的祈愿记录覆盖到祈愿卡池中。
        注意：此方法不会检验卡池的祈愿类型跟记录是否匹配。
        """
        if not isinstance(records, (list, tuple)):
            return None
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
        对祈愿历史记录排序，然后去除重复项。

        - 使用 ``id`` 字段鉴别重复记录。如果其字段值相同，将会直接判定为重复并清除。
        - 默认的排序依据为 ``time``、``id`` 两个字段。

        :param key: 排序依据。
        :param reverse: 是否倒序排列。
        """
        self._records.sort(key=key, reverse=reverse)
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


def _check_tnf(obj, attr: str, new_value):
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


class PlayerPool:
    def __init__(
            self,
            uid: str = '',
            lang: str = 'zh-cn',
            region: str = '',
            merge_uid: TNF = False,
            merge_region: TNF = False,
            merge_lang: TNF = True,
    ):
        """
        面向单个玩家的祈愿记录操作类。内部使用单个卡池统一存储祈愿记录。

        :param uid: 玩家在原神中的账号号码，或自定义的唯一标识符。
                    空字符串也作为一种标识符。
        :param lang: 祈愿记录的语言文字。默认为``zh-cn``。
        :param region: 游戏客户端所在地区。空字符串也作为一个独立地区。
        :param merge_uid: 是否允许合并不同玩家的祈愿记录。遵循TNF策略。
        :param merge_region: 是否允许合并不同地区的祈愿记录。遵循TNF策略。
        :param merge_lang: 是否允许合并不同文字的祈愿记录。遵循TNF策略。
        """
        self.uid = uid
        self.region = region
        self.language = lang
        self.merge_uid = merge_uid
        self.merge_region = merge_region
        self.merge_language = merge_lang

        self.wish = Wish()
        """所有祈愿记录。"""

    def __iadd__(self, o):
        if not isinstance(o, self.__class__):
            raise TypeError(
                f'{type(o).__class__.__name__}'
                ' 类型不能与 PlayerPool 相加。'
            )
        _check_tnf(self, 'uid', o.uid)
        _check_tnf(self, 'region', o.region)
        _check_tnf(self, 'language', o.language)
        self.wish += o.wish
        return self

    def nonempty(self) -> bool:
        """但凡有一条祈愿记录都会返回``True``，否则返回``False``。"""
        return len(self.wish) > 0

    __bool__ = nonempty

    def dump(self, fp: IO = None) -> Optional[dict]:
        """
        将所有卡池的祈愿记录导出为dict，或导出到JSON文件。

        :param fp: 文件对象。
        :return: 当不提供fp时返回一个dict，其余时候不返回。
        """
        export_at = datetime.now()
        content = {
            "info": {
                "uid": self.uid,
                "lang": self.language,
                "export_time": export_at.strftime(UNIFORM_TIME_FORMAT),
                "export_timestamp": int(export_at.timestamp()),
                "export_app": UIGF_APP_NAME,
                "export_app_version": UIGF_APP_VERSION,
                "uigf_version": UIGF_VERSION,
            },
            "list": self.wish[:],
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
        :return: ``info`` 部分。
        :raise UnsupportedJsonStruct:
        """
        # 从文件载入并进行基础检查：
        content = json.load(fp)
        ot = type(content)
        if ot is not dict:
            raise UnsupportedJsonStruct(0x01, ot)
        surplus = {'info', 'list'} - set(content.keys())
        if len(surplus) > 0:
            raise UnsupportedJsonStruct(0x02, surplus)

        # 反序列化：
        self.uid = content['info'].get('uid', '')
        self.language = content['info'].get('lang', '')
        self.wish.clear()
        self.wish += content.pop('list', [])

        # 返回文件头部信息：
        return content['info']

    def pad(self):
        """
        使用祈愿卡池中的信息填充以下属性：

        - uid
        - region
        - language
        """
        self.uid = self.wish.uid
        self.region = self.wish.region
        self.language = self.wish.language


class PlayerShelf:
    def __init__(
            self,
            uid: str = '',
            lang: str = 'zh-cn',
            region: str = '',
            merge_uid: bool = False,
            merge_region: bool = False,
            merge_lang: bool = True,
    ):
        """
        面向单个玩家的祈愿记录操作类。内部使用多个卡池分别存储祈愿记录。

        :param uid: 玩家在原神中的账号号码，或自定义的唯一标识符。
                    空字符串也作为一种标识符。
        :param lang: 祈愿记录的语言文字。默认为``zh-cn``。
        :param region: 游戏客户端所在地区。空字符串也作为一个独立地区。
        :param merge_uid: 是否允许合并不同玩家的祈愿记录。遵循TNF策略。
        :param merge_region: 是否允许合并不同地区的祈愿记录。遵循TNF策略。
        :param merge_lang: 是否允许合并不同文字的祈愿记录。遵循TNF策略。
        """
        self.uid = uid
        self.region = region
        self.language = lang
        self.merge_uid = merge_uid
        self.merge_region = merge_region
        self.merge_language = merge_lang

        self.beginner_wish = Wish(WishType.BEGINNERS_WISH)
        """新手祈愿卡池。"""

        self.wanderlust_inv = Wish(WishType.WANDERLUST_INVOCATION)
        """常驻祈愿卡池。"""

        self.character_wish = Wish(WishType.CHARACTER_EVENT_WISH)
        """角色祈愿卡池、角色祈愿-2卡池。"""

        self.weapon_wish = Wish(WishType.WEAPON_EVENT_WISH)
        """武器祈愿卡池。"""

        self._wishes: Dict[WishType, Wish] = {
            wish.wish_type: wish for wish in [
                self.beginner_wish, self.wanderlust_inv,
                self.character_wish, self.weapon_wish,
            ]
        }

    def __iadd__(self, o):
        if not isinstance(o, self.__class__):
            raise TypeError(
                f'{type(o).__class__.__name__}'
                ' 类型不能与 PlayerShelf 相加。'
            )
        _check_tnf(self, 'uid', o.uid)
        _check_tnf(self, 'region', o.region)
        _check_tnf(self, 'language', o.language)
        self.beginner_wish += o.beginner_wish
        self.wanderlust_inv += o.wanderlust_inv
        self.character_wish += o.character_wish
        self.weapon_wish += o.weapon_wish
        return self

    def __iter__(self):
        """
        实现允许使用 for 循环遍历所有卡池。

        >>> shelf = PlayerShelf()
        >>> for key in shelf:
        >>>     wish_type: WishType = key
        >>>     wish_obj: Wish = shelf[key]
        """
        return iter(self._wishes)

    def __getitem__(self, key: Union[WishType, str, int]):
        """
        实现允许使用 WishType 取出卡池对象。

        >>> shelf = PlayerShelf()
        >>> wish: Wish = shelf[WishType.BEGINNERS_WISH]
        """
        try:
            if key in self._wishes:
                return self._wishes[key]
            k = WishType(str(key))
            if k in self._wishes:
                return self._wishes[k]
        except ValueError:
            pass
        raise KeyError(key)

    def nonempty(self) -> bool:
        """但凡有一条祈愿记录都会返回``True``，否则返回``False``。"""
        return any([
            len(self._wishes[k]) for k in self._wishes
        ])

    __bool__ = nonempty

    def dump(self, fp: IO = None) -> Optional[dict]:
        """
        将所有卡池的祈愿记录导出为dict，或导出到JSON文件。

        :param fp: 文件对象。
        :return: 当不提供fp时返回一个dict，其余时候不返回。
        """
        export_at = datetime.now()
        content = {
            "info": {
                "uid": self.uid,
                "lang": self.language,
                "export_time": export_at.strftime(UNIFORM_TIME_FORMAT),
                "export_timestamp": int(export_at.timestamp()),
                "export_app": UIGF_APP_NAME,
                "export_app_version": UIGF_APP_VERSION,
                "uigf_version": UIGF_VERSION,
            },
            "records": {
                k.value: self._wishes[k][:]
                for k in self._wishes
            }
        }
        if not fp:
            return content
        json.dump(
            content, fp, ensure_ascii=False,
            indent=None, separators=(',', ':')
        )
        return None

    def load(self, fp: IO = None):
        """
        从文件中载入祈愿记录。

        :param fp: 包含JSON的文件对象。
        :return: 以字典形式返回没有被存入对象的信息。比如导出时间。
        """
        # 从文件载入并进行基础检查：
        content = json.load(fp)
        ot = type(content)
        if ot is not dict:
            raise UnsupportedJsonStruct(0x01, ot)
        surplus = {'info', 'records'} - set(content.keys())
        if len(surplus) > 0:
            raise UnsupportedJsonStruct(0x02, surplus)

        # 反序列化：
        self.uid = content['info']['uid']
        self.language = content['info']['lang']
        try:
            for w in content['records']:
                wish_type = WishType(w)
                self._wishes[wish_type].set(
                    content['records'][w]
                )
        except ValueError as e:
            # e.args == ('300 is not a valid Type',)
            # rpartition是为了预防value有空格的情况
            raise UnsupportedJsonStruct(
                0x03, e.args[0].rpartition(' is ')[0]
            ) from e

        # 返回未被使用的字段：
        return {
            'export_time': datetime.strptime(
                date_string=content['info']['export_time'],
                format=UNIFORM_TIME_FORMAT,
            ),
            'export_timestamp': int(
                content['info']['export_timestamp']
            )
        }
