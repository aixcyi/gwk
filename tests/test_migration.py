from gwk.records.excel import save_as_uigf
from gwk.records.models import Wish, migrate


def main(uid):
    with open(f'./ggr_{uid}.json', 'r', encoding='UTF-8') as f:
        old = migrate(f)

    new = Wish()
    with open(f'./records_{uid}.json', 'r', encoding='UTF-8') as f:
        new.load(f)

    new.merging_check = False
    new += old
    new.merging_check = True
    new.sort(key=lambda r: (r['uigf_gacha_type'], r['time'], r['id']))
    new.deduplicate()

    with open(f'./migration_{uid}.json', 'w', encoding='UTF-8') as f:
        new.dump(f)
    save_as_uigf(new, f'./migration_{uid}.xlsx')


if __name__ == '__main__':
    print('请输入已导出JSON的祈愿uid：', end='')
    main(input())
