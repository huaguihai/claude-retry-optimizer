#!/usr/bin/env python3
"""
test_binary.py - 测试 binary.py 模块
"""

import os
import tempfile
import shutil
from pathlib import Path

from claude_retry_optimizer.binary import (
    find_binary,
    get_backup_path,
    has_backup,
    create_backup,
    restore_from_backup,
    remove_backup,
    get_binary_info,
    read_binary,
    write_binary,
)


def test_find_binary():
    """测试查找二进制"""
    binary_path = find_binary()
    print(f"✓ find_binary: {binary_path}")
    # 注意：在测试环境可能找不到 claude，这是正常的
    if binary_path:
        assert os.path.isfile(binary_path)


def test_backup_operations():
    """测试备份操作"""
    # 创建临时文件模拟二进制
    with tempfile.NamedTemporaryFile(delete=False) as f:
        test_binary = f.name
        f.write(b"test binary content")

    try:
        # 测试备份路径
        backup_path = get_backup_path(test_binary)
        assert backup_path == test_binary + ".orig"
        print(f"✓ get_backup_path: {backup_path}")

        # 测试检查备份（应该不存在）
        assert not has_backup(test_binary)
        print(f"✓ has_backup (before): False")

        # 测试创建备份
        assert create_backup(test_binary)
        assert os.path.isfile(backup_path)
        assert has_backup(test_binary)
        print(f"✓ create_backup: {backup_path}")

        # 测试创建备份（已存在）
        assert create_backup(test_binary)  # 应该返回 True（已存在）
        print(f"✓ create_backup (already exists): True")

        # 修改原文件
        with open(test_binary, "wb") as f:
            f.write(b"modified content")

        # 测试恢复备份
        assert restore_from_backup(test_binary)
        with open(test_binary, "rb") as f:
            content = f.read()
        assert content == b"test binary content"
        print(f"✓ restore_from_backup: content restored")

        # 测试删除备份
        assert remove_backup(test_binary)
        assert not os.path.isfile(backup_path)
        assert not has_backup(test_binary)
        print(f"✓ remove_backup: {backup_path} removed")

    finally:
        # 清理
        if os.path.isfile(test_binary):
            os.unlink(test_binary)
        backup_path = get_backup_path(test_binary)
        if os.path.isfile(backup_path):
            os.unlink(backup_path)


def test_binary_info():
    """测试获取二进制信息"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        test_binary = f.name
        f.write(b"test" * 100)

    try:
        info = get_binary_info(test_binary)
        assert info["path"] == test_binary
        assert info["size"] == 400
        assert not info["has_backup"]
        print(f"✓ get_binary_info: {info}")

    finally:
        os.unlink(test_binary)


def test_read_write_binary():
    """测试读写二进制"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        test_binary = f.name
        original_content = b"original binary data"
        f.write(original_content)

    try:
        # 测试读取
        data = read_binary(test_binary)
        assert data == bytearray(original_content)
        print(f"✓ read_binary: {len(data)} bytes")

        # 测试写入
        new_data = bytearray(b"new binary data")
        assert write_binary(test_binary, new_data)

        # 验证写入
        with open(test_binary, "rb") as f:
            content = f.read()
        assert content == bytes(new_data)
        print(f"✓ write_binary: {len(new_data)} bytes")

    finally:
        os.unlink(test_binary)


def run_all_tests():
    """运行所有测试"""
    print("\n=== 测试 binary.py ===\n")

    test_find_binary()
    test_backup_operations()
    test_binary_info()
    test_read_write_binary()

    print("\n✅ 所有 binary.py 测试通过！\n")


if __name__ == "__main__":
    run_all_tests()
