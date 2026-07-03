#!/usr/bin/env python3
"""
debug_find_binary.py - 调试 find_binary() 在 Windows 上的行为
"""

import os
import platform
import subprocess


def debug_find_binary():
    """调试版本的 find_binary，输出所有尝试的路径"""
    print(f"\n=== 调试 find_binary() ===\n")
    print(f"平台: {platform.system()}")
    print(f"架构: {platform.machine()}\n")

    # 方法 1: shutil.which
    print("方法 1: shutil.which('claude')")
    import shutil
    claude_path = shutil.which("claude")
    if claude_path:
        print(f"  ✓ 找到: {claude_path}")
        real_path = os.path.realpath(claude_path)
        print(f"  真实路径: {real_path}")
        print(f"  文件存在: {os.path.isfile(real_path)}")
    else:
        print(f"  ✗ 未找到")
    print()

    # 方法 2: npm root -g
    print("方法 2: npm root -g")
    try:
        result = subprocess.run(
            ["npm", "root", "-g"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=(platform.system() == "Windows")
        )
        if result.returncode == 0:
            npm_root = result.stdout.strip()
            print(f"  npm_root: {npm_root}")

            npm_bin = os.path.dirname(npm_root)
            print(f"  npm_bin: {npm_bin}")

            if platform.system() == "Windows":
                candidates = [
                    os.path.join(npm_root, "@anthropic-ai", "claude-code", "bin", "claude.exe"),
                    os.path.join(npm_root, "@anthropic-ai", "claude-code", "claude.exe"),
                    os.path.join(npm_root, ".bin", "claude.exe"),
                    os.path.join(npm_root, "@anthropic-ai", "claude-code-win32-x64", "claude.exe"),
                    os.path.join(npm_bin, "node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe"),
                ]

                print(f"\n  尝试 {len(candidates)} 个候选路径:")
                for i, c in enumerate(candidates, 1):
                    exists = os.path.isfile(c)
                    status = "✓ 存在" if exists else "✗ 不存在"
                    print(f"    {i}. {status}")
                    print(f"       {c}")
                    if exists:
                        print(f"       [找到！]")
                        break
        else:
            print(f"  ✗ npm root -g 失败: {result.stderr}")
    except Exception as e:
        print(f"  ✗ 异常: {e}")
    print()

    # 方法 3: APPDATA
    if platform.system() == "Windows":
        print("方法 3: APPDATA 路径")
        appdata = os.environ.get("APPDATA")
        if appdata:
            print(f"  APPDATA: {appdata}")
            candidates = [
                os.path.join(appdata, "npm", "node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe"),
                os.path.join(appdata, "npm", "node_modules", "@anthropic-ai", "claude-code", "claude.exe"),
            ]
            print(f"\n  尝试 {len(candidates)} 个候选路径:")
            for i, c in enumerate(candidates, 1):
                exists = os.path.isfile(c)
                status = "✓ 存在" if exists else "✗ 不存在"
                print(f"    {i}. {status}")
                print(f"       {c}")
                if exists:
                    print(f"       [找到！]")
                    break
        else:
            print(f"  ✗ APPDATA 环境变量不存在")
        print()

    # 方法 4: npm bin -g + claude.cmd
    if platform.system() == "Windows":
        print("方法 4: npm bin -g + claude.cmd")
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
                print(f"  npm_bin: {npm_bin}")

                claude_cmd = os.path.join(npm_bin, "claude.cmd")
                print(f"  claude.cmd: {claude_cmd}")
                print(f"  存在: {os.path.isfile(claude_cmd)}")

                if os.path.isfile(claude_cmd):
                    with open(claude_cmd, "r", encoding="utf-8") as f:
                        content = f.read()
                        print(f"\n  claude.cmd 内容:")
                        print("  " + "─" * 60)
                        for line in content.splitlines()[:10]:  # 只显示前10行
                            print(f"  {line}")
                        print("  " + "─" * 60)
            else:
                print(f"  ✗ npm bin -g 失败: {result.stderr}")
        except Exception as e:
            print(f"  ✗ 异常: {e}")
        print()

    print("=== 调试结束 ===\n")


if __name__ == "__main__":
    debug_find_binary()
