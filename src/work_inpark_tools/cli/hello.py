from typing import Optional

import typer


def world(
    name: Optional[str] = typer.Argument(None, help="要问候的名字"),
    count: int = typer.Option(1, "--count", "-c", help="重复次数"),
):
    """
    向世界或指定的名字问好
    """
    for _ in range(count):
        if name:
            typer.echo(f"你好, {name}!")
        else:
            typer.echo("你好, 世界!")
