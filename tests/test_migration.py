from gwk.records.excel import save_as_uigf
from gwk.records.models import Wish, merge_from_ggk


def main(uid):
    master = Wish()
    with open(f'./records_{uid}.json', 'r', encoding='UTF-8') as f:
        master.load(f)
    with open(f'./ggr_{uid}.json', 'r', encoding='UTF-8') as f:
        master = merge_from_ggk(master, f)
        master.sort()
    with open(f'./migration_{uid}.json', 'w', encoding='UTF-8') as f:
        master.dump(f)
    save_as_uigf(master, f'./migration_{uid}.xlsx')


if __name__ == '__main__':
    print('请输入已导出JSON的祈愿uid：', end='')
    main(input())
