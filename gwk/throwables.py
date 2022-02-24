# -*- coding: utf-8 -*-

class GWKException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class LogfileNotFound(GWKException):
    def __init__(self, file: str):
        super().__init__('找不到原神客户端日志文件。' + file)


class AuthNotFound(GWKException):
    def __init__(self):
        super().__init__(
            '在日志文件中找不到鉴权信息。'
            '请尝试进入原神，打开祈愿面板，然后点击左下角的 “历史” 浏览一下。'
        )


class AuthNotAvailable(GWKException):
    def __init__(self, context: str):
        super().__init__('测试失败，鉴权信息不可用。' + context)


class MultiPlayerException(GWKException):
    def __init__(self, uid_master: str, uid_other: str):
        super().__init__(
            f'如需合并uid为 {uid_master} 与 {uid_other} 的两份祈愿记录，'
            '请将 multi_uid 设为 True 。'
        )


class MultiRegionException(GWKException):
    def __init__(self, region_master: str, region_other: str):
        super().__init__(
            f'如需合并地区为 {region_master} 与 {region_other} 的两份祈愿记录，'
            '请将 multi_region 设为 True 。'
        )


class RawRespDecodeError(Exception):
    def __str__(self):
        return '原始响应解码失败，因为它不是一份合法的JSON字符串。'


class RawRespTypeError(Exception):
    def __str__(self):
        return '原始响应缺少以下字段：' + self.args[0]
