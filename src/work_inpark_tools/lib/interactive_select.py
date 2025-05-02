"""通用交互式选择模块（questionary 版）。

此模块基于 questionary 实现交互式多选，支持任意类型列表选择。
"""

from typing import Any, Callable, List, Optional, Tuple

import questionary
from questionary import Style


def interactive_select(
    items: List[Any],
    *,
    item_formatter: Optional[Callable[[Any], str]] = None,
    header: str = "使用空格选择，回车确认，Ctrl+C 取消",
    min_selections: int = 1,
    max_selections: Optional[int] = None,
) -> Tuple[List[Any], List[int]]:
    """交互式选择列表项（基于 questionary）。

    Args:
        items: 待选择的项目列表
        item_formatter: 自定义项目格式化函数，默认使用 str()
        header: 菜单头部显示的文本
        min_selections: 最少需要选择的项目数（questionary 不支持，需自行校验）
        max_selections: 最多可以选择的项目数（questionary 不支持，需自行校验）

    Returns:
        Tuple[List[Any], List[int]]: 选中的项目列表和对应的索引列表
    """
    if not items:
        return [], []
    formatter = item_formatter or str
    choices = [
        questionary.Choice(title=formatter(item), value=i)
        for i, item in enumerate(items)
    ]
    custom_style = Style(
        [
            ("checkbox", "fg:#00d787"),  # 选项文本颜色
            ("selected", "fg:#ffaf00 bold"),  # 选中项颜色
            ("pointer", "fg:#00d7ff bold"),  # 光标颜色
            ("question", "fg:#5f5fff bold"),  # 问题颜色
            ("answer", "fg:#ff5f5f bold"),  # 答案颜色
            ("separator", "fg:#6c6c6c"),  # 分隔符颜色
        ]
    )
    while True:
        result = questionary.checkbox(
            message=header,
            choices=choices,
            validate=lambda a: (len(a) >= min_selections)
            or f"至少选择 {min_selections} 项"
            if min_selections > 0
            else True,
            qmark="»",
            style=custom_style,
        ).ask()
        if result is None:
            raise KeyboardInterrupt
        if max_selections is not None and len(result) > max_selections:
            print(f"最多只能选择 {max_selections} 项，请重新选择。\n")
            continue
        break
    selected_indices = sorted(result)
    selected_items = [items[i] for i in selected_indices]
    return selected_items, selected_indices


if __name__ == "__main__":
    test_items = [f"选项{i + 1}" for i in range(13)]
    selected, indices = interactive_select(test_items)
    print("你选择了：", selected)
