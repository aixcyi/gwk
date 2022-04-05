from gwk.io.local import save_as_uigf, migrate


def main(uid):
    with open(f'./ggr_{uid}.json', 'r', encoding='UTF-8') as f:
        old = migrate(f)

    with open(f'./records_{uid}-.json', 'w', encoding='UTF-8') as f:
        old.dump(f)
    save_as_uigf(old, f'./records_{uid}-.xlsx')


if __name__ == '__main__':
    print('请输入已导出JSON的祈愿uid：', end='')
    main(input())
