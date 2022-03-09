from datetime import datetime
from random import random
from time import sleep

from gwk.constants import WishType
from gwk.records.models import PlayerPool, map_raw_to_basic
from gwk.records.wrappers import RawCollector
from gwk.utils import extract_auths, get_logfile


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
    log(f'{gacha_type.label}: 第{page}页获取完毕。')
    sleep(random())


def main():
    branch = PlayerPool()

    log('鉴权信息: 正在读取本地日志……')
    collector = RawCollector(auths=extract_auths(get_logfile()))

    log('鉴权信息: 测试中……')
    collector.available()

    for wish_type in WishType:
        branch.wish += collector.get_wish(wish_type, page_callback)
        log('----------------')
    branch.wish.sort()
    branch.wish.maps(map_raw_to_basic)
    branch.pad()

    with open('./z_records.json', 'w', encoding='UTF-8') as f:
        branch.dump(f)


if __name__ == '__main__':
    main()
