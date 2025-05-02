from typing import Annotated, Optional

import typer

from .cli import split_excel

try:
    from importlib.metadata import version

    __version__ = version("work-inpark-tools")
except ImportError:
    from importlib_metadata import version  # type: ignore

    __version__ = version("work-inpark-tools")

app = typer.Typer(name="inpark-tools", help="工具集")

app.command(name="split-excel", help="分割 Excel 文件")(split_excel)


def version_callback(value: bool):
    if value:
        typer.secho(__version__, fg=typer.colors.GREEN)
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            help="显示版本信息",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    typer.secho(__version__, fg=typer.colors.GREEN)
