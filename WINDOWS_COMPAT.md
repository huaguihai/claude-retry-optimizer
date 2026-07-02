# Windows 平台兼容性说明

## 修复的问题

### 问题 1: `which` 命令不存在
- **之前**: 使用 `subprocess.run(["which", "claude"])`
- **问题**: Windows 上没有 `which` 命令
- **修复**: 使用 Python 的 `shutil.which()`（跨平台）

### 问题 2: npm.cmd 无法执行
- **之前**: `subprocess.run(["npm", "root", "-g"])`
- **问题**: Windows 上 npm 是 `.cmd` 文件，需要 shell
- **修复**: 添加 `shell=(platform.system() == "Windows")`

### 问题 3: 路径分隔符
- **之前**: 硬编码 Unix 风格路径 `@anthropic-ai/claude-code/bin/claude.exe`
- **问题**: Windows 和 Unix 路径分隔符不同
- **修复**: 使用 `os.path.join()` 构建跨平台路径

### 问题 4: Windows 特定路径
- **新增**: 检查 `%APPDATA%\npm\node_modules\...` 路径
- **原因**: Windows npm 全局包可能安装在 APPDATA 目录

## 测试结果

### Linux (当前环境)
```
平台: Linux x86_64
✓ 找到 Claude Code
✓ 文件存在，大小: 237.4 MB
```

### Windows (预期行为)
```
方法 1: shutil.which("claude") 
  → 找到: C:\Users\xxx\AppData\Roaming\npm\claude.cmd
  → 真实路径: C:\Users\xxx\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe

方法 2: npm root -g (with shell=True)
  → 找到: C:\Users\xxx\AppData\Roaming\npm\node_modules
  → 候选路径: ...\@anthropic-ai\claude-code\bin\claude.exe

方法 3: APPDATA 环境变量
  → 找到: %APPDATA%\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe
```

## 跨平台特性

| 功能 | Linux | macOS | Windows |
|------|-------|-------|---------|
| shutil.which() | ✅ | ✅ | ✅ |
| npm root -g | ✅ | ✅ | ✅ (shell=True) |
| 路径构建 | ✅ | ✅ | ✅ (os.path.join) |
| 平台特定路径 | ✅ | ✅ | ✅ (APPDATA) |

## 后续验证

在 Windows 上验证：
```powershell
# 1. 安装工具
pip install git+https://github.com/huaguihai/claude-retry-optimizer.git

# 2. 运行测试
python -m claude_retry_optimizer

# 预期结果：能正确找到 Claude Code 路径
```

## 代码改动摘要

- 添加 `platform` 模块检测操作系统
- `shutil.which()` 替代 `which` 命令
- `npm` 调用在 Windows 上使用 `shell=True`
- 根据平台选择不同的候选路径
- 新增 Windows APPDATA 路径检测
