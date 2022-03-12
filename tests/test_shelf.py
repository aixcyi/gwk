from datetime import datetime
from random import random
from time import sleep

from gwk.constants import WishType
from gwk.records.excel import save_as_uigf
from gwk.records.models import PlayerShelf
from gwk.records.raw import RawCollector
from gwk.utils import (
    extract_auths,
    get_logfile,
    map_raw_to_uigf_j2
)


def log(text):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f'[{time}] {text}')


def page_callback(
        gacha_type: WishType,
        size: int,
        page: int,
        end_id: str,
):
    """祈愿记录获取回调。"""
    _ = size, end_id
    log(f'{gacha_type.label}: 第{page}页获取完毕。')
    sleep(random())


def main():
    branch = PlayerShelf()
    master = PlayerShelf(
        merge_uid=True, merge_lang=True, merge_region=True
    )

    log('正在读取本地日志……')
    collector = RawCollector(auths=extract_auths(get_logfile()))

    log('正在测试日志中的鉴权信息……')
    collector.available()

    for wish_type in WishType:
        branch[wish_type] += collector.get_wish(
            wish_type, page_callback
        )
        log('----------------')
    branch.pad()

    for wish_type in WishType:
        branch[wish_type].maps(map_raw_to_uigf_j2)

    log('正在导出当次获取……')
    export = datetime.now()
    path_b = export.strftime(
        f'./rs_{branch.uid}_%Y%m%d_%H%M%S.json'
    )
    with open(path_b, 'w', encoding='UTF-8') as f:
        branch.dump(f, export)

    log('正在合并汇总……')
    path_m = f'./rs_{branch.uid}.json'
    with open(path_m, 'a+', encoding='UTF-8') as f:
        master.load(f)
        master.pad()
    master += branch

    log('导出合并汇总结果……')
    with open(path_m, 'w', encoding='UTF-8') as f:
        master.dump(f)

    log('导出Excel表格……')
    path_x = f'./rs_{branch.uid}.xlsx'
    if not save_as_uigf(master, path_x):
        log('警告: Excel表格导出失败')

    log('完毕。')


if __name__ == '__main__':
    main()
    # a_list = [
    #     {"姓名": "陆六", "性别": "男", "生日": "2000-01-11", "部门": "事业部", "……": "……"},
    #     {"姓名": "张三", "性别": "男", "生日": "1999-01-01", "部门": "工程部", "……": "……"},
    #     {"姓名": "李四", "性别": "男", "生日": "1999-12-31", "部门": "工程部", "……": "……"},
    #     {"姓名": "王五", "性别": "男", "生日": "2000-11-01", "部门": "工程部", "……": "……"},
    #     {"姓名": "柒七", "性别": "女", "生日": "1999-07-18", "部门": "事业部", "……": "……"}
    # ]
    # print(classify(a_list, '性别', ('生日', lambda day: day[:4]), '部门'))
