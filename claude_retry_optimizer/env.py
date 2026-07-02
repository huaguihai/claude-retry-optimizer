#!/usr/bin/env python3
"""
env.py - 环境变量管理模块
"""

import os
from pathlib import Path
from typing import List, Optional


class EnvManager:
    """环境变量管理器"""

    ENV_FILE = Path.home() / ".claude-retry-optimizer.env"

    def __init__(self):
        self.env_file = self.ENV_FILE

    def generate_env_content(self, max_retries: int, retry_interval_ms: int) -> str:
        """生成环境变量文件内容"""
        return f"""# Claude Retry Optimizer - 自动生成的环境变量
# 请勿手动编辑此文件

export CLAUDE_CODE_MAX_RETRIES={max_retries}
export CLAUDE_CODE_RETRY_INTERVAL_MS={retry_interval_ms}
"""

    def write_env_file(self, max_retries: int, retry_interval_ms: int) -> bool:
        """写入环境变量文件"""
        try:
            content = self.generate_env_content(max_retries, retry_interval_ms)
            with open(self.env_file, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入环境变量文件失败: {e}")
            return False

    def remove_env_file(self) -> bool:
        """删除环境变量文件"""
        if self.env_file.exists():
            try:
                self.env_file.unlink()
                return True
            except Exception as e:
                print(f"删除环境变量文件失败: {e}")
                return False
        return True

    def get_shell_config_files(self) -> List[Path]:
        """获取 shell 配置文件列表"""
        home = Path.home()
        configs = []

        # Bash
        bashrc = home / ".bashrc"
        if bashrc.exists():
            configs.append(bashrc)

        # Zsh
        zshrc = home / ".zshrc"
        if zshrc.exists():
            configs.append(zshrc)

        # Fish
        fish_config = home / ".config" / "fish" / "config.fish"
        if fish_config.exists():
            configs.append(fish_config)

        return configs

    def is_env_sourced(self, shell_config: Path) -> bool:
        """检查 shell 配置是否已 source 环境变量文件"""
        try:
            with open(shell_config, "r", encoding="utf-8") as f:
                content = f.read()
            return str(self.env_file) in content
        except Exception:
            return False

    def add_source_to_shell_config(self, shell_config: Path) -> bool:
        """在 shell 配置中添加 source 语句"""
        if self.is_env_sourced(shell_config):
            return True  # 已经添加过

        source_line = f"\n# Claude Retry Optimizer\n[ -f {self.env_file} ] && source {self.env_file}\n"

        try:
            with open(shell_config, "a", encoding="utf-8") as f:
                f.write(source_line)
            return True
        except Exception as e:
            print(f"添加到 {shell_config} 失败: {e}")
            return False

    def remove_source_from_shell_config(self, shell_config: Path) -> bool:
        """从 shell 配置中移除 source 语句"""
        if not self.is_env_sourced(shell_config):
            return True  # 没有需要移除的

        try:
            with open(shell_config, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 移除相关行
            new_lines = []
            skip_next = False
            for line in lines:
                if "Claude Retry Optimizer" in line:
                    skip_next = True
                    continue
                if skip_next and str(self.env_file) in line:
                    skip_next = False
                    continue
                new_lines.append(line)

            with open(shell_config, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        except Exception as e:
            print(f"从 {shell_config} 移除失败: {e}")
            return False

    def setup_env(self, max_retries: int, retry_interval_ms: int) -> bool:
        """设置环境变量（写入文件 + 添加到 shell 配置）"""
        # 1. 写入环境变量文件
        if not self.write_env_file(max_retries, retry_interval_ms):
            return False

        # 2. 添加到 shell 配置
        shell_configs = self.get_shell_config_files()
        if not shell_configs:
            print("警告: 未找到 shell 配置文件（.bashrc / .zshrc / config.fish）")
            print(f"请手动在你的 shell 配置中添加: source {self.env_file}")
            return True

        success = True
        for config in shell_configs:
            if not self.add_source_to_shell_config(config):
                success = False

        return success

    def cleanup_env(self) -> bool:
        """清理环境变量（删除文件 + 从 shell 配置移除）"""
        # 1. 从 shell 配置移除
        shell_configs = self.get_shell_config_files()
        for config in shell_configs:
            self.remove_source_from_shell_config(config)

        # 2. 删除环境变量文件
        return self.remove_env_file()

    def get_current_env_values(self) -> dict:
        """获取当前环境变量值"""
        return {
            "CLAUDE_CODE_MAX_RETRIES": os.environ.get("CLAUDE_CODE_MAX_RETRIES"),
            "CLAUDE_CODE_RETRY_INTERVAL_MS": os.environ.get("CLAUDE_CODE_RETRY_INTERVAL_MS"),
        }
