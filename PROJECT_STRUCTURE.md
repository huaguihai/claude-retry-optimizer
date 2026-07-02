# Claude Retry Optimizer - 项目结构

## 目录结构

```
claude-retry-optimizer/
├── claude_retry_optimizer/       # 主包
│   ├── __init__.py
│   ├── __main__.py              # 入口：python -m claude_retry_optimizer
│   ├── menu.py                  # 菜单系统（主菜单 + 配置子菜单）
│   ├── binary.py                # 二进制文件操作（查找、备份、恢复）
│   ├── patcher.py               # Patch 逻辑（动态模式发现 + 字节替换）
│   ├── config.py                # 配置管理（保存/读取/预设方案）
│   └── env.py                   # 环境变量管理（写入 shell 配置）
├── tests/                       # 测试
│   ├── __init__.py
│   ├── test_binary.py
│   ├── test_patcher.py
│   ├── test_config.py
│   └── test_env.py
├── setup.py                     # 安装脚本
├── requirements.txt             # 依赖
├── README.md                    # 文档
└── LICENSE                      # MIT 许可证
```

## 模块职责

### menu.py
- 主菜单（6个选项）
- 配置子菜单（快捷/自定义）
- 状态显示
- 用户交互

### binary.py
- `find_binary()` - 查找 Claude Code 二进制
- `backup_binary()` - 创建备份
- `restore_binary()` - 恢复原版
- `get_binary_info()` - 获取版本和路径

### patcher.py
- `discover_patterns()` - 动态发现变量名
- `apply_patches()` - 应用所有修改
- `validate_binary()` - 验证二进制完整性

### config.py
- `ConfigManager` - 配置管理类
- 预设方案：快捷模式（50次/1秒）
- 保存/读取配置到 `~/.claude-retry-optimizer.json`
- 状态跟踪（未配置/已配置/已失效）

### env.py
- `update_shell_config()` - 写入环境变量到 shell 配置
- `remove_shell_config()` - 清除环境变量
- 支持 bash/zsh/fish

## 依赖库

```
rich>=13.0.0         # 终端 UI（表格、进度条、彩色输出）
```

## 状态文件

- `~/.claude-retry-optimizer.json` - 用户配置
- `~/.claude-retry-optimizer.env` - 环境变量（被 shell 配置 source）
- `<binary_path>.orig` - 原版备份

## 配置示例

```json
{
  "version": "1.0.0",
  "status": "configured",
  "mode": "quick",
  "config": {
    "max_retries": 50,
    "retry_interval_ms": 1000,
    "rate_limit_max_delay_ms": 10000
  },
  "binary_path": "/usr/local/bin/claude",
  "last_modified": "2026-07-02T12:00:00Z"
}
```
