# Claude Retry Optimizer

优化 Claude Code 重试行为的交互式工具。

## 🎯 功能特性

- ✅ **交互式菜单** - 小白友好的图形化菜单界面
- ✅ **快捷配置** - 一键应用推荐配置（50次重试，1秒间隔）
- ✅ **自定义配置** - 手动调整重试参数
- ✅ **自动备份** - 安全修改，随时可恢复
- ✅ **环境变量管理** - 自动写入 shell 配置

## 📦 安装

### 方式 1：从源码安装（推荐）

```bash
git clone https://github.com/huaguihai/claude-retry-optimizer.git
cd claude-retry-optimizer
pip install -e .
```

### 方式 2：直接安装

```bash
pip install git+https://github.com/huaguihai/claude-retry-optimizer.git
```

## 🚀 使用方法

### 启动交互式菜单

```bash
claude-retry-optimizer
```

或者：

```bash
python -m claude_retry_optimizer
```

### 检查并更新到最新版本

```bash
claude-retry-optimizer update
```

### 查看帮助

```bash
claude-retry-optimizer --help
```

## 📋 菜单说明

### 主菜单

```
┌─────────────────────────────────────────────────┐
│  Claude Code 重试优化工具                       │
├─────────────────────────────────────────────────┤
│  当前状态：未配置（使用官方默认）               │
│  Claude 路径：/usr/local/bin/claude             │
│  备份状态：无备份                               │
├─────────────────────────────────────────────────┤
│  1. 安装与更新                                  │
│  2. 开始配置                                    │
│  3. 修改配置                                    │
│  4. 测试当前配置                                │
│  5. 卸载                                        │
│  6. 退出                                        │
└─────────────────────────────────────────────────┘
```

### 功能说明

#### 1. 安装与更新
- 自动检测 Claude Code 位置
- 创建二进制文件备份
- 为后续配置做准备

#### 2. 开始配置（首次配置）
- **快捷配置**：使用推荐参数（50次重试，1秒间隔）
- **自定义配置**：手动输入重试次数和间隔

#### 3. 修改配置
- 查看当前配置
- 切换快捷/自定义模式
- 调整参数

#### 4. 测试当前配置
- 模拟重试流程
- 验证配置是否生效

#### 5. 卸载
- 恢复原版 Claude Code
- 清理环境变量和配置文件
- 删除备份

## 🔧 配置方案

### 快捷配置（推荐）
```
最大重试次数：50
重试间隔：1 秒
Rate-limit 处理：10 秒
```

### 自定义配置
- 重试次数：15-99 次
- 重试间隔：1-5 秒

## 📝 工作原理

该工具通过修改 Claude Code 二进制文件，优化以下行为：

1. **移除 15 次重试上限** - 提升到 50-99 次
2. **固定重试间隔** - 从指数退避改为固定间隔（默认 1 秒）
3. **优化 Rate-limit 处理** - 降低等待时间（从 30 分钟降到 10 秒）

修改过程：
- ✅ 自动备份原版二进制
- ✅ 动态发现变量名（版本无关）
- ✅ 字节级精确替换
- ✅ 原子写入（避免文件损坏）

## ⚠️ 注意事项

1. **需要 sudo 权限** - 修改系统级二进制文件
2. **更新后需重新配置** - `npm update @anthropic-ai/claude-code` 后需重新运行
3. **重启终端生效** - 配置后需重新打开终端或执行 `source ~/.bashrc`

## 🔄 更新 Claude Code 后

当你更新 Claude Code 时，优化会失效。重新运行工具即可：

```bash
# 更新 Claude Code
npm update -g @anthropic-ai/claude-code

# 重新应用优化
claude-retry-optimizer
# 选择 1. 安装与更新
# 选择 2. 开始配置
```

## 🗂️ 文件位置

- 配置文件：`~/.claude-retry-optimizer.json`
- 环境变量：`~/.claude-retry-optimizer.env`
- 备份文件：`<claude_binary_path>.orig`

## 🔍 故障排查

### 问题：找不到 Claude Code

```bash
# 检查是否安装
which claude

# 如果未安装
npm install -g @anthropic-ai/claude-code
```

### 问题：权限错误

```bash
# 使用 sudo 运行
sudo claude-retry-optimizer
```

### 问题：配置未生效

```bash
# 重新加载 shell 配置
source ~/.bashrc  # 或 ~/.zshrc
```

### 问题：想恢复原版

在菜单中选择 `5. 卸载` 即可恢复。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🔗 相关链接

- [Claude Code 官方文档](https://code.claude.com/)
- [Claude Code 重试机制说明](https://code.claude.com/docs/en/errors#automatic-retries)

## 📧 联系方式

- GitHub: [@huaguihai](https://github.com/huaguihai)

---

**免责声明**：此工具通过修改二进制文件来优化重试行为。使用前请确保你了解其工作原理。建议先在测试环境使用。
