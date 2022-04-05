# -*- coding: utf-8 -*-

import json
from typing import IO

from xlsxwriter import Workbook

from gwk.constants import WishType, GachaType
from gwk.models import Wish
from gwk.utils import classify


def migrate(fp: IO) -> Wish:
    """
    将旧项目导出的JSON文件转换为 Wish 。

    [genshin-gacha-kit](https://github.com/aixcyi/genshin-gacha-kit)

    :param fp:
    :return:
    """
    content = json.load(fp)
    wish = Wish()

    if type(content) is not dict:
        raise TypeError('文件格式不正确。')

    if 'infos' not in content or type(content['infos']) is not dict:
        raise TypeError('文件格式不正确。')
    wish.uid = content['infos'].get('uid', '')
    wish.region = content['infos'].get('region', '')
    wish.language = content['infos'].get('lang', '')

    def mapping(r) -> dict:
        r['gacha_type'] = w
        r['item_id'] = ''
        r['count'] = '1'
        r['uigf_gacha_type'] = w
        return r

    if 'records' not in content and type(content['records']) is not dict:
        raise TypeError('文件格式不正确。')
    for w in content['records']:
        wish += list(map(mapping, content['records'][w]))
    wish.sort(key=lambda r: (r['uigf_gacha_type'], r['time'], r['id']))

    return wish


def save_as_uigf(
        wish: Wish,
        file_path: str,
        font_name: str = '微软雅黑'
):
    """
    将祈愿记录数据加工存储为带有颜色标记的xlsx文件。

    所存储的信息有：

    - 祈愿时间
    - 角色/武器的名称
    - 类别（角色还是武器）
    - 角色/武器的星级
    - 祈愿所在卡池的名称
    - 总第几次祈愿
    - 保底内第几次祈愿

    :param wish: PlayerShelf类或衍生类的实例。
    :param file_path: xlsx文件地址。
    :param font_name: 所用字体的名称。
    :return: 返回 ``True`` 表示导出完毕，否则表示未能导出。
    """
    if (not isinstance(wish, Wish)) or (not wish.nonempty()):
        return False
    book = Workbook(filename=file_path)
    columns = [
        {'width': (0, 0, 24), 'en': 'Time', 'cn': '时间'},
        {'width': (1, 1, 14), 'en': 'Item', 'cn': '名称'},
        {'width': (2, 2, 7), 'en': 'Type', 'cn': '类别'},
        {'width': (3, 3, 7), 'en': 'Rank', 'cn': '星级'},
        {'width': (4, 4, 16), 'en': 'Wish', 'cn': '祈愿卡池'},
        {'width': (5, 5, 9), 'en': 'No. ', 'cn': '总第几抽'},
        {'width': (6, 6, 14), 'en': '[No.]', 'cn': '保底内第几抽'},
    ]
    if str(wish.language).lower() in ('cn', 'zh-cn', 'zh-tw'):
        lang = 'cn'
    else:
        lang = 'en'
    style_head = book.add_format({  # 表格头部
        "align": "left",
        "font_name": font_name,
        "bg_color": "#dbd7d3",
        "border_color": "#c4c2bf",
        "border": 1,
        "color": "#757575",
        "bold": True
    })
    style_rank3 = book.add_format({  # 行内容样式-三星
        "align": "left",
        "font_name": font_name,
        "bg_color": "#ebebeb",
        "border_color": "#c4c2bf",
        "border": 1,
        "color": "#8e8e8e"
    })
    style_rank4 = book.add_format({  # 行内容样式-四星
        "align": "left",
        "font_name": font_name,
        "bg_color": "#ebebeb",
        "border_color": "#c4c2bf",
        "border": 1,
        "color": "#a256e1",
        "bold": True
    })
    style_rank5 = book.add_format({  # 行内容样式-五星
        "align": "left",
        "font_name": font_name,
        "bg_color": "#ebebeb",
        "border_color": "#c4c2bf",
        "border": 1,
        "color": "#bd6932",
        "bold": True
    })
    records = classify(wish[:], 'uigf_gacha_type')

    for wt in WishType:
        # 按卡池创建表：
        sheet = book.add_worksheet(wt.label)

        # 设置样式：
        sheet.freeze_panes(1, 0)  # 冻结首行
        sheet.write_row(  # 设置首行的内容（表头）
            row=0, col=0, cell_format=style_head,
            data=[col[lang] for col in columns],
        )
        for config in columns:  # 设置各个列宽：
            sheet.set_column(*config['width'])

        # 写入祈愿记录：
        if wt.value not in records:
            # 有些卡池已经不在了，比如新手祈愿，应当跳过
            continue
        total = 0  # 总计祈愿多少次
        last5 = 0  # 距离上次抽出五星角色/武器多少次（从1开始算）
        for record in records[wt.value]:
            total += 1
            last5 += 1
            sheet.write_row(
                row=total, col=0,
                data=[
                    record['time'], record['name'],
                    record['item_type'], int(record['rank_type']),
                    GachaType(record['gacha_type']).label,
                    total, last5
                ],
                cell_format={
                    '3': style_rank3,
                    '4': style_rank4,
                    '5': style_rank5,
                }[record['rank_type']]
            )
            if record['rank_type'] == '5':
                last5 = 0
    book.close()
    return True
