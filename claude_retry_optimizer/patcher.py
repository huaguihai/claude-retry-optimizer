#!/usr/bin/env python3
"""
patcher.py - Patch 逻辑模块（基于原 patch-retry.py）
"""

import re
from typing import Optional, Tuple, List


def find_all(data: bytes, pattern: bytes) -> List[int]:
    """查找所有匹配的偏移量"""
    offsets = []
    start = 0
    while True:
        idx = data.find(pattern, start)
        if idx == -1:
            break
        offsets.append(idx)
        start = idx + 1
    return offsets


def find_nearest(data: bytes, pattern: bytes, ref_offset: int, max_dist: int) -> Optional[int]:
    """查找最接近参考偏移量的匹配"""
    offsets = find_all(data, pattern)
    best = None
    best_dist = max_dist
    for off in offsets:
        dist = abs(off - ref_offset)
        if dist < best_dist:
            best_dist = dist
            best = off
    return best


def discover_retry_cap_var(data: bytes) -> Optional[bytes]:
    """发现重试次数上限变量名

    代码模式: CLAUDE_CODE_MAX_RETRIES=${e} clamped to ${VARNAME}
    其中 VARNAME=15 是我们要修改的上限
    """
    for m in re.finditer(rb'CLAUDE_CODE_MAX_RETRIES=\$\{', data):
        ctx = data[m.start():m.start() + 200]
        clamped = re.search(rb'clamped to \$\{([a-zA-Z_$][a-zA-Z0-9_$]*)\}', ctx)
        if clamped:
            return clamped.group(1)
    return None


def discover_backoff_base_var(data: bytes) -> Optional[bytes]:
    """发现退避基础延迟变量名

    代码模式: Math.min(VARNAME*Math.pow(2,e-1),n)
    其中 VARNAME=500 是基础延迟（毫秒）
    """
    for m in re.finditer(rb'Math\.min\(([a-zA-Z_$][a-zA-Z0-9_$]*)\*Math\.pow\(2,e-1\)', data):
        return m.group(1)
    return None


def discover_rate_limit_vars(data: bytes) -> Tuple[Optional[bytes], Optional[bytes], Optional[bytes]]:
    """发现 rate-limit 相关变量名

    返回: (fallback_var, min_var, threshold_var)
    """
    fallback_var = None
    min_var = None
    threshold_var = None

    # 在 "rate_limit" 附近搜索
    for marker in [b'rate_limit', b'retry_after']:
        idx = data.find(marker)
        while idx != -1:
            ctx = data[max(0, idx - 1000):idx + 1000]

            # 新版模式: Math.min(G7(l,x,VAR1),VAR2)
            m = re.search(rb'Math\.min\(G7\([a-zA-Z_$][a-zA-Z0-9_$]*,[a-zA-Z_$][a-zA-Z0-9_$]*,([a-zA-Z_$][a-zA-Z0-9_$]*)\),([a-zA-Z_$][a-zA-Z0-9_$]*)\)', ctx)
            if m:
                min_var = m.group(1)
                fallback_var = m.group(2)

            # 阈值模式: I>VAR
            for m2 in re.finditer(rb'[Ii]>([a-zA-Z_$][a-zA-Z0-9_$]*)', ctx):
                var = m2.group(1)
                pattern = var + rb'=\d+'
                if re.search(pattern, data):
                    threshold_var = var
                    break

            if fallback_var and min_var and threshold_var:
                return fallback_var, min_var, threshold_var

            idx = data.find(marker, idx + 1)

    return fallback_var, min_var, threshold_var


def apply_byte_patch(
    data: bytearray,
    desc: str,
    search: bytes,
    replace: bytes,
    stats: dict,
    hint_offset: Optional[int] = None,
    max_dist: int = 0,
    verbose: bool = True
) -> bytearray:
    """应用单个字节替换

    Args:
        data: 二进制数据
        desc: 描述
        search: 搜索模式
        replace: 替换内容
        stats: 统计字典
        hint_offset: 提示偏移量
        max_dist: 最大距离
        verbose: 是否输出详细信息

    Returns:
        修改后的数据
    """
    if len(search) != len(replace):
        if verbose:
            print(f"  跳过: {desc} — 字节长度不匹配 ({len(search)} vs {len(replace)})")
        stats["failed"] += 1
        return data

    if hint_offset is not None:
        offset = find_nearest(data, search, hint_offset, max_dist)
        if offset is None:
            if verbose:
                print(f"  警告: 在提示位置附近未找到模式: {desc}")
            stats["failed"] += 1
            return data
    else:
        offsets = find_all(data, search)
        if not offsets:
            if verbose:
                print(f"  警告: 未找到模式: {desc}")
            stats["failed"] += 1
            return data
        offset = offsets[0]

    # 验证字节匹配
    actual = data[offset:offset + len(search)]
    if actual != search:
        if verbose:
            print(f"  跳过: {desc} — 字节不匹配 @ offset {offset}")
        stats["failed"] += 1
        return data

    if verbose:
        print(f"  ✓ {desc} @ offset {offset}")
    data[offset:offset + len(replace)] = replace
    stats["applied"] += 1
    return data


class PatchConfig:
    """Patch 配置"""
    def __init__(
        self,
        max_retries: int = 50,
        retry_interval_ms: int = 1000,
        rate_limit_max_delay_ms: int = 10000,
        rate_limit_min_delay_ms: int = 1000,
        rate_limit_threshold_ms: int = 30000,
    ):
        self.max_retries = max_retries
        self.retry_interval_ms = retry_interval_ms
        self.rate_limit_max_delay_ms = rate_limit_max_delay_ms
        self.rate_limit_min_delay_ms = rate_limit_min_delay_ms
        self.rate_limit_threshold_ms = rate_limit_threshold_ms


def apply_patches(data: bytearray, config: PatchConfig, verbose: bool = True) -> Tuple[bytearray, dict]:
    """应用所有 patch

    Args:
        data: 二进制数据
        config: Patch 配置
        verbose: 是否输出详细信息

    Returns:
        (修改后的数据, 统计信息)
    """
    stats = {"applied": 0, "failed": 0}

    if verbose:
        print("\n=== 发现版本特定模式 ===")

    # 发现变量名
    retry_cap_var = discover_retry_cap_var(data)
    if retry_cap_var:
        if verbose:
            print(f"  重试上限变量: {retry_cap_var.decode()}")
    else:
        if verbose:
            print("  警告: 未找到重试上限变量")

    backoff_base_var = discover_backoff_base_var(data)
    if backoff_base_var:
        if verbose:
            print(f"  退避基础变量: {backoff_base_var.decode()}")
    else:
        if verbose:
            print("  警告: 未找到退避基础变量")

    rl_fallback_var, rl_min_var, rl_threshold_var = discover_rate_limit_vars(data)
    if rl_fallback_var:
        if verbose:
            print(f"  Rate-limit 降级变量: {rl_fallback_var.decode()}")
    if rl_min_var:
        if verbose:
            print(f"  Rate-limit 最小延迟变量: {rl_min_var.decode()}")
    if rl_threshold_var:
        if verbose:
            print(f"  Rate-limit 阈值变量: {rl_threshold_var.decode()}")

    # 保存 backoff base 提示偏移量
    backoff_base_hint_offset = None
    if backoff_base_var:
        search = backoff_base_var + b"=500"
        hits = find_all(data, search)
        if hits:
            backoff_base_hint_offset = hits[0]
            if verbose:
                print(f"  保存退避基础提示偏移: {backoff_base_hint_offset}")

    # Patch 1: 移除 15 次重试上限
    if verbose:
        print("\n=== Patch 1: 移除重试上限 ===")
    if retry_cap_var:
        # 确保新值是两位数（字节长度相同）
        if config.max_retries > 99:
            config.max_retries = 99
        search = retry_cap_var + b"=15"
        replace = retry_cap_var + f"={config.max_retries:02d}".encode()
        data = apply_byte_patch(
            data,
            f"提高重试上限 15 → {config.max_retries} ({retry_cap_var.decode()})",
            search,
            replace,
            stats,
            verbose=verbose
        )
    else:
        if verbose:
            print("  跳过: 重试上限变量未发现")
        stats["failed"] += 1

    # Patch 2a: 修改退避基础延迟
    if verbose:
        print("\n=== Patch 2: 替换指数退避为固定间隔 ===")
    if backoff_base_var:
        search = backoff_base_var + b"=500"
        replace = backoff_base_var + b"=1e3"
        data = apply_byte_patch(
            data,
            f"修改退避基础 500ms → 1000ms ({backoff_base_var.decode()})",
            search,
            replace,
            stats,
            verbose=verbose
        )
    else:
        if verbose:
            print("  跳过: 退避基础变量未发现")
        stats["failed"] += 1

    # Patch 2b: 禁用指数增长
    data = apply_byte_patch(
        data,
        "修改 pow 基数 2→1 (禁用指数增长)",
        b"Math.pow(2,e-1)",
        b"Math.pow(1,e-1)",
        stats,
        hint_offset=backoff_base_hint_offset,
        max_dist=100000,
        verbose=verbose
    )

    # Patch 3: 修改 Anthropic SDK 内置重试退避
    if verbose:
        print("\n=== Patch 3: 修改 Anthropic SDK 内置重试退避 ===")
    data = apply_byte_patch(
        data,
        "修改 SDK 退避 0.5*2^o → 1.0*1^o (固定 ~1s 延迟)",
        b"0.5*Math.pow(2,o)",
        b"1.0*Math.pow(1,o)",
        stats,
        verbose=verbose
    )

    # Patch 4: 降低 rate-limit 降级延迟
    if verbose:
        print("\n=== Patch 4: 降低 rate-limit 降级延迟 ===")

    if rl_fallback_var:
        # 最大延迟: 21600000ms (6h) → 01000000ms (10s)
        search = rl_fallback_var + b"=21600000"
        replace = rl_fallback_var + b"=01000000"
        data = apply_byte_patch(
            data,
            f"降低 rate-limit 最大延迟 6h → 10s ({rl_fallback_var.decode()})",
            search,
            replace,
            stats,
            verbose=verbose
        )
    else:
        if verbose:
            print("  跳过: Rate-limit 降级变量未发现")
        stats["failed"] += 1

    if rl_min_var:
        # 基础延迟: 300000ms (5min) → 001000ms (1s)
        search = rl_min_var + b"=300000"
        replace = rl_min_var + b"=001000"
        data = apply_byte_patch(
            data,
            f"降低 rate-limit 基础延迟 5min → 1s ({rl_min_var.decode()})",
            search,
            replace,
            stats,
            verbose=verbose
        )
    else:
        if verbose:
            print("  跳过: Rate-limit 最小延迟变量未发现")
        stats["failed"] += 1

    if rl_threshold_var:
        # 阈值: 60000ms (60s) → 30000ms (30s)
        search = rl_threshold_var + b"=60000"
        replace = rl_threshold_var + b"=30000"
        data = apply_byte_patch(
            data,
            f"降低 rate-limit 阈值 60s → 30s ({rl_threshold_var.decode()})",
            search,
            replace,
            stats,
            verbose=verbose
        )
    else:
        if verbose:
            print("  跳过: Rate-limit 阈值变量未发现")
        stats["failed"] += 1

    return data, stats
