# -*- coding: utf-8 -*-

__all__ = [
    'save_as_uigf',
]

from xlsxwriter import Workbook

from gwk.constants import WishType, GachaType
from gwk.records.models import Player


def save_as_uigf(
        player: Player,
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

    :param player: PlayerShelf类或衍生类的实例。
    :param file_path: xlsx文件地址。
    :param font_name: 所用字体的名称。
    :return: 返回 ``True`` 表示导出完毕，否则表示未能导出。
    """
    if (not isinstance(player, Player)) \
            or (not player.nonempty()):
        return False
    book = Workbook(filename=file_path)
    configs = [
        {'width': (0, 0, 24), 'en': 'Time', 'cn': '时间'},
        {'width': (1, 1, 14), 'en': 'Item', 'cn': '名称'},
        {'width': (2, 2, 7), 'en': 'Type', 'cn': '类别'},
        {'width': (3, 3, 7), 'en': 'Rank', 'cn': '星级'},
        {'width': (4, 4, 24), 'en': 'Wish', 'cn': '祈愿卡池'},
        {'width': (5, 5, 9), 'en': 'No. ', 'cn': '总第几抽'},
        {'width': (6, 6, 14), 'en': '[No.]', 'cn': '保底内第几抽'},
    ]
    is_sc = any([
        str(player.language).lower() == lang
        for lang in ['cn', 'zh-cn', 'zh-tw']
    ])
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
    for wt in WishType:
        # 按卡池创建表：
        sheet = book.add_worksheet(wt.label)

        # 设置样式：
        sheet.freeze_panes(1, 0)  # 冻结首行
        sheet.write_row(
            row=0, col=0, cell_format=style_head,
            data=[
                config['cn'] if is_sc else config['en']
                for config in configs
            ]
        )
        for config in configs:
            sheet.set_column(*config['width'])

        # 写入祈愿记录：
        row = 0  # 总计祈愿多少次
        counter = 0  # 距离上次抽出五星角色/武器多少次（从1开始算）
        for record in player[wt]:
            row += 1
            counter += 1
            sheet.write_row(
                row=row, col=0,
                data=[
                    record['time'], record['name'],
                    record['item_type'], int(record['rank_type']),
                    GachaType(record['gacha_type']).label,
                    row, counter
                ],
                cell_format={
                    '3': style_rank3,
                    '4': style_rank4,
                    '5': style_rank5,
                }[record['rank_type']]
            )
    book.close()
    return True
