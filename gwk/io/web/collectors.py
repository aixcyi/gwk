# -*- coding: utf-8 -*-

from typing import Callable, Dict, Any

from requests import get as http_get

from gwk.constants import WishType
from gwk.io.web.wraps import GenshinResponse
from gwk.models import Wish
from gwk.throwables import AuthNotAvailable


class RawCollector:
    SIZE_PER_PAGE_MAX = 20
    PAGE_START = 0

    def __init__(self, auths: Dict[str, Any]):
        """
        祈愿历史记录下载类。

        :param auths: 鉴权信息。
        """
        self.url = 'https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog'
        self.query = auths if type(auths) is dict else {}

    def available(self) -> None:
        """
        检测鉴权信息是否可用。

        :raise AuthNotAvailable: 鉴权信息不可用时抛出。
        """
        resp = GenshinResponse(http_get(
            self.url, params=self.query
        ))
        if resp.retcode != 0:
            raise AuthNotAvailable(resp.message)

    def get_page(
            self,
            gacha_type: WishType,
            size: int = SIZE_PER_PAGE_MAX,
            page: int = PAGE_START,
            end_id: str = '0',
            callback: Callable = None
    ) -> dict:
        """
        下载某一卡池的某一页祈愿历史。

        :param gacha_type: 卡池类型。
        :param size: 每一页的祈愿历史数量。
        :param page: 第几页祈愿历史，即页码偏移量。
        :param end_id: 最后一条祈愿历史的ID。初始值为 "0" 。
        :param callback: 回调函数。每下载完一页就会调用一次。
                         一般用于延时和跟踪下载进度。
                         参数声明同本方法（除回调函数参数外）。
        :return: 经过JSON解析的HTTP响应正文，包含当前一页的所有祈愿历史。
        """
        self.query['size'] = str(size)
        self.query['gacha_type'] = gacha_type.value
        self.query['page'] = str(page)
        self.query['end_id'] = end_id
        resp = GenshinResponse(http_get(self.url, self.query))
        if callable(callback):
            callback(gacha_type, size=size,
                     page=page, end_id=end_id)
        return resp.data

    def get_wish(
            self,
            gacha_type: WishType,
            callback: Callable = None
    ) -> Wish:
        """
        下载一个卡池的所有祈愿历史。

        :param gacha_type: 祈愿卡池类型。
        :param callback: 回调函数。每下载完一页就会调用一次。
                         一般用于延时和跟踪下载进度。
                         参数声明见 ``get_page()`` 。
        :return: 包含零条或多条祈愿历史的列表。
        """
        page_offset = 1
        end_id = '0'
        wish = Wish(gacha_type)
        while True:
            page = self.get_page(
                gacha_type, page=page_offset,
                end_id=end_id, callback=callback
            )
            wish.region = page['region']
            if not page['list']:
                break
            wish += page['list']
            wish.language = page['list'][-1]['lang']
            wish.uid = page['list'][-1]['uid']
            end_id = page['list'][-1]['id']
            page_offset += 1
        return wish
