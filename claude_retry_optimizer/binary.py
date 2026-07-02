#!/usr/bin/env python3
"""
binary.py - Claude Code 二进制文件操作模块
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_binary() -> Optional[str]:
    """查找 Claude Code 二进制文件路径"""
    # 尝试 which claude
    try:
        result = subprocess.run(
            ["which", "claude"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            path = os.path.realpath(result.stdout.strip())
            if os.path.isfile(path):
                return path
    except Exception:
        pass

    # 备用：查找 npm 全局安装目录
    try:
        result = subprocess.run(
            ["npm", "root", "-g"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            npm_root = result.stdout.strip()
            candidates = [
                os.path.join(npm_root, "@anthropic-ai/claude-code/bin/claude.exe"),
                os.path.join(npm_root, "@anthropic-ai/claude-code-linux-x64/claude"),
                os.path.join(npm_root, "@anthropic-ai/claude-code-linux-arm64/claude"),
                os.path.join(npm_root, "@anthropic-ai/claude-code-darwin-arm64/claude"),
                os.path.join(npm_root, "@anthropic-ai/claude-code-darwin-x64/claude"),
            ]
            for c in candidates:
                if os.path.isfile(c):
                    return os.path.realpath(c)
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
