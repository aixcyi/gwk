from datetime import datetime
from random import random
from time import sleep

from gwk.constants import WishType
from gwk.io.local import extract_auths, get_logfile, save_as_uigf
from gwk.io.web import RawCollector
from gwk.models import Wish
from gwk.tools.mappings import map_raw_to_uigf_j2


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
    sleep(random() * 1.414)


def main():
    branch = Wish()  # 当次获取的祈愿记录（仅能获取半年内的）
    master = Wish()  # 本地原有的完整祈愿记录
    master.merging_check = False

    log('正在读取并测试鉴权信息……')
    collector = RawCollector(auths=extract_auths(get_logfile()))
    collector.available()

    # 获取各个卡池的祈愿记录：
    branch.merging_check = False
    for wish_type in WishType:
        branch += collector.get_wish(wish_type, page_callback)
        log('----------------')
    branch.merging_check = True
    # 先从祈愿记录获取uid等信息，再转换每条记录的格式，
    # 否则可能会获取不到需要的信息。
    branch.pad()
    branch.maps(map_raw_to_uigf_j2)

    export = datetime.now()
    path_b = export.strftime(
        f'./records_{branch.uid}_%Y%m%d_%H%M%S.json'
    )
    log('导出文件 ' + path_b)
    with open(path_b, 'w', encoding='UTF-8') as f:
        branch.dump(f, export)

    # 因为当次只能获取最近半年内的祈愿记录，是不完整的，
    # 因而需要合并本地留存的祈愿记录，形成一份完整的祈愿历史记录。
    path_m = f'./records_{branch.uid}.json'
    log('导出文件 ' + path_m)
    with open(path_m, 'r', encoding='UTF-8') as f:
        master.load(f)
        master.pad()
    master += branch
    master.sort(key=lambda r: (r['uigf_gacha_type'], r['time'], r['id']))
    master.deduplicate()
    with open(path_m, 'w', encoding='UTF-8') as f:
        master.dump(f)

    path_x = f'./records_{branch.uid}.xlsx'
    log('导出文件 ' + path_x)
    if not save_as_uigf(master, path_x):
        log('警告: Excel表格导出失败')

    log('完毕。')


if __name__ == '__main__':
    main()
