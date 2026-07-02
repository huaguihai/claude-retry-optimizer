#!/usr/bin/env python3
"""
run_all_tests.py - 运行所有测试
"""

import sys

from test_binary import run_all_tests as test_binary
from test_patcher import run_all_tests as test_patcher
from test_config import run_all_tests as test_config
from test_env import run_all_tests as test_env


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Claude Retry Optimizer - 回归测试")
    print("=" * 60)

    try:
        # 运行各模块测试
        test_binary()
        test_patcher()
        test_config()
        test_env()

        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        print()

        return 0

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
