#!./venv/Scripts/python.exe
# -*- coding: utf-8 -*-
from enum import Enum
from pathlib import Path

try:
    import click
    from rich import box
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print('pip install --user -r ./requirements.txt')
    print('请先安装依赖包。')
    exit(-1)

from gwk.handlers.abs import HandlingException, SingleGachaFileHandler
from gwk.handlers.biuuu import BiuuuJsonHandler
from gwk.handlers.uigf import UigfJsonHandler
from gwk.common import patch_id64

HANDLERS: tuple[type[SingleGachaFileHandler], ...] = (
    UigfJsonHandler,
    BiuuuJsonHandler,
)

ego = Path(__file__).absolute()


class ExitCode(Enum):
    DONE = 0
    UNKNOWN = -1
    FILE_NOTFOUND = -10000
    HANDLER_NOTFOUND = -10086
    SOLUTION_NOTFOUND = -10100


def warning(msg: str):
    console = Console(stderr=True)
    console.print(msg, style='yellow')


@click.group(__name__)
@click.help_option('-h', '--help', help='显示这份帮助信息。')
def cli():
    """
    各家祈愿记录导出文件的转换器。
    """


@cli.command('list', help='列出所有处理器及修复方案。')
@click.help_option('-h', '--help', help='显示这份帮助信息。')
def lister():
    table = Table('处理器', '描述', box=box.SIMPLE_HEAD)

    for handler in HANDLERS:
        if not issubclass(handler, SingleGachaFileHandler):
            continue
        if handler.abstract:
            continue
        if handler.__name__.endswith('Handler'):
            name = handler.__name__[:-7]
        else:
            name = handler.__name__
        table.add_row(name, handler.description)

    Console().print(table)


@cli.command('convert', help='将文件转换到另一种格式。')
@click.argument('file')
@click.option('-s', '--save-to', metavar='FILE', help='输出到哪里。')
@click.option('-r', '--reader', metavar='HANDLER', help='源格式的处理器。若不提供则自动识别。')
@click.option('-w', '--writer', metavar='HANDLER', help='目标格式的处理器。默认与源格式处理器相同。')
@click.option('--patch-id-64', is_flag=True,
              help='模拟生成祈愿记录的ID，并补充到数据集中。模拟ID在设计上保证是一个有符号64位整数。')
@click.option('-F', '--force', is_flag=True, help='不提示，直接保存。')
@click.help_option('-h', '--help', help='显示这份帮助信息。')
def converter(
        file: str,
        save_to: str = None,
        reader: str = None,
        writer: str = None,
        patch_id_64: str = None,
        force: bool = False,
):
    # --------------------------------
    # 校验

    ifp = Path(file).absolute()
    if not ifp.exists():
        warning(f'{ifp!s} 文件不存在。')
        exit(ExitCode.FILE_NOTFOUND)

    ofp = Path(save_to or file).absolute()
    if ofp.exists() and not force:
        if ofp == ifp:
            if input('覆盖保存到输入数据的文件？y/[n] ')[:1] not in 'yY':
                exit(ExitCode.FILE_NOTFOUND)
        else:
            if input('目标文件已存在，确认覆盖？y/[n] ')[:1] not in 'yY':
                exit(ExitCode.FILE_NOTFOUND)

    # --------------------------------
    # 读取

    if reader:
        try:
            parser = HANDLERS[[h.__name__ for h in HANDLERS].index(f'{reader}Handler')]()
        except ValueError:
            warning(f'处理器 {reader} 不存在。请使用 {ego.name} list 命令查看所有处理器。')
            exit(ExitCode.HANDLER_NOTFOUND)
        try:
            parser.read(ifp)
        except HandlingException as e:
            print(str(e))
            exit(ExitCode.UNKNOWN)
        except:
            Console().print_exception()
            exit(ExitCode.UNKNOWN)
    else:
        for Parser in HANDLERS:
            if Parser.abstract:
                continue
            parser = Parser()
            if not parser.is_supported(ifp):
                continue
            try:
                parser.read(ifp)
                break
            except HandlingException:
                continue
        else:
            print('找不到合适的源格式处理器。')
            exit(ExitCode.HANDLER_NOTFOUND)

    # ----------------

    if writer:
        try:
            builder = HANDLERS[[h.__name__ for h in HANDLERS].index(f'{writer}Handler')]()
        except ValueError:
            warning(f'处理器 {writer} 不存在。请使用 {ego.name} list 命令查看所有处理器。')
            exit(ExitCode.HANDLER_NOTFOUND)
    else:
        builder = type(parser)()

    # ----------------

    rows_total_unload = parser.rows_total_read - parser.rows_total_loaded
    if rows_total_unload > 0:
        print(
            f'读取 {parser.rows_total_read} 条记录，'
            f'解析 {parser.rows_total_loaded} 条记录，'
            f'有 {rows_total_unload} 条解析失败。'
        )
    else:
        print(
            f'读取 {parser.rows_total_read} 条记录，'
            f'全部解析成功。'
        )

    # --------------------------------
    # 修复

    data = parser.data

    if patch_id_64:
        rows_total_broken, rows_total_effected = patch_id64(data)
        print(
            f'总计 {rows_total_broken} 条记录缺失 ID，'
            f'为 {rows_total_effected} 条记录补充了 ID。'
        )

    # --------------------------------
    # 保存

    name = builder.__class__.__name__
    name = name[:-1] if name.endswith('Handler') else name
    builder.data = data
    builder.write(ofp)
    print(f'已使用 {name} 写入。')


if __name__ == '__main__':
    cli()
