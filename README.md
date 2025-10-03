## 介绍

这是我的博客网站仓库, 基于 [Frosti](https://github.com/EveSunMaple/Frosti) 模板搭建, 并通过 GitHub Actions 自动推送到服务器上.

GitHub Actions 非常方便, 推荐大家使用.

[**❤️ My Blog**](https://www.tankimzeg.top)

## 更新脚本

原项目包含一个 `frosti.update.sh` 更新脚本, 但该脚本在 Windows 下无法使用. 为此我编写了一个 `frosti-update.py` 脚本, 该脚本可以在 Windows 和 Linux 下运行. 该脚本会自动拉取最新的 Frosti 模板, 并将更新的文件覆盖到当前仓库中, 忽略 `.updateignore` 文件中指定的文件和文件夹.
