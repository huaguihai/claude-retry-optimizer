#!/usr/bin/env python3
"""
Claude Retry Optimizer - 主入口
"""

import sys
from .menu import main
from .updater import run_update_command

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        run_update_command()
    else:
        main()
