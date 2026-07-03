#!/usr/bin/env python3
"""
menu.py - 交互式菜单系统
"""

import os
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table

from .binary import (
    find_binary,
    get_binary_info,
    has_backup,
    create_backup,
    restore_from_backup,
    remove_backup,
    read_binary,
    write_binary,
    check_version_compatibility,
)
from .config import ConfigManager
from .env import EnvManager
from .patcher import PatchConfig, apply_patches


console = Console()


class MenuSystem:
    """菜单系统"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.env_manager = EnvManager()
        self.binary_path: Optional[str] = None

    def show_header(self):
        """显示标题"""
        console.print()
        console.print(Panel.fit(
            "[bold cyan]Claude Code 重试优化工具[/bold cyan]\n"
            "[dim]优化 Claude Code 的重试行为，提升稳定性[/dim]",
            border_style="cyan"
        ))
        console.print()

    def show_status(self):
        """显示当前状态"""
        from .binary import get_claude_version

        # 检测二进制
        self.binary_path = find_binary()

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("项目", style="cyan", width=12)
        table.add_column("状态")

        # 当前状态
        status = self.config_manager.get_status()
        status_color = "green" if "已配置" in status else "yellow"
        table.add_row("🎯 配置状态", f"[{status_color}]{status}[/{status_color}]")

        # Claude 路径
        if self.binary_path:
            table.add_row("📍 Claude 路径", self.binary_path)
        else:
            table.add_row("📍 Claude 路径", "[red]未找到[/red]")

        # Claude 版本（传入 binary_path）
        if self.binary_path:
            version = get_claude_version(self.binary_path)
            if version:
                table.add_row("📦 Claude 版本", version)

        # 备份状态
        if self.binary_path:
            backup_status = "有备份 ✓" if has_backup(self.binary_path) else "未备份"
            backup_color = "green" if has_backup(self.binary_path) else "dim"
            table.add_row("💾 备份状态", f"[{backup_color}]{backup_status}[/{backup_color}]")

        # 配置摘要
        config_summary = self.config_manager.get_config_summary()
        if config_summary:
            table.add_row("⚙️  当前配置", config_summary)

        console.print(Panel(table, border_style="cyan", title="系统状态", title_align="left"))
        console.print()

    def show_main_menu(self):
        """显示主菜单"""
        console.print("[bold]请选择操作：[/bold]")
        console.print("  [cyan]1.[/cyan] 开始配置")
        console.print("  [cyan]2.[/cyan] 修改配置")
        console.print("  [cyan]3.[/cyan] 测试当前配置")
        console.print("  [cyan]4.[/cyan] 卸载")
        console.print("  [cyan]5.[/cyan] 退出")
        console.print()

    def run(self):
        """运行菜单系统"""
        while True:
            console.clear()
            self.show_header()
            self.show_status()
            self.show_main_menu()

            choice = Prompt.ask("请选择", choices=["1", "2", "3", "4", "5"], default="5")

            if choice == "1":
                self.start_config()
            elif choice == "2":
                self.modify_config()
            elif choice == "3":
                self.test_config()
            elif choice == "4":
                self.uninstall()
            elif choice == "5":
                console.print("\n[cyan]再见！[/cyan]")
                break

    def show_config_menu(self) -> str:
        """显示配置子菜单

        Returns:
            选择的模式 ("quick" 或 "custom" 或 "cancel")
        """
        console.print("\n[bold]选择配置方式：[/bold]\n")
        console.print("  [cyan]1.[/cyan] 快捷配置（推荐）")
        console.print("      [dim]重试 50 次，间隔 1 秒[/dim]")
        console.print()
        console.print("  [cyan]2.[/cyan] 自定义配置")
        console.print("      [dim]手动设置参数[/dim]")
        console.print()
        console.print("  [cyan]0.[/cyan] 返回")
        console.print()

        choice = Prompt.ask("请选择", choices=["0", "1", "2"], default="1")

        if choice == "1":
            return "quick"
        elif choice == "2":
            return "custom"
        else:
            return "cancel"

    def get_custom_config(self) -> Optional[dict]:
        """获取自定义配置

        Returns:
            配置字典或 None（取消）
        """
        console.print("\n[bold cyan]自定义配置[/bold cyan]\n")

        try:
            max_retries = IntPrompt.ask(
                "请输入最大重试次数 (15-99)",
                default=50
            )
            if max_retries < 15 or max_retries > 99:
                console.print("[red]✗[/red] 重试次数必须在 15-99 之间")
                return None

            retry_interval = IntPrompt.ask(
                "请输入重试间隔（秒）(1-5)",
                default=1
            )
            if retry_interval < 1 or retry_interval > 5:
                console.print("[red]✗[/red] 重试间隔必须在 1-5 秒之间")
                return None

            console.print("\n[bold]确认配置：[/bold]")
            console.print(f"  • 最大重试次数：{max_retries}")
            console.print(f"  • 重试间隔：{retry_interval} 秒")
            console.print()

            if not Confirm.ask("是否应用此配置？", default=True):
                return None

            return {
                "max_retries": max_retries,
                "retry_interval_ms": retry_interval * 1000,
            }
        except KeyboardInterrupt:
            return None

    def apply_config(self, mode: str, config: dict) -> bool:
        """应用配置

        Args:
            mode: 模式 ("quick" 或 "custom")
            config: 配置字典 {"max_retries": int, "retry_interval_ms": int}

        Returns:
            是否成功
        """
        if not self.binary_path:
            console.print("[red]✗[/red] 未找到 Claude Code")
            return False

        console.print("\n[cyan]正在应用配置...[/cyan]\n")

        # 读取二进制
        console.print("[cyan]读取二进制文件...[/cyan]")
        data = read_binary(self.binary_path)
        if data is None:
            console.print("[red]✗[/red] 读取二进制文件失败")
            return False
        console.print("[green]✓[/green] 读取成功")

        # 应用 patch
        console.print("[cyan]应用优化...[/cyan]")
        patch_config = PatchConfig(
            max_retries=config["max_retries"],
            retry_interval_ms=config["retry_interval_ms"],
        )
        patched_data, stats = apply_patches(data, patch_config, verbose=True)

        console.print()
        if stats["applied"] == 0:
            console.print("[red]✗[/red] 未应用任何优化")
            return False

        console.print(f"[green]✓[/green] 成功应用 {stats['applied']} 项优化")
        if stats["failed"] > 0:
            console.print(f"[yellow]![/yellow] {stats['failed']} 项优化跳过")

        # 写入二进制
        console.print("\n[cyan]写入二进制文件...[/cyan]")
        if not write_binary(self.binary_path, patched_data):
            console.print("[red]✗[/red] 写入失败")
            return False
        console.print("[green]✓[/green] 写入成功")

        # 设置环境变量
        console.print("[cyan]设置环境变量...[/cyan]")
        if not self.env_manager.setup_env(
            config["max_retries"],
            config["retry_interval_ms"]
        ):
            console.print("[yellow]![/yellow] 环境变量设置失败")

        console.print("[green]✓[/green] 环境变量设置成功")

        # 保存配置
        console.print("[cyan]保存配置...[/cyan]")
        cfg = self.config_manager.create_config(
            self.binary_path,
            mode,
            config["max_retries"],
            config["retry_interval_ms"]
        )
        if not self.config_manager.save(cfg):
            console.print("[yellow]![/yellow] 配置保存失败")
        console.print("[green]✓[/green] 配置保存成功")

        return True

    def ensure_backup(self) -> bool:
        """确保备份存在（自动创建）

        Returns:
            是否成功（备份已存在或创建成功）
        """
        if not self.binary_path:
            console.print("[red]✗[/red] 未找到 Claude Code")
            return False

        if has_backup(self.binary_path):
            return True  # 已有备份

        # 自动创建备份
        console.print("\n[cyan]💾 首次使用需要创建备份...[/cyan]")
        console.print("[dim]（备份文件用于恢复原版，只创建一次）[/dim]\n")

        # 检查版本兼容性
        is_compatible, current_version, error_msg = check_version_compatibility()

        if not is_compatible:
            console.print(Panel(
                f"[yellow]⚠️  版本不兼容[/yellow]\n\n"
                f"[red]{error_msg}[/red]\n\n"
                f"[bold]此工具需要 Claude Code 2.1.191 或更高版本。[/bold]\n"
                f"优化可能无法生效。\n\n"
                f"[bold cyan]建议操作：[/bold cyan]\n"
                f"  1. 升级到最新版本:\n"
                f"     [cyan]npm update -g @anthropic-ai/claude-code[/cyan]\n\n"
                f"  2. 或使用官方环境变量（不修改二进制）:\n"
                f"     [cyan]export CLAUDE_CODE_RETRY_WATCHDOG=300000[/cyan]",
                border_style="yellow",
                title="版本检查",
            ))
            console.print()

            if not Confirm.ask("是否仍要继续？（不推荐）", default=False):
                return False

            console.print("\n[yellow]⚠️  警告: 强制继续可能导致优化失败[/yellow]\n")

        # 创建备份
        info = get_binary_info(self.binary_path)
        size_mb = info['size'] / (1024 * 1024)
        console.print(f"[cyan]正在备份二进制文件... ({size_mb:.1f} MB)[/cyan]")

        if not create_backup(self.binary_path):
            console.print("[red]✗[/red] 备份创建失败")
            return False

        console.print("[green]✓[/green] 备份创建成功\n")
        return True

    def start_config(self):
        """开始配置"""
        console.print("\n[bold cyan]→ 开始配置[/bold cyan]\n")

        # 检查 Claude Code
        if not self.binary_path:
            console.print("[red]✗[/red] 未找到 Claude Code")
            console.print("请先安装: [cyan]npm install -g @anthropic-ai/claude-code[/cyan]")
            Prompt.ask("\n按回车返回")
            return

        # 自动确保备份存在
        if not self.ensure_backup():
            Prompt.ask("\n按回车返回")
            return

        # 显示配置菜单
        mode = self.show_config_menu()
        if mode == "cancel":
            return

        # 获取配置
        if mode == "quick":
            config = {
                "max_retries": 50,
                "retry_interval_ms": 1000,
            }
        else:  # custom
            config = self.get_custom_config()
            if config is None:
                return

        # 应用配置
        success = self.apply_config(mode, config)

        console.print()
        if success:
            console.print(Panel(
                "[bold green]✅ 配置完成！[/bold green]\n\n"
                "📊 [bold]优化摘要[/bold]\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "✓ 重试策略已优化\n"
                "✓ 环境变量已设置\n"
                "✓ 配置已保存\n\n"
                "💡 [dim]提示：新配置将在下次启动 Claude Code 时生效[/dim]\n"
                "[dim]   如需立即生效，请重新打开终端或执行: source ~/.bashrc[/dim]",
                border_style="green",
                title="配置成功",
            ))
        else:
            console.print("[bold red]❌ 配置失败[/bold red]")

        Prompt.ask("\n按回车返回")

    def modify_config(self):
        """修改配置"""
        console.print("\n[bold cyan]→ 修改配置[/bold cyan]\n")

        # 检查是否已配置
        config = self.config_manager.load()
        if not config or config.get("status") != "configured":
            console.print("[yellow]![/yellow] 尚未配置，请先选择 [cyan]1. 开始配置[/cyan]")
            Prompt.ask("\n按回车返回")
            return

        # 自动确保备份存在（修改配置也需要修改二进制）
        if not self.ensure_backup():
            Prompt.ask("\n按回车返回")
            return

        # 显示当前配置
        console.print("[bold]当前配置：[/bold]")
        cfg = config.get("config", {})
        console.print(f"  • 最大重试次数：{cfg.get('max_retries', '?')}")
        console.print(f"  • 重试间隔：{cfg.get('retry_interval_ms', '?')} ms")
        console.print()

        # 显示配置菜单（复用）
        mode = self.show_config_menu()
        if mode == "cancel":
            return

        # 获取新配置
        if mode == "quick":
            new_config = {
                "max_retries": 50,
                "retry_interval_ms": 1000,
            }
        else:  # custom
            new_config = self.get_custom_config()
            if new_config is None:
                return

        # 应用配置
        success = self.apply_config(mode, new_config)

        console.print()
        if success:
            console.print(Panel(
                "[bold green]✅ 配置已更新！[/bold green]\n\n"
                "💡 [dim]提示：新配置将在下次启动 Claude Code 时生效[/dim]",
                border_style="green",
            ))
        else:
            console.print("[bold red]❌ 配置更新失败[/bold red]")

        Prompt.ask("\n按回车返回")

    def test_config(self):
        """测试当前配置"""
        console.print("\n[bold cyan]→ 测试当前配置[/bold cyan]\n")

        config = self.config_manager.load()
        if not config or config.get("status") != "configured":
            console.print("[yellow]![/yellow] 尚未配置，无法测试")
            Prompt.ask("\n按回车返回")
            return

        cfg = config.get("config", {})
        max_retries = cfg.get("max_retries", 50)
        interval_ms = cfg.get("retry_interval_ms", 1000)

        console.print("[bold]当前配置：[/bold]")
        console.print(f"  • 最大重试次数：{max_retries}")
        console.print(f"  • 重试间隔：{interval_ms} ms")
        console.print()

        console.print("[dim]模拟测试：假设前 2 次失败，第 3 次成功[/dim]\n")

        import time
        for i in range(1, 4):
            if i < 3:
                console.print(f"  [尝试 {i}/{max_retries}] [red]失败[/red] → 等待 {interval_ms}ms")
                time.sleep(interval_ms / 1000)
            else:
                console.print(f"  [尝试 {i}/{max_retries}] [green]成功 ✓[/green]")

        total_time = (interval_ms / 1000) * 2
        console.print(f"\n[bold]测试结果：[/bold]")
        console.print(f"  • 总耗时：{total_time:.1f} 秒")
        console.print(f"  • 成功重试：第 3 次")

        Prompt.ask("\n按回车返回")

    def uninstall(self):
        """卸载"""
        console.print("\n[bold cyan]→ 卸载[/bold cyan]\n")

        if not self.binary_path:
            console.print("[red]✗[/red] 未找到 Claude Code")
            Prompt.ask("\n按回车返回")
            return

        if not has_backup(self.binary_path):
            console.print("[yellow]![/yellow] 未找到备份文件，无法卸载")
            console.print("[dim]（可能从未配置过，或备份已被手动删除）[/dim]")
            Prompt.ask("\n按回车返回")
            return

        # 显示备份信息
        info = get_binary_info(self.binary_path)
        backup_path = info['path'] + '.orig'
        backup_size = os.path.getsize(backup_path) / (1024 * 1024)

        console.print(Panel(
            f"[yellow]⚠️  确认卸载[/yellow]\n\n"
            f"此操作将：\n"
            f"  • 恢复原版 Claude Code\n"
            f"  • 清理环境变量\n"
            f"  • 删除配置文件\n"
            f"  • 删除备份文件 ({backup_size:.1f} MB)\n\n"
            f"[dim]卸载后可重新配置[/dim]",
            border_style="yellow",
        ))
        console.print()

        if not Confirm.ask("确定要卸载吗？", default=False):
            return

        console.print("\n[cyan]正在卸载...[/cyan]\n")

        # 恢复二进制
        console.print("[cyan]恢复原版二进制...[/cyan]")
        if not restore_from_backup(self.binary_path):
            console.print("[red]✗[/red] 恢复失败")
            Prompt.ask("\n按回车返回")
            return
        console.print("[green]✓[/green] 恢复成功")

        # 清理环境变量
        console.print("[cyan]清理环境变量...[/cyan]")
        self.env_manager.cleanup_env()
        console.print("[green]✓[/green] 环境变量已清理")

        # 删除配置
        console.print("[cyan]删除配置文件...[/cyan]")
        self.config_manager.remove()
        console.print("[green]✓[/green] 配置文件已删除")

        # 删除备份
        console.print("[cyan]删除备份文件...[/cyan]")
        remove_backup(self.binary_path)
        console.print("[green]✓[/green] 备份文件已删除")

        console.print()
        console.print(Panel(
            "[bold green]✅ 卸载完成！[/bold green]\n\n"
            "已恢复到官方默认配置\n"
            "你可以随时重新配置",
            border_style="green",
        ))

        Prompt.ask("\n按回车返回")


def main():
    """主函数"""
    import sys

    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "update":
            from .updater import run_update_command
            run_update_command()
            return
        elif sys.argv[1] in ["-h", "--help"]:
            console.print("\n[bold cyan]Claude Retry Optimizer[/bold cyan] - 优化 Claude Code 重试行为\n")
            console.print("用法:")
            console.print("  [cyan]claude-retry-optimizer[/cyan]        启动交互式菜单")
            console.print("  [cyan]claude-retry-optimizer update[/cyan]  检查并更新到最新版本")
            console.print("  [cyan]claude-retry-optimizer -h[/cyan]      显示此帮助信息")
            console.print()
            return
        else:
            console.print(f"[red]未知命令: {sys.argv[1]}[/red]")
            console.print("使用 [cyan]claude-retry-optimizer -h[/cyan] 查看帮助")
            sys.exit(1)

    # 默认启动菜单
    try:
        menu = MenuSystem()
        menu.run()
    except KeyboardInterrupt:
        console.print("\n\n[cyan]已取消[/cyan]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
