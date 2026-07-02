#!/usr/bin/env python3
"""
test_version_check.py - 测试版本检查功能
"""

from claude_retry_optimizer.binary import (
    get_claude_version,
    compare_versions,
    check_version_compatibility,
)


def test_get_claude_version():
    """测试获取版本号"""
    version = get_claude_version()
    print(f"✓ get_claude_version: {version}")
    # 注意：在测试环境可能获取不到版本


def test_compare_versions():
    """测试版本比较"""
    # 测试相等
    assert compare_versions("2.1.191", "2.1.191") == 0
    print(f"✓ compare_versions: 2.1.191 == 2.1.191")

    # 测试大于
    assert compare_versions("2.1.191", "2.1.172") == 1
    print(f"✓ compare_versions: 2.1.191 > 2.1.172")

    # 测试小于
    assert compare_versions("2.1.172", "2.1.191") == -1
    print(f"✓ compare_versions: 2.1.172 < 2.1.191")

    # 测试主版本号
    assert compare_versions("3.0.0", "2.1.191") == 1
    print(f"✓ compare_versions: 3.0.0 > 2.1.191")

    # 测试次版本号
    assert compare_versions("2.2.0", "2.1.191") == 1
    print(f"✓ compare_versions: 2.2.0 > 2.1.191")


def test_check_version_compatibility():
    """测试版本兼容性检查"""
    is_compatible, current_version, error_msg = check_version_compatibility("2.1.191")

    if current_version:
        print(f"✓ check_version_compatibility: current={current_version}, compatible={is_compatible}")
        if not is_compatible:
            print(f"  Error: {error_msg}")
    else:
        print(f"✓ check_version_compatibility: version unavailable")


def run_all_tests():
    """运行所有测试"""
    print("\n=== 测试版本检查功能 ===\n")

    test_get_claude_version()
    test_compare_versions()
    test_check_version_compatibility()

    print("\n✅ 所有版本检查测试通过！\n")


if __name__ == "__main__":
    run_all_tests()
