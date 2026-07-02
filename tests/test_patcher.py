#!/usr/bin/env python3
"""
test_patcher.py - 测试 patcher.py 模块
"""

from claude_retry_optimizer.patcher import (
    find_all,
    find_nearest,
    discover_retry_cap_var,
    discover_backoff_base_var,
    discover_rate_limit_vars,
    apply_byte_patch,
    PatchConfig,
    apply_patches,
)


def test_find_all():
    """测试查找所有匹配"""
    data = b"hello world hello universe hello"
    pattern = b"hello"
    offsets = find_all(data, pattern)
    assert offsets == [0, 12, 27]
    print(f"✓ find_all: {offsets}")


def test_find_nearest():
    """测试查找最近的匹配"""
    data = b"AAA" + b"X" * 100 + b"BBB" + b"X" * 50 + b"CCC"
    pattern = b"BBB"

    # 从位置 50 开始查找 BBB（最近的是 103）
    offset = find_nearest(data, pattern, 50, 200)
    assert offset == 103
    print(f"✓ find_nearest: {offset}")


def test_discover_retry_cap_var():
    """测试发现重试上限变量"""
    # 模拟真实代码片段
    data = b'CLAUDE_CODE_MAX_RETRIES=${e} clamped to ${maxRetries}'
    var = discover_retry_cap_var(data)
    assert var == b"maxRetries"
    print(f"✓ discover_retry_cap_var: {var.decode()}")


def test_discover_backoff_base_var():
    """测试发现退避基础变量"""
    # 模拟真实代码片段
    data = b'Math.min(baseDelay*Math.pow(2,e-1),n)'
    var = discover_backoff_base_var(data)
    assert var == b"baseDelay"
    print(f"✓ discover_backoff_base_var: {var.decode()}")


def test_apply_byte_patch():
    """测试应用字节替换"""
    data = bytearray(b"maxRetries=15 someOtherCode")
    stats = {"applied": 0, "failed": 0}

    # 测试成功替换
    result = apply_byte_patch(
        data,
        "Test patch",
        b"maxRetries=15",
        b"maxRetries=50",
        stats,
        verbose=False
    )
    assert result == bytearray(b"maxRetries=50 someOtherCode")
    assert stats["applied"] == 1
    print(f"✓ apply_byte_patch: success")

    # 测试长度不匹配
    stats = {"applied": 0, "failed": 0}
    result = apply_byte_patch(
        data,
        "Test patch",
        b"maxRetries=15",
        b"maxRetries=100",  # 长度不同
        stats,
        verbose=False
    )
    assert stats["failed"] == 1
    print(f"✓ apply_byte_patch: length mismatch detected")


def test_patch_config():
    """测试配置类"""
    config = PatchConfig(
        max_retries=50,
        retry_interval_ms=1000,
    )
    assert config.max_retries == 50
    assert config.retry_interval_ms == 1000
    print(f"✓ PatchConfig: max_retries={config.max_retries}, interval={config.retry_interval_ms}ms")


def test_apply_patches():
    """测试应用所有 patch"""
    # 创建模拟的二进制数据（包含需要 patch 的模式）
    data = bytearray(
        b"CLAUDE_CODE_MAX_RETRIES=${e} clamped to ${r15}\n"
        b"r15=15\n"
        b"Math.min(b500*Math.pow(2,e-1),n)\n"
        b"b500=500\n"
        b"Math.pow(2,e-1)\n"
        b"0.5*Math.pow(2,o)\n"
        b"f21=21600000\n"
        b"m30=300000\n"
        b"t60=60000\n"
    )

    config = PatchConfig(max_retries=50, retry_interval_ms=1000)

    patched_data, stats = apply_patches(data, config, verbose=False)

    # 检查统计
    assert stats["applied"] > 0
    print(f"✓ apply_patches: {stats['applied']} patches applied, {stats['failed']} failed")


def run_all_tests():
    """运行所有测试"""
    print("\n=== 测试 patcher.py ===\n")

    test_find_all()
    test_find_nearest()
    test_discover_retry_cap_var()
    test_discover_backoff_base_var()
    test_apply_byte_patch()
    test_patch_config()
    test_apply_patches()

    print("\n✅ 所有 patcher.py 测试通过！\n")


if __name__ == "__main__":
    run_all_tests()
