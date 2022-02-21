# -*- coding: utf-8 -*-

class GWorkException(Exception):
    def __init__(self, message: str):
        self.message = message


class LogfileNotFound(GWorkException):
    def __init__(self, file: str):
        super('找不到原神客户端日志文件。' + file)


class AuthNotFound(GWorkException):
    def __init__(self):
        super(
            '在日志文件中找不到鉴权信息。'
            '请尝试进入原神，打开祈愿面板，然后点击左下角的 “历史” 浏览一下。'
        )


class AuthNotAvailable(GWorkException):
    def __init__(self, context: str):
        super('鉴权测试失败。' + context)


class RawRespDecodeError(Exception):
    def __str__(self):
        return '原始响应解码失败，因为它不是一份合法的JSON字符串。'


class RawRespTypeError(Exception):
    def __str__(self):
        return '原始响应缺少以下字段：' + self.args[0]
