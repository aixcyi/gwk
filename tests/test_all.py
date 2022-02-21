from datetime import datetime
from random import random
from time import sleep

from gwk.constants import WishType
from gwk.records.models import Wish
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
    log(f'{gacha_type.label}: 第{page}页获取完毕。')
    sleep(random())


wishes = [
    Wish(wish_type) for wish_type in WishType
]
log('鉴权信息: 正在读取本地日志……')
collector = RawCollector(
    auths=extract_auths(get_logfile())
)
log('鉴权信息: 测试中……')
collector.available()

log('--------开始获取--------')
for wish in wishes:
    wish += collector.get_wish(
        wish.wish_type, page_callback
    )
