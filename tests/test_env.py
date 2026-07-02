#!/usr/bin/env python3
"""
test_env.py - 测试 env.py 模块
"""

import os
import tempfile
from pathlib import Path

from claude_retry_optimizer.env import EnvManager


def test_generate_env_content():
    """测试生成环境变量内容"""
    manager = EnvManager()
    content = manager.generate_env_content(50, 1000)

    assert "CLAUDE_CODE_MAX_RETRIES=50" in content
    assert "CLAUDE_CODE_RETRY_INTERVAL_MS=1000" in content
    print(f"✓ generate_env_content: {len(content)} chars")


def test_write_and_remove_env_file():
    """测试写入和删除环境变量文件"""
    manager = EnvManager()

    # 使用临时文件
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_env = Path(f.name)

    original_path = manager.env_file
    manager.env_file = temp_env

    try:
        # 测试写入
        assert manager.write_env_file(50, 1000)
        assert temp_env.exists()

        with open(temp_env, "r") as f:
            content = f.read()
        assert "CLAUDE_CODE_MAX_RETRIES=50" in content
        print(f"✓ write_env_file: {temp_env}")

        # 测试删除
        assert manager.remove_env_file()
        assert not temp_env.exists()
        print(f"✓ remove_env_file: deleted")

    finally:
        manager.env_file = original_path
        if temp_env.exists():
            temp_env.unlink()


def test_shell_config_operations():
    """测试 shell 配置操作"""
    manager = EnvManager()

    # 使用临时文件模拟 shell 配置
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        temp_shell_config = Path(f.name)
        f.write("# Existing shell config\nexport PATH=/usr/bin\n")

    try:
        # 测试检查是否已 source（应该没有）
        assert not manager.is_env_sourced(temp_shell_config)
        print(f"✓ is_env_sourced (before): False")

        # 测试添加 source 语句
        assert manager.add_source_to_shell_config(temp_shell_config)

        with open(temp_shell_config, "r") as f:
            content = f.read()
        assert "Claude Retry Optimizer" in content
        assert str(manager.env_file) in content
        print(f"✓ add_source_to_shell_config: added")

        # 测试检查是否已 source（应该有）
        assert manager.is_env_sourced(temp_shell_config)
        print(f"✓ is_env_sourced (after): True")

        # 测试重复添加（应该跳过）
        assert manager.add_source_to_shell_config(temp_shell_config)
        with open(temp_shell_config, "r") as f:
            content = f.read()
        # 确认只有一个
        assert content.count("Claude Retry Optimizer") == 1
        print(f"✓ add_source_to_shell_config (duplicate): skipped")

        # 测试移除 source 语句
        assert manager.remove_source_from_shell_config(temp_shell_config)

        with open(temp_shell_config, "r") as f:
            content = f.read()
        assert "Claude Retry Optimizer" not in content
        assert str(manager.env_file) not in content
        print(f"✓ remove_source_from_shell_config: removed")

    finally:
        temp_shell_config.unlink()


def test_get_shell_config_files():
    """测试获取 shell 配置文件"""
    manager = EnvManager()
    configs = manager.get_shell_config_files()

    # 至少应该找到一个（.bashrc 或 .zshrc）
    print(f"✓ get_shell_config_files: {len(configs)} found")
    for config in configs:
        print(f"  - {config}")


def test_get_current_env_values():
    """测试获取当前环境变量值"""
    manager = EnvManager()
    values = manager.get_current_env_values()

    assert "CLAUDE_CODE_MAX_RETRIES" in values
    assert "CLAUDE_CODE_RETRY_INTERVAL_MS" in values
    print(f"✓ get_current_env_values: {values}")


def run_all_tests():
    """运行所有测试"""
    print("\n=== 测试 env.py ===\n")

    test_generate_env_content()
    test_write_and_remove_env_file()
    test_shell_config_operations()
    test_get_shell_config_files()
    test_get_current_env_values()

    print("\n✅ 所有 env.py 测试通过！\n")


if __name__ == "__main__":
    run_all_tests()
