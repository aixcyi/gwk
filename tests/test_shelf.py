from datetime import datetime
from random import random
from time import sleep

from gwk.constants import WishType
from gwk.records.models import PlayerShelf
from gwk.records.wrappers import RawCollector
from gwk.utils import (
    extract_auths,
    get_logfile,
    map_raw_to_basic
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

    log('鉴权信息: 正在读取本地日志……')
    collector = RawCollector(auths=extract_auths(get_logfile()))

    log('鉴权信息: 测试中……')
    collector.available()

    for wish_type in WishType:
        branch[wish_type] += collector.get_wish(
            wish_type, page_callback
        )
        branch[wish_type].maps(map_raw_to_basic)
        log('----------------')
    branch.pad()

    log('文件: 导出当次获取……')
    export = datetime.now()
    path_b = export.strftime(
        f'./records_{branch.uid}_%Y%m%d_%H%M%S.json'
    )
    with open(path_b, 'w', encoding='UTF-8') as f:
        branch.dump(f, export)

    path_m = f'./records_{branch.uid}.json'
    with open(path_m, 'r', encoding='UTF-8') as f:
        master.load(f)
        master.pad()

    log('文件: 正在合并总记录……')
    master += branch

    log('文件: 导出总记录……')
    with open(path_m, 'w', encoding='UTF-8') as f:
        master.dump(f)


if __name__ == '__main__':
    main()
