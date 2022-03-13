from datetime import datetime
from random import random
from time import sleep

from gwk.constants import WishType
from gwk.records.excel import save_as_uigf
from gwk.records.models import Wish
from gwk.records.raw import RawCollector
from gwk.utils import (
    extract_auths,
    get_logfile,
    map_raw_to_uigf_j2,
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
    branch = Wish()  # 当次获取的祈愿记录（仅能获取半年内的）
    master = Wish()  # 本地原有的完整祈愿记录
    master.merge_uid = True
    master.merge_lang = True
    master.merge_region = True

    log('正在读取本地的客户端日志……')
    collector = RawCollector(auths=extract_auths(get_logfile()))

    log('正在测试鉴权信息……')
    collector.available()

    # 获取各个卡池的祈愿记录：
    for wish_type in WishType:
        branch += collector.get_wish(wish_type, page_callback)
        log('----------------')
    # 先从祈愿记录获取uid等信息，再转换每条记录的格式，
    # 否则可能会获取不到需要的信息。
    branch.pad()
    branch.maps(map_raw_to_uigf_j2)

    log('正在导出当次获取……')
    export = datetime.now()
    path_b = export.strftime(
        f'./uigf_{branch.uid}_%Y%m%d_%H%M%S.json'
    )
    with open(path_b, 'w', encoding='UTF-8') as f:
        branch.dump(f, export)

    # 因为当次只能获取最近半年内的祈愿记录，是不完整的，
    # 因而需要合并本地留存的祈愿记录，形成一份完整的祈愿历史记录。
    log('正在合并汇总……')
    path_m = f'./uigf_{branch.uid}.json'
    with open(path_m, 'a+', encoding='UTF-8') as f:
        master.load(f)
        master.pad()
    master += branch
    branch.sort()

    log('正在导出合并汇总结果……')
    with open(path_m, 'w', encoding='UTF-8') as f:
        master.dump(f)

    # if master.has('uigf_gacha_type'):
    #     log('正在导出Excel表格……')
    #     shelf = player_to_shelf(master, lambda r: WishType(r['uigf_gacha_type']))
    #     path_x = f'./uigf_{branch.uid}.xlsx'
    #     if not save_as_uigf(shelf, path_x):
    #         log('警告: Excel表格导出失败')

    log('完毕。')


if __name__ == '__main__':
    main()
