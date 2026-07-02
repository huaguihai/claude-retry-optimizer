#!/usr/bin/env python3
"""
test_windows_compat.py - 测试 Windows 兼容性
"""

import platform
from claude_retry_optimizer.binary import find_binary


def test_find_binary_cross_platform():
    """测试跨平台二进制查找"""
    print(f"\n=== 测试 Windows 兼容性 ===\n")
    print(f"当前平台: {platform.system()}")
    print(f"架构: {platform.machine()}")
    print()

    # 测试查找二进制
    binary_path = find_binary()

    if binary_path:
        print(f"✓ 找到 Claude Code: {binary_path}")

        # 验证文件存在
        import os
        if os.path.isfile(binary_path):
            size = os.path.getsize(binary_path)
            print(f"✓ 文件存在，大小: {size} 字节 ({size / (1024*1024):.1f} MB)")
        else:
            print(f"✗ 文件不存在（路径错误）")
    else:
        print(f"✗ 未找到 Claude Code")
        print(f"\n提示:")
        print(f"  - 请确认已安装: npm install -g @anthropic-ai/claude-code")
        print(f"  - 或者 Claude Code 可能未添加到 PATH")

    print()
    print("✅ 跨平台兼容性测试完成")
    print()


if __name__ == "__main__":
    test_find_binary_cross_platform()
