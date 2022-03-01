# -*- coding: utf-8 -*-

__all__ = [
    'Wish',
    'Player',
    'map_raw_to_uigf_j2',
    'map_raw_to_basic',
]

import abc
import json
from datetime import datetime, timedelta
from typing import Callable, Union, IO

from gwk.constants import *
from gwk.throwables import (
    MultiPlayerException, MultiRegionException
)


def map_raw_to_uigf_j2(record: dict) -> dict:
    del record['uid']
    del record['lang']
    record['uigf_gacha_type'] = {
        '100': WishType.BEGINNERS_WISH,
        '200': WishType.WANDERLUST_INVOCATION,
        '301': WishType.CHARACTER_EVENT_WISH,
        '302': WishType.WEAPON_EVENT_WISH,
        '400': WishType.CHARACTER_EVENT_WISH,
    }[record['gacha_type']].value
    return record


def map_raw_to_basic(record: dict) -> dict:
    del record['uid']
    del record['gacha_type']
    del record['item_id']
    del record['count']
    del record['lang']
    return record


def map_fix_time(record: dict) -> dict:
    """
    【映射函数】为祈愿记录添加 ``time`` 字段（祈愿时间）。

    - 添加的祈愿时间不一定为精确值。
    - 使用此函数前需要确保祈愿记录拥有 ``id`` 字段。
    - 已有的 ``time`` 字段值将会被覆盖。
    """
    dt_obj = datetime.fromtimestamp(int(record['id'][:10]))
    record['time'] = dt_obj.strftime(UNIFORM_TIME_FORMAT)
    return record


class Wish(list):
    """
    单个祈愿卡池。
    """

    def __init__(self, wish_type: WishType = None):
        super().__init__()

        self.wish_type = wish_type
        """祈愿卡池类型。"""

        self.CEILING = CEILINGS[wish_type]
        """祈愿保底次数（抽出五星金色品质的最大抽取次数）。"""

    def __repr__(self) -> str:
        if self.wish_type:
            return '<Wish(%s) %s，记录数量：%d，语言文字：%s>' % (
                self.wish_type, self.wish_type.label,
                len(self), self.language,
            )
        else:
            return '<Wish(*) 记录数量：%d，语言文字：%s>' % (
                len(self), self.language,
            )

    def __eq__(self, o) -> bool:
        if type(o) is not self.__class__:
            return False
        return o.wish_type == self.wish_type

    @property
    def uid(self) -> str:
        """玩家在原神中的账号号码。"""
        return self._uid_ if hasattr(self, '_uid_') else ''

    @property
    def language(self) -> str:
        """祈愿历史记录的语言文字。"""
        return self._lang_ if hasattr(self, '_lang_') else ''

    def sort(self, key=lambda r: (r['time'], r['id']), reverse: bool = False):
        """
        对祈愿历史记录排序，然后去除重复项。

        - 使用 ``id`` 字段鉴别重复记录。如果其字段值相同，将会直接判定为重复并清除。
        - 默认的排序依据为 ``time``、``id`` 两个字段。

        :param key: 排序依据。
        :param reverse: 是否倒序排列。
        """
        super().sort(key=key, reverse=reverse)
        for i in range(len(self) - 1, 0, -1):
            # 注意range的区间是 (0, __len__]
            if self[i]['id'] == self[i - 1]['id']:
                self.pop(i)

    def maps(self, mapping: Callable):
        """
        更改每一条祈愿历史记录的字段结构。

        :param mapping: 映射函数。其应当有且仅有一个参数和返回值，负责单一一条记录的字段结构更改。
        """
        records = list(map(mapping, self))
        self.clear()
        self.insert(0, records)

    def touch(self):
        """
        根据祈愿记录获取相关信息，并填充到以下属性：

        - ``self.uid``
        - ``self.language``
        """
        try:
            self._uid_ = self[0]['uid']
            self._lang_ = self[0]['lang']
        except (IndexError, KeyError):
            pass


class _WishesStruct:
    def __init__(self, string: bool = False):
        if string:
            self.wish = Wish()
            """所有祈愿记录。"""

            self._list = [self.wish]
        else:
            self.beginner = Wish(WishType.BEGINNERS_WISH)
            """新手祈愿卡池。"""

            self.wanderlust = Wish(WishType.WANDERLUST_INVOCATION)
            """常驻祈愿卡池。"""

            self.character = Wish(WishType.CHARACTER_EVENT_WISH)
            """角色祈愿卡池、角色祈愿-2卡池。"""

            self.weapon = Wish(WishType.WEAPON_EVENT_WISH)
            """武器祈愿卡池。"""

            self._list = [
                self.beginner, self.wanderlust,
                self.character, self.weapon,
            ]

    def __iter__(self):
        return self._list

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index) -> Wish:
        return self._list[index]


class Player(abc.ABC):
    """面向单个玩家的祈愿记录操作类。"""

    @staticmethod
    def earliest(fmt: str = '%Y-%m-%d') -> Union[str, datetime]:
        """
        原神只能获取最近六个月的祈愿历史记录。
        此方法用于计算最早可以获取到哪天的祈愿记录。

        :param fmt: 日期时间的字符串格式。若为None，则直接返回datetime对象。
        :return: 返回一个datetime或str，表示可能获取到的最早的记录的日期。
        """
        time = datetime.now() - timedelta(days=6 * 30 - 1)
        return time.strftime(fmt) if fmt else time

    def __init__(
            self,
            uid: str = '',
            lang: str = 'zh-cn',
            region: str = '',
            multi_uid: bool = False,
            multi_region: bool = False,
    ):
        """
        :param uid: 玩家在原神中的账号号码，或自定义的唯一标识符。空字符串也作为一种标识符。
        :param lang: 祈愿记录的语言文字。默认为``zh-cn``。
        :param region: 游戏客户端所在地区。空字符串也作为一个独立地区。
        :param multi_uid: 是否允许合并不同玩家的祈愿记录。
        :param multi_region: 是否允许合并不同地区的祈愿记录。
        """
        self.uid = uid
        self.region = region
        self.language = lang
        self.multi_uid = multi_uid
        self.multi_region = multi_region

    def __iadd__(self, other):
        ot = type(other)
        if ot is not self.__class__:
            raise TypeError(
                '仅支持与 %s 类型相加，而提供的是 %s' % (
                    self.__class__.__name__, ot.__name__,
                )
            )
        if self.uid != other.uid:
            if self.multi_uid is False:
                raise MultiPlayerException(self.uid, other.uid)
            self.uid = other.uid
        if self.region != other.region:
            if self.multi_region is False:
                raise MultiRegionException(self.region, other.region)
            self.region = other.region
        return self

    @abc.abstractmethod
    def __bool__(self) -> bool:
        pass

    @abc.abstractmethod
    def nonempty(self) -> bool:
        pass

    @abc.abstractmethod
    def dump(self, fp: IO = None):
        pass

    @abc.abstractmethod
    def load(self, fp: IO = None):
        pass


class PlayerPool(Player):
    """面向单个玩家的单卡池祈愿记录操作类。"""

    wishes = _WishesStruct(True)

    def __iadd__(self, other):
        super(PlayerPool, self).__iadd__(other)
        if not other.nonempty():
            return self
        self.wishes[0] += other.wishes[0]
        self.wishes[0].touch()
        return self

    def nonempty(self) -> bool:
        """但凡有一条祈愿记录都会返回``True``，否则返回``False``。"""
        return len(self.wishes[0]) > 0

    __bool__ = nonempty

    def dump(self, fp: IO = None):
        """
        将所有卡池的祈愿记录导出为dict，或导出到JSON文件。

        :param fp: 文件对象。
        :return: 当不提供fp时返回一个dict，其余时候不返回。
        """
        from gwk import UIGF_APP_NAME, UIGF_APP_VERSION, UIGF_VERSION

        export_at = datetime.now()
        content = {
            "info": {
                "uid": self.uid,
                "lang": self.language,
                "export_time": export_at.strftime(UNIFORM_TIME_FORMAT),
                "export_timestamp": export_at.timestamp(),
                "export_app": UIGF_APP_NAME,
                "export_app_version": UIGF_APP_VERSION,
                "uigf_version": UIGF_VERSION,
            },
            "records": {
                wish.wish_type: list(wish) for wish in self.wishes
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
        # TODO: 载入单卡池祈愿记录
        return None


class PlayerShelf(Player):
    """面向单个玩家的多卡池祈愿记录操作类。"""

    wishes = _WishesStruct(False)

    def __iadd__(self, other):
        super(PlayerShelf, self).__iadd__(other)
        if not other.nonempty():
            return self
        for i in range(len(self.wishes)):
            self.wishes[i] += other.wishes[i]
            self.wishes[i].touch()
        return self

    def nonempty(self) -> bool:
        """但凡有一条祈愿记录都会返回``True``，否则返回``False``。"""
        return any([len(wish) for wish in self.wishes])

    __bool__ = nonempty

    def dump(self, fp: IO = None):
        """
        将所有卡池的祈愿记录导出为dict，或导出到JSON文件。

        :param fp: 文件对象。
        :return: 当不提供fp时返回一个dict，其余时候不返回。
        """
        from gwk import UIGF_APP_NAME, UIGF_APP_VERSION, UIGF_VERSION

        export_at = datetime.now()
        content = {
            "info": {
                "uid": self.uid,
                "lang": self.language,
                "export_time": export_at.strftime(UNIFORM_TIME_FORMAT),
                "export_timestamp": export_at.timestamp(),
                "export_app": UIGF_APP_NAME,
                "export_app_version": UIGF_APP_VERSION,
                "uigf_version": UIGF_VERSION,
            },
        }
        for wish in self.wishes:
            content['list'] += list(wish)
        if not fp:
            return content
        json.dump(
            content, fp, ensure_ascii=False,
            indent=None, separators=(',', ':')
        )
        return None

    def load(self, fp: IO = None):
        # TODO: 载入多卡池祈愿记录
        pass
