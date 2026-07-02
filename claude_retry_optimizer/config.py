#!/usr/bin/env python3
"""
config.py - 配置管理模块
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """配置管理器"""

    CONFIG_FILE = Path.home() / ".claude-retry-optimizer.json"

    # 预设方案
    PRESETS = {
        "quick": {
            "name": "快捷配置",
            "description": "推荐配置：重试 50 次，间隔 1 秒",
            "max_retries": 50,
            "retry_interval_ms": 1000,
        },
        "custom": {
            "name": "自定义配置",
            "description": "手动设置参数",
        }
    }

    def __init__(self):
        self.config_path = self.CONFIG_FILE

    def load(self) -> Optional[Dict[str, Any]]:
        """加载配置"""
        if not self.config_path.exists():
            return None

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None

    def save(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            # 添加时间戳
            config["last_modified"] = datetime.now().isoformat()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get_status(self) -> str:
        """获取当前状态

        Returns:
            "未配置", "已配置 - 快捷模式", "已配置 - 自定义模式", "配置已失效"
        """
        config = self.load()
        if not config:
            return "未配置（使用官方默认）"

        status = config.get("status", "unknown")
        mode = config.get("mode", "unknown")

        if status == "configured":
            if mode == "quick":
                return "已配置 - 快捷模式"
            elif mode == "custom":
                return "已配置 - 自定义模式"
            else:
                return "已配置"
        elif status == "invalid":
            return "配置已失效（需要重新配置）"
        else:
            return "未配置（使用官方默认）"

    def create_config(
        self,
        binary_path: str,
        mode: str,
        max_retries: int,
        retry_interval_ms: int,
    ) -> Dict[str, Any]:
        """创建新配置

        Args:
            binary_path: 二进制路径
            mode: 模式 ("quick" 或 "custom")
            max_retries: 最大重试次数
            retry_interval_ms: 重试间隔（毫秒）

        Returns:
            配置字典
        """
        return {
            "version": "1.0.0",
            "status": "configured",
            "mode": mode,
            "config": {
                "max_retries": max_retries,
                "retry_interval_ms": retry_interval_ms,
            },
            "binary_path": binary_path,
            "last_modified": datetime.now().isoformat(),
        }

    def invalidate(self) -> bool:
        """标记配置为失效（例如二进制更新后）"""
        config = self.load()
        if not config:
            return True

        config["status"] = "invalid"
        return self.save(config)

    def remove(self) -> bool:
        """删除配置文件"""
        if self.config_path.exists():
            try:
                self.config_path.unlink()
                return True
            except Exception as e:
                print(f"删除配置文件失败: {e}")
                return False
        return True

    def get_config_summary(self) -> Optional[str]:
        """获取配置摘要（用于显示）"""
        config = self.load()
        if not config or config.get("status") != "configured":
            return None

        cfg = config.get("config", {})
        max_retries = cfg.get("max_retries", "?")
        interval = cfg.get("retry_interval_ms", "?")

        return f"重试 {max_retries} 次，间隔 {interval}ms"
