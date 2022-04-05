# -*- coding: utf-8 -*-

from urllib.parse import parse_qs, urlparse

from gwk.throwables import AuthNotFound
from gwk.typing import Path


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


def extract_auths(
        logfile: str,
        encoding: str = 'UTF-8'
) -> dict:
    """
    从文件中提取鉴权信息。

    :param logfile: 原神客户端日志文件的地址。
    :param encoding: 文件编码。默认为 UTF-8。
    :return: 以字典形式存放的鉴权信息。
    :raise AuthNotFound: 找不到鉴权信息。
    """
    with open(logfile, 'r', encoding=encoding) as f:
        lines = f.readlines()[::-1]

    line_prefix = 'OnGetWebViewPageFinish:'
    for line in lines:
        if line.startswith(line_prefix):
            url = line[len(line_prefix):]
            break
    else:
        raise AuthNotFound()
    return parse_qs(urlparse(url).query)
