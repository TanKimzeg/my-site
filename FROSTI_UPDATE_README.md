# Frosti 更新脚本使用说明

本项目现在同时提供了 Bash 和 PowerShell 两个版本的更新脚本：

## Bash 版本 (Linux/macOS/Windows WSL)

```bash
./frosti.update.sh [语言代码]
```

## PowerShell 版本 (Windows)

```powershell
.\frosti.update.ps1 [-Language 语言代码]
```

### 支持的语言

- `en` - English (英语)
- `zh` - 中文简体

### 使用示例

**PowerShell (推荐用于 Windows):**

```powershell
# 使用系统默认语言
.\frosti.update.ps1

# 指定英语
.\frosti.update.ps1 -Language en

# 指定中文
.\frosti.update.ps1 -Language zh
```

**Bash (用于 Linux/macOS/WSL):**

```bash
# 使用系统默认语言
./frosti.update.sh

# 指定英语
./frosti.update.sh en

# 指定中文
./frosti.update.sh zh
```

### 功能说明

两个脚本具有相同的功能：

1. 从官方仓库克隆最新代码
2. 安全地更新项目文件（根据 `.updateignore` 保护用户内容）
3. 删除已废弃的文件
4. 清理空目录
5. 使用 pnpm 安装/更新依赖

### 注意事项

- 运行前请确保所有修改都已提交到 Git
- 脚本会自动保护 `.updateignore` 文件中列出的内容
- Windows 用户建议使用 PowerShell 版本以获得更好的兼容性
