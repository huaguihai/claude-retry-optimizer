#!/usr/bin/env python3
"""
test_config.py - 测试 config.py 模块
"""

import json
import tempfile
from pathlib import Path

from claude_retry_optimizer.config import ConfigManager


def test_config_manager():
    """测试配置管理器"""
    # 使用临时文件替代真实配置文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_config = Path(f.name)

    # 创建配置管理器并替换配置文件路径
    manager = ConfigManager()
    original_path = manager.config_path
    manager.config_path = temp_config

    try:
        # 测试加载（不存在）
        config = manager.load()
        assert config is None
        print(f"✓ load (not exists): None")

        # 测试获取状态（未配置）
        status = manager.get_status()
        assert status == "未配置（使用官方默认）"
        print(f"✓ get_status (not configured): {status}")

        # 测试创建配置
        new_config = manager.create_config(
            binary_path="/usr/local/bin/claude",
            mode="quick",
            max_retries=50,
            retry_interval_ms=1000,
        )
        assert new_config["status"] == "configured"
        assert new_config["mode"] == "quick"
        assert new_config["config"]["max_retries"] == 50
        print(f"✓ create_config: {new_config['mode']}")

        # 测试保存配置
        assert manager.save(new_config)
        assert temp_config.exists()
        print(f"✓ save: {temp_config}")

        # 测试加载（已存在）
        loaded_config = manager.load()
        assert loaded_config is not None
        assert loaded_config["mode"] == "quick"
        print(f"✓ load (exists): {loaded_config['mode']}")

        # 测试获取状态（已配置）
        status = manager.get_status()
        assert status == "已配置 - 快捷模式"
        print(f"✓ get_status (configured): {status}")

        # 测试配置摘要
        summary = manager.get_config_summary()
        assert "50" in summary
        assert "1000" in summary
        print(f"✓ get_config_summary: {summary}")

        # 测试标记失效
        assert manager.invalidate()
        config = manager.load()
        assert config["status"] == "invalid"
        status = manager.get_status()
        assert status == "配置已失效（需要重新配置）"
        print(f"✓ invalidate: {status}")

        # 测试删除配置
        assert manager.remove()
        assert not temp_config.exists()
        print(f"✓ remove: config file deleted")

    finally:
        # 恢复原路径
        manager.config_path = original_path
        # 清理临时文件
        if temp_config.exists():
            temp_config.unlink()


def test_presets():
    """测试预设方案"""
    manager = ConfigManager()

    # 测试快捷模式预设
    quick_preset = manager.PRESETS["quick"]
    assert quick_preset["max_retries"] == 50
    assert quick_preset["retry_interval_ms"] == 1000
    print(f"✓ PRESETS['quick']: {quick_preset['name']}")

    # 测试自定义模式预设
    custom_preset = manager.PRESETS["custom"]
    assert custom_preset["name"] == "自定义配置"
    print(f"✓ PRESETS['custom']: {custom_preset['name']}")


def run_all_tests():
    """运行所有测试"""
    print("\n=== 测试 config.py ===\n")

    test_config_manager()
    test_presets()

    print("\n✅ 所有 config.py 测试通过！\n")


if __name__ == "__main__":
    run_all_tests()
