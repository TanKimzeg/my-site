---
title: EndeavourOS体验 | Arch
description: "EndeavourOS是Arch Linux的衍生版，主打轻量简洁，但又解决了Arch安装复杂的问题。用户选择它通常是因为想要Arch的滚动更新和软件库，又不想折腾安装过程。"
pubDate: 2025 07 25 
image: /image/EndeavourOS.png
categories: 
  - tech
tags:
  - Linux
---

厌倦了臃肿的系统，又对 Arch Linux 的安装门槛望而却步？那么，**EndeavourOS** 可能就是你的理想选择！

它并非又一个“简单版 Arch”，而是秉承 Arch 哲学精髓的优雅继承者：**轻量、滚动更新、软件包丰富（得益于 AUR）**。EndeavourOS 的核心目标非常明确：**为你提供一个近乎纯净的 Arch Linux 基础，同时通过一个极其友好的图形安装程序（Calamares），彻底扫除安装 Arch 的最大障碍。**

安装后，你将获得一个**清爽、快速、高度可定制**的桌面环境（默认是精心调校过的 KDE，但也提供多种流行桌面选项）。没有预装大量你可能不需要的软件，系统将掌控权完全交还给你。你可以通过便捷的包管理工具 `pacman` 和 `yay` ，轻松访问 Arch 庞大的软件仓库和用户仓库（AUR），构建属于你自己的专属系统。

## 安装
在[官网](https://endeavouros.com/)中找到自己所在区域下载ISO，然后，就可以像Ubuntu/Kali等发行版那样进入图形化安装界面，顺便配置好镜像源，非常简单省事！离线默认安装KDE桌面，而且自带水星太空主题，很美观嘛：

![login-plasma](attachments/EndeavourOS-login-plasma.png)

每次开机后，自动会出现一个Welcome向导，充满新手关怀：

![welcome](attachments/EndeavourOS-welcome.png)

## 丰富的软件生态
与majargo有自己的软件仓库不同，Endeavouros完全就是用Arch的软件仓库。`yay`则能从AUR装软件包。

Arch的软件生态真是独一档。`pacman` 包管理器从[官方的软件仓库](https://archlinux.org/packages/)搜索软件包。这里的软件包开源可靠稳定的。

我一开始在这边安装了vscode，结果发现是那个开源版的vscode。而平时用到vscode与此不同，随后我发现它在[AUR](https://aur.archlinux.org/)里面。

为了便捷安装AUR的软件包，我发现了一个类似于 `pacman` 的包管理器 `yay`。作为补充，它能自动安装AUR的软件包。用法也与 `pacman`相同。

我们可以先搜索一下软件包的名字：

![packages](attachments/EndeavourOS-packages.png)

找到真正想要的那一个
![AUR](attachments/EndeavourOS-AUR.png)
在网页里面看更方便准确。

之前在NixOS里面想用V2rayN，结果发现无法自动配置系统代理。搞了很久才明白是不支持Xfce桌面的系统代理。而且连浏览器里面不能设置浏览器的代理，真是一个致命缺陷！相比之下，虽然Gnome和KDE资源占用较多，但还是受主流支持。

这次，在AUR里面找到V2rayN并安装，非常顺利就设置好了代理。

`pacman`还是很好用的，常用的命令就那几个。我这边一个月没滚动更新了，运行一下`sudo pacman -Syu`也没有挂。所以我觉得只要不去折腾太多的不稳定的插件和软件包，也没有那么容易滚挂吧...

![EndeavourOS-pacman-Syu](attachments/EndeavourOS-pacman-Syu.png)

## 详细的文档
[Arch Wiki](https://wiki.archlinuxcn.org/wiki/%E9%A6%96%E9%A1%B5)的文档真是非常详实。

比如我现在想把bash换成zsh，直接在Arch Wiki里面搜索[zsh](https://wiki.archlinuxcn.org/wiki/Zsh)，就教你怎么换默认shell，甚至zsh的第三方拓展也给你指明了它们的项目地址，配置起来还是非常高效的。

## Zsh的配置
Zsh支持Vim motion！那么我们初始化zsh之后，就去Github上的oh-my-zsh项目，按照README的指示下载并激活了oh-my-zsh。在~/.zshrc里面，我先置 `ZSH_THEME="random"`，出来`source ~/.zshrc`一下，给我加载了一个叫做lukerandall的主题，看起来挺美观的，就它了：

![EndeavourOS-lukerandall-theme](attachments/EndeavourOS-lukerandall-theme.png)

还能显示进程异常返回码，比显示时间有用😆

我安装的其他插件，都用oh-my-zsh管理：

- [zsh autosuggestions](https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md)
- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting/blob/master/INSTALL.md)

