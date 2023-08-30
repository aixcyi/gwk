#!./venv/Scripts/python.exe
# -*- coding: utf-8 -*-
from pathlib import Path

from rich import box

try:
    import click
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print('pip install --user -r ./requirements.txt')
    print('请先安装依赖包。')
    exit(0)

from gwk.handlers.abs import HandlingException, SingleGachaFileHandler
from gwk.handlers.biuuu import BiuuuJsonHandler
from gwk.handlers.uigf import UigfJsonHandler

HANDLERS: tuple[type[SingleGachaFileHandler], ...] = (
    UigfJsonHandler,
    BiuuuJsonHandler,
)

ego = Path(__file__).absolute()


def warning(msg: str):
    console = Console(stderr=True)
    console.print(msg, style='yellow')


@click.group(__name__)
@click.help_option('-h', '--help', help='显示这份帮助信息。')
def cli():
    """
    各家祈愿记录导出文件的转换器。Genshin Gacha Records Converter。
    """


@cli.command('list', help='列出所有处理器。')
@click.help_option('-h', '--help', help='显示这份帮助信息。')
def lister():
    table = Table('处理器', '描述', box=box.SIMPLE_HEAD)

    for handler in HANDLERS:
        if not issubclass(handler, SingleGachaFileHandler):
            continue
        if handler.abstract:
            continue
        table.add_row(handler.__name__, handler.description)

    Console().print(table)


@cli.command('convert', help='将文件转换到另一种格式。')
@click.argument('handle_by')
@click.argument('file')
@click.option('-o', '--output', 'save_to', metavar='FILE', help='输出到哪里。')
@click.option('-f', '--force', is_flag=True, help='不提示，直接保存。')
@click.help_option('-h', '--help', help='显示这份帮助信息。')
def converter(
        handle_by: str,
        file: str,
        save_to: str = None,
        force: bool = False,
):
    try:
        Builder = HANDLERS[[h.__name__ for h in HANDLERS].index(handle_by)]
        builder = Builder()
    except ValueError:
        warning(f'处理器 {handle_by} 不存在。请使用 {ego.name} list 命令查看所有处理器。')
        return

    ifp = Path(file).absolute()
    if not ifp.exists():
        warning('文件不存在。')
        return

    ofp = Path(save_to or file).absolute()
    if ofp.exists() and not force:
        if ofp == ifp:
            if input('覆盖保存到输入数据的文件？Y/[n]')[:1] not in 'yY':
                return
        else:
            if input('目标文件已存在，覆盖原有数据？Y/[n]')[:1] not in 'yY':
                return

    for Handler in HANDLERS:
        handler = Handler()
        if not handler.is_supported(ifp):
            continue
        try:
            handler.read(ifp)
        except HandlingException:
            continue
        print(f'已使用 {Handler.__name__} 读取。')

        builder.data = handler.data
        builder.write(ofp)
        print(f'已使用 {Builder.__name__} 写入。')
        return

    print('解析过程中找不到合适的处理器。未向文件写入任何数据。')


if __name__ == '__main__':
    cli()
