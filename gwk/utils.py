# -*- coding: utf-8 -*-

__all__ = [
    'Path',
    'URL',
    'get_logfile',
    'extract_auths',
    'fit_id',
    'make_id',
]

from datetime import datetime
from os.path import isfile, expanduser, join
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from gwk.constants import *
from gwk.throwables import LogfileNotFound, AuthNotFound


class Path:
    def __init__(self, root: str = ''):
        self.path = expanduser(root)

    def __truediv__(self, other: str):
        self.path = join(self.path, other)
        return self

    def __str__(self):
        return self.path

    def is_file(self) -> bool:
        return isfile(self.path)


class URL:
    scheme: str = ''  # protocol
    host: str = ''  # domain
    path: str = ''
    params: str = ''
    query: dict = {}
    fragment: str = ''

    def __init__(self, url: str):
        self.scheme, self.host, self.path, self.params, q, f = urlparse(url)
        self.query = parse_qs(q)
        self.fragment = f

    def __str__(self):
        return urlunparse((
            self.scheme, self.host, self.path, self.params,
            urlencode(self.query), self.fragment
        ))


def get_logfile() -> str:
    """
    查找原神客户端日志文件。

    :return: 日志文件地址。找不到则返回空字符串。
    """
    base = Path('~/AppData/LocalLow/miHoYo')
    for folder in ('原神', 'Genshin Impact', 'YuanShen'):
        logfile = base / folder / 'output_log.txt'
        if logfile.is_file():
            return str(logfile)
    return ''


def extract_auths(logfile: str, encoding: str = 'UTF-8') -> dict:
    """
    从文件中提取鉴权信息。

    :param logfile: 原神客户端日志文件的地址。
    :param encoding: 文件编码。默认为 UTF-8。
    :return: 以字典形式存放的鉴权信息。
    """
    try:
        with open(logfile, 'r', encoding=encoding) as f:
            lines = f.readlines()[::-1]
    except FileNotFoundError as e:
        raise LogfileNotFound(e.filename) from e

    line_prefix = 'OnGetWebViewPageFinish:'
    for line in lines:
        if line.startswith(line_prefix):
            url = line[len(line_prefix):]
            break
    else:
        raise AuthNotFound()
    return parse_qs(urlparse(url).query)


def fit_id(time: str, offset: int, uid: int) -> str:
    """
    祈愿历史记录ID拟合函数。（更贴近原始ID）

    :param time: 祈愿时间。字符串格式应为 "yyyy-MM-dd HH:mm:ss"
    :param offset: 偏移量。用于当祈愿时间相同时生成不同的ID，取值范围为0到999,9999。
    :param uid: 玩家账号号码。
    :return: 19位纯数字组成的字符串。
    """
    wish_time = datetime.strptime(time, UNIFORM_TIME_FORMAT)
    tt = list(wish_time.timetuple())
    if wish_time <= DT_STAMP_OFFSET_CHANGE:
        tt[4], tt[5] = 0, 0
    else:
        tt[4], tt[5] = 6, 0
    record_time = datetime(*tt[:6])
    left = str(int(record_time.timestamp())).rjust(10, '0')

    if wish_time >= DT_VERSION_START_2_3:
        offset = offset * 100 + uid % 100
    right = str(offset % 1000000000).rjust(9, '0')

    return left + right


def make_id(time: str, generator: int, player: int, offset: int = 0) -> str:
    """
    高精度祈愿历史记录ID生成函数。（编码空间更大，墙裂推荐）

    :param time: 祈愿时间。字符串格式应为 "yyyy-MM-dd HH:mm:ss"
    :param generator: 生成器标识。用于标记不同应用或中间件生成的ID。取值范围[0,16383]。
    :param player: 玩家标识。用于标记不同玩家。取值范围为[0,4095]。
    :param offset: 偏移量。用于当祈愿时间相同时生成不同的ID，取值范围为[0,15]。
    :return: 19位纯数字组成的字符串。
    """
    wish_time = datetime.strptime(time, UNIFORM_TIME_FORMAT)
    wish_stamp = int(wish_time.timestamp())
    return str(
        (0x7FFFFFFFC0000000 & wish_stamp << 30) +
        (0x000000003FFF0000 & generator << 16) +
        (0x000000000000FFF0 & player << 4) +
        (0x000000000000000F & offset)
    )
