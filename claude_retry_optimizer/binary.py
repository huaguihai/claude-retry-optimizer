#!/usr/bin/env python3
"""
binary.py - Claude Code 二进制文件操作模块
"""

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def find_binary() -> Optional[str]:
    """查找 Claude Code 二进制文件路径（跨平台）"""

    # 方法 1: 使用 shutil.which（跨平台）
    # 注意：Windows 上可能返回 .cmd 包装器，我们需要跳过它找真正的 .exe
    try:
        claude_path = shutil.which("claude")
        if claude_path:
            path = os.path.realpath(claude_path)
            # 如果是 .cmd 或 .bat 包装器（Windows），跳过，继续尝试其他方法
            if os.path.isfile(path) and not path.lower().endswith(('.cmd', '.bat')):
                return path
    except Exception:
        pass

    # 方法 2: 通过 npm root -g 查找
    try:
        # Windows 上需要 shell=True 才能执行 .cmd 文件
        result = subprocess.run(
            ["npm", "root", "-g"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=(platform.system() == "Windows")
        )
        if result.returncode == 0:
            npm_root = result.stdout.strip()

            # 根据平台构建候选路径
            if platform.system() == "Windows":
                # Windows 上尝试多个可能的位置
                npm_bin = os.path.dirname(npm_root)  # npm bin 目录（npm_root 的上一级）

                candidates = [
                    # 标准位置：node_modules/@anthropic-ai/claude-code/bin/claude.exe
                    os.path.join(npm_root, "@anthropic-ai", "claude-code", "bin", "claude.exe"),

                    # npm bin 目录中的包装器可能指向的位置
                    os.path.join(npm_root, "@anthropic-ai", "claude-code", "claude.exe"),

                    # .bin 目录（某些 npm 版本）
                    os.path.join(npm_root, ".bin", "claude.exe"),

                    # win32 特定包
                    os.path.join(npm_root, "@anthropic-ai", "claude-code-win32-x64", "claude.exe"),

                    # 直接在 npm bin 目录查找（通过 node_modules 找到）
                    os.path.join(npm_bin, "node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe"),
                ]
            elif platform.system() == "Darwin":  # macOS
                candidates = [
                    os.path.join(npm_root, "@anthropic-ai", "claude-code-darwin-arm64", "claude"),
                    os.path.join(npm_root, "@anthropic-ai", "claude-code-darwin-x64", "claude"),
                ]
            else:  # Linux
                candidates = [
                    os.path.join(npm_root, "@anthropic-ai", "claude-code-linux-x64", "claude"),
                    os.path.join(npm_root, "@anthropic-ai", "claude-code-linux-arm64", "claude"),
                ]

            for c in candidates:
                if os.path.isfile(c):
                    return os.path.realpath(c)
    except Exception:
        pass

    # 方法 3: Windows 特定路径（APPDATA）
    if platform.system() == "Windows":
        try:
            appdata = os.environ.get("APPDATA")
            if appdata:
                candidates = [
                    # APPDATA/npm/node_modules 路径
                    os.path.join(appdata, "npm", "node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe"),
                    os.path.join(appdata, "npm", "node_modules", "@anthropic-ai", "claude-code", "claude.exe"),
                ]
                for c in candidates:
                    if os.path.isfile(c):
                        return os.path.realpath(c)
        except Exception:
            pass

    # 方法 4: 从 npm bin 目录通过 claude.cmd 找到真实路径（Windows）
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["npm", "bin", "-g"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            if result.returncode == 0:
                npm_bin = result.stdout.strip()
                claude_cmd = os.path.join(npm_bin, "claude.cmd")

                # 如果 claude.cmd 存在，读取它找到真实的 .exe 路径
                if os.path.isfile(claude_cmd):
                    try:
                        with open(claude_cmd, "r", encoding="utf-8") as f:
                            content = f.read()
                            # claude.cmd 通常包含类似这样的内容：
                            # @"%~dp0\node_modules\@anthropic-ai\claude-code\bin\claude.exe" %*
                            # 或 node "%~dp0\node_modules\@anthropic-ai\claude-code\bin\claude.js" %*

                            # 提取路径
                            import re
                            matches = re.findall(r'["\']?%~dp0\\(.+?\.exe)["\']?', content)
                            if matches:
                                # %~dp0 表示 .cmd 文件所在目录
                                relative_path = matches[0].replace('\\', os.sep)
                                full_path = os.path.join(npm_bin, relative_path)
                                if os.path.isfile(full_path):
                                    return os.path.realpath(full_path)
                    except Exception:
                        pass
        except Exception:
            pass

    return None


def get_backup_path(binary_path: str) -> str:
    """获取备份文件路径"""
    return binary_path + ".orig"


def has_backup(binary_path: str) -> bool:
    """检查是否存在备份"""
    backup_path = get_backup_path(binary_path)
    return os.path.isfile(backup_path)


def create_backup(binary_path: str) -> bool:
    """创建二进制备份"""
    if has_backup(binary_path):
        return True  # 已存在备份

    backup_path = get_backup_path(binary_path)
    try:
        shutil.copy2(binary_path, backup_path)
        return True
    except OSError as e:
        print(f"创建备份失败: {e}")
        return False


def restore_from_backup(binary_path: str) -> bool:
    """从备份恢复原版二进制"""
    backup_path = get_backup_path(binary_path)
    if not os.path.isfile(backup_path):
        print(f"备份文件不存在: {backup_path}")
        return False

    try:
        shutil.copy2(backup_path, binary_path)
        os.chmod(binary_path, 0o755)
        return True
    except OSError as e:
        print(f"恢复失败: {e}")
        return False


def remove_backup(binary_path: str) -> bool:
    """删除备份文件"""
    backup_path = get_backup_path(binary_path)
    if not os.path.isfile(backup_path):
        return True  # 已经不存在

    try:
        os.remove(backup_path)
        return True
    except OSError as e:
        print(f"删除备份失败: {e}")
        return False


def get_binary_info(binary_path: str) -> dict:
    """获取二进制文件信息"""
    stat = os.stat(binary_path)
    return {
        "path": binary_path,
        "size": stat.st_size,
        "mtime": stat.st_mtime,
        "has_backup": has_backup(binary_path),
    }


def read_binary(binary_path: str) -> Optional[bytearray]:
    """读取二进制文件内容"""
    try:
        with open(binary_path, "rb") as f:
            return bytearray(f.read())
    except Exception as e:
        print(f"读取二进制文件失败: {e}")
        return None


def write_binary(binary_path: str, data: bytearray) -> bool:
    """写入二进制文件（原子操作）"""
    import tempfile

    binary_dir = os.path.dirname(binary_path)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=binary_dir, suffix=".tmp")
        fd_closed = False
        try:
            os.write(fd, data)
            os.close(fd)
            fd_closed = True
            os.chmod(tmp_path, 0o755)
            os.replace(tmp_path, binary_path)
            return True
        except Exception:
            if not fd_closed:
                os.close(fd)
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except OSError as e:
        print(f"写入二进制文件失败: {e}")
        return False


def get_claude_version() -> Optional[str]:
    """获取 Claude Code 版本号

    Returns:
        版本号字符串（如 "2.1.191"）或 None
    """
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # 输出格式: "2.1.191 (Claude Code)"
            output = result.stdout.strip()
            match = re.search(r'(\d+\.\d+\.\d+)', output)
            if match:
                return match.group(1)
    except Exception:
        pass
    return None


def compare_versions(version1: str, version2: str) -> int:
    """比较两个版本号

    Args:
        version1: 版本号 1 (如 "2.1.191")
        version2: 版本号 2 (如 "2.1.172")

    Returns:
        1 if version1 > version2
        0 if version1 == version2
        -1 if version1 < version2
    """
    def parse_version(v: str) -> Tuple[int, int, int]:
        parts = v.split('.')
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    try:
        v1 = parse_version(version1)
        v2 = parse_version(version2)

        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0
    except Exception:
        return 0


def check_version_compatibility(min_version: str = "2.1.191") -> Tuple[bool, Optional[str], Optional[str]]:
    """检查版本兼容性

    Args:
        min_version: 最低要求版本

    Returns:
        (是否兼容, 当前版本, 错误信息)
    """
    current_version = get_claude_version()

    if current_version is None:
        return False, None, "无法获取 Claude Code 版本"

    if compare_versions(current_version, min_version) < 0:
        return False, current_version, f"版本过低（当前 {current_version}，需要 {min_version}+）"

    return True, current_version, None
