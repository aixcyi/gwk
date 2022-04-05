# -*- coding: utf-8 -*-

from typing import Any

from requests import Response

from gwk.throwables import RawRespDecodeError, RawRespTypeError


class GenshinResponse:
    """
    原神HTTP响应的包装类。
    """

    def __init__(self, resp: Response):
        try:
            content: dict = resp.json()
            self.retcode: int = content['retcode']
            self.message: str = content['message']
            self.data: Any = content['data']
        except ValueError as e:
            raise RawRespDecodeError() from e
        except KeyError as e:
            raise RawRespTypeError(e.args[0]) from e
