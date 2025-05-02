from datetime import datetime
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer

from ..lib.interactive_select import interactive_select


def get_default_output_dir() -> Path:
    """获取默认输出文件夹"""
    path = Path.cwd() / "output"
    path.mkdir(parents=True, exist_ok=True)
    return path


def main(
    file: Annotated[
        Path,
        typer.Argument(
            help="要分割的Excel文件", exists=True, file_okay=True, dir_okay=False
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Argument(
            help="输出文件夹名，默认当前目录下的 output 文件夹",
            default_factory=get_default_output_dir,
            exists=False,
            file_okay=False,
            dir_okay=True,
        ),
    ],
    sheet: Annotated[
        int,
        typer.Option(help="要分割的Sheet名"),
    ] = 0,
    prefix: Annotated[
        str,
        typer.Option(help="文件名前缀"),
    ] = None,
):
    """
    主命令入口：读取 Excel，交互式选择分组列，按组分割并输出。
    """
    try:
        df = read_excel_file(file, sheet)
    except Exception as e:
        typer.secho(f"读取 Excel 失败: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
    if df.empty:
        typer.secho("Excel 数据为空，无法分割。", fg=typer.colors.RED)
        raise typer.Exit(1)
    columns = list(df.columns)
    try:
        selected_cols, _ = interactive_select(
            columns,
            header="请选择分组列（可多选，空格选择，回车确认）",
            min_selections=1,
        )
    except KeyboardInterrupt:
        typer.secho("操作已取消。", fg=typer.colors.YELLOW)
        raise typer.Exit(0)
    if not selected_cols:
        typer.secho("未选择分组列，已退出。", fg=typer.colors.YELLOW)
        raise typer.Exit(0)
    try:
        split_and_save_by_group(
            df,
            group_cols=selected_cols,
            output_dir=output_dir,
            prefix=prefix,
            origin_file=file,
        )
    except Exception as e:
        typer.secho(f"分组写入文件失败: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"分割完成，文件已输出到: {output_dir}", fg=typer.colors.GREEN)


def read_excel_file(file_path: Path, sheet_name: str = None) -> pd.DataFrame:
    """
    读取 Excel 文件并返回指定 Sheet 的 DataFrame。

    Args:
        file_path (Path): Excel 文件路径。
        sheet_name (str, optional): 要读取的 Sheet 名称，默认为第一个 Sheet。

    Returns:
        pd.DataFrame: 读取到的数据。

    Raises:
        FileNotFoundError: 文件不存在时抛出。
        ValueError: Sheet 名称不存在时抛出。
        pd.errors.EmptyDataError: 文件为空时抛出。
        Exception: 其他读取异常。
    """
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name or 0)
    except ValueError as e:
        raise ValueError(f"Sheet 名称不存在: {sheet_name}") from e
    except Exception as e:
        raise Exception(f"读取 Excel 文件失败: {e}") from e
    return df


def split_and_save_by_group(
    df: pd.DataFrame,
    group_cols: list[str],
    output_dir: Path,
    prefix: str = "",
    origin_file: Path = None,
) -> None:
    """
    按指定列对 DataFrame 分组并将每组写入单独的 Excel 文件。

    Args:
        df (pd.DataFrame): 需要分组的数据。
        group_cols (list[str]): 分组依据的列名列表。
        output_dir (Path): 输出目录。
        prefix (str, optional): 文件名前缀，未提供则用原文件名。
        origin_file (Path, optional): 原始 Excel 文件路径，用于默认前缀。

    Raises:
        ValueError: 分组列不存在时抛出。
        Exception: 写入文件失败时抛出。
    """
    if not group_cols:
        raise ValueError("必须指定至少一个分组列")
    for col in group_cols:
        if col not in df.columns:
            raise ValueError(f"分组列不存在: {col}")
    output_dir.mkdir(parents=True, exist_ok=True)
    if not prefix:
        if origin_file is not None:
            prefix = origin_file.stem
    date_str = datetime.now().strftime("%Y%m%d")
    for group_keys, group_df in df.groupby(group_cols):
        if not isinstance(group_keys, tuple):
            group_keys = (group_keys,)
        group_name = "_".join(str(k) for k in group_keys)
        file_name = f"{prefix}.{group_name}.{date_str}.xlsx"
        file_path = output_dir / file_name
        try:
            group_df.to_excel(file_path, index=False)
        except Exception as e:
            raise Exception(f"写入文件失败: {file_path}, 错误: {e}") from e
