#!/usr/bin/env python3
"""
updater.py - 版本检查和更新模块
"""

import subprocess
import sys
import urllib.request
import json
from typing import Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

# 当前版本（从 setup.py 同步）
__version__ = "1.0.0"

GITHUB_REPO = "huaguihai/claude-retry-optimizer"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
INSTALL_URL = f"git+https://github.com/{GITHUB_REPO}.git"


def get_current_version() -> str:
    """获取当前安装的版本"""
    return __version__


def get_latest_version() -> Optional[str]:
    """从 GitHub API 获取最新版本

    Returns:
        最新版本号（如 "1.0.1"）或 None
    """
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"User-Agent": "claude-retry-optimizer"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            # tag_name 格式: "v1.0.1" 或 "1.0.1"
            tag = data.get("tag_name", "")
            return tag.lstrip("v")
    except Exception as e:
        console.print(f"[yellow]警告: 无法检查更新 - {e}[/yellow]")
        return None


def compare_versions(v1: str, v2: str) -> int:
    """比较两个版本号

    Returns:
        1 if v1 > v2
        0 if v1 == v2
        -1 if v1 < v2
    """
    def parse_version(v: str) -> Tuple[int, int, int]:
        parts = v.split('.')
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    try:
        ver1 = parse_version(v1)
        ver2 = parse_version(v2)

        if ver1 > ver2:
            return 1
        elif ver1 < ver2:
            return -1
        else:
            return 0
    except Exception:
        return 0


def check_for_updates(silent: bool = False) -> Tuple[bool, Optional[str]]:
    """检查是否有更新

    Args:
        silent: 是否静默模式（不输出信息）

    Returns:
        (是否有更新, 最新版本号)
    """
    current = get_current_version()
    latest = get_latest_version()

    if latest is None:
        return False, None

    has_update = compare_versions(latest, current) > 0

    if not silent:
        if has_update:
            console.print(f"[yellow]发现新版本: {latest}[/yellow]")
            console.print(f"[dim]当前版本: {current}[/dim]")
        else:
            console.print(f"[green]✓[/green] 已是最新版本 ({current})")

    return has_update, latest


def update_package() -> bool:
    """执行更新

    Returns:
        是否成功
    """
    console.print("\n[cyan]正在更新...[/cyan]\n")

    try:
        # 执行 pip install --upgrade
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", INSTALL_URL],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            console.print("[green]✓[/green] 更新成功！")
            console.print("\n[dim]请重新运行 claude-retry-optimizer 使用新版本[/dim]")
            return True
        else:
            console.print(f"[red]✗[/red] 更新失败")
            console.print(f"[dim]{result.stderr}[/dim]")
            return False

    except Exception as e:
        console.print(f"[red]✗[/red] 更新失败: {e}")
        return False


def run_update_command():
    """运行 update 子命令"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Claude Retry Optimizer - 版本更新[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # 检查更新
    console.print("[cyan]检查更新...[/cyan]\n")
    has_update, latest_version = check_for_updates()

    if not has_update:
        console.print("\n[green]已是最新版本，无需更新[/green]")
        return

    # 显示更新信息
    console.print()
    console.print(Panel(
        f"[bold]发现新版本！[/bold]\n\n"
        f"当前版本: {get_current_version()}\n"
        f"最新版本: {latest_version}\n\n"
        f"更新地址: https://github.com/{GITHUB_REPO}",
        border_style="yellow",
        title="可用更新",
    ))
    console.print()

    # 确认更新
    if not Confirm.ask("是否立即更新？", default=True):
        console.print("\n[dim]已取消更新[/dim]")
        return

    # 执行更新
    success = update_package()

    if success:
        console.print()
        console.print(Panel(
            "[bold green]✅ 更新完成！[/bold green]\n\n"
            "请重新运行以下命令使用新版本:\n"
            "[cyan]claude-retry-optimizer[/cyan]",
            border_style="green",
        ))
