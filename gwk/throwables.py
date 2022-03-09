# -*- coding: utf-8 -*-

__all__ = [
    'GWKException',
    'AuthNotFound',
    'AuthNotAvailable',
    'MergingException',
    'UnsupportedJsonStruct',
    'RawRespDecodeError',
    'RawRespTypeError',
]


class GWKException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class AuthNotFound(GWKException):
    def __init__(self):
        super().__init__(
            '在日志文件中找不到鉴权信息。请尝试进入原神，'
            '打开祈愿面板，然后点击左下角的 “历史” 浏览一下。'
        )


class AuthNotAvailable(GWKException):
    def __init__(self, context: str):
        super().__init__('测试失败，鉴权信息不可用。' + context)


class MergingException(GWKException):
    def __init__(self, attr: str, one: str, another: str, cls: str):
        super().__init__(
            f'不能合并 {attr} 分别为 {one} 与 {another} 的两个 {cls}。'
        )


class UnsupportedJsonStruct(GWKException):
    def __init__(self, err, context):
        try:
            super().__init__(
                {
                    0x01: ('仅支持导入导出 dict 类型的JSON文件，'
                           '而当前的类型是 ' + context.__name__),
                    0x02: ('导入的JSON文件缺少字段：'
                           + '、'.join(context)),
                    0x03: '不能解析WishType为 %s 的祈愿卡池。' % context
                }[err]
            )
        except KeyError:
            super().__init__('[ERROR] 参数错误。')


class RawRespDecodeError(Exception):
    def __str__(self):
        return '原始响应解码失败，因为它不是一份合法的JSON字符串。'


class RawRespTypeError(Exception):
    def __str__(self):
        return '原始响应缺少以下字段：' + self.args[0]
