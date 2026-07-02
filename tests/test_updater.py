#!/usr/bin/env python3
"""
test_updater.py - 测试更新模块
"""

from claude_retry_optimizer.updater import (
    get_current_version,
    compare_versions,
    check_for_updates,
)


def test_get_current_version():
    """测试获取当前版本"""
    version = get_current_version()
    assert version == "1.0.0"
    print(f"✓ get_current_version: {version}")


def test_compare_versions():
    """测试版本比较"""
    # 相等
    assert compare_versions("1.0.0", "1.0.0") == 0
    print(f"✓ compare_versions: 1.0.0 == 1.0.0")

    # 大于
    assert compare_versions("1.0.1", "1.0.0") == 1
    print(f"✓ compare_versions: 1.0.1 > 1.0.0")

    # 小于
    assert compare_versions("1.0.0", "1.0.1") == -1
    print(f"✓ compare_versions: 1.0.0 < 1.0.1")

    # 主版本号
    assert compare_versions("2.0.0", "1.9.9") == 1
    print(f"✓ compare_versions: 2.0.0 > 1.9.9")


def test_check_for_updates():
    """测试检查更新（静默模式）"""
    has_update, latest_version = check_for_updates(silent=True)

    if latest_version:
        print(f"✓ check_for_updates: latest={latest_version}, has_update={has_update}")
    else:
        print(f"✓ check_for_updates: 无法连接到 GitHub")


def run_all_tests():
    """运行所有测试"""
    print("\n=== 测试更新模块 ===\n")

    test_get_current_version()
    test_compare_versions()
    test_check_for_updates()

    print("\n✅ 所有更新模块测试通过！\n")


if __name__ == "__main__":
    run_all_tests()
