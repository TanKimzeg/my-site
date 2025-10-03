---
title: "使用Github Actions自动部署静态网站"
description: "Github Actions入门"
pubDate: 2025 10 03 
categories: 
  - tech
tags:
  - network
  - Linux
---

由于服务器的性能不好,之间在上面运行构建会卡死.所以,以前我都是在本地构建产物,将产物push到Github,再从服务器上下载`dist/`.

这当然不是最佳实践.最近我了解到Github Actions,完美地解决了这个问题!

## 回顾部署流程

我的静态博客基于 `Astro`. 跟`Hexo`, `Hugo`这类一样,都是将我所写的md文件编译成最终的 html,css,js等静态资源.通过Nginx导向dist/目录即可将网站搭建起来.

现在使用了Github Actions之后,这些部署任务就自动交给它做了:

1. 拉取网站源码
2. 运行 `npm run build`
3. 将产物(`dist/`)复制到服务器Nginx指向的目录
4. 服务器重启Ningx: `sudo nginx -s reload`

## 实现

在 `.github/workflows/` 下新建一个 `main.yaml` 文件.按照文档和GPT-5的指引,生成了[这些内容](https://github.com/TanKimzeg/my-site/blob/main/.github/workflows/main.yaml).

这里我做一个大致的说明：

- on 表示触发条件
- jobs 表示要做的工作
- jobs 下的 step 表示要做的步骤，前一步失败，后面不会继续执行。
- jobs 下的 step 下有 name、uses、with 等，表示一个 action。
- name 表示 action 的名称，uses 表示使用哪个插件，with 表示传给插件的参数。
- use 是插件
- `secrets.XXX` 这个 XXX 表示本仓库的环境变量.秘密信息不能硬编码在源码里,而是通过 `secret.XXX` 的形式定义. 

随后,我们去仓库的 setting 页面,找到 "Secrets and variables"下的Actions, 新建 Repository secrets配置这些秘密变量.

在这个项目,我们需要服务器的IP地址,端口,登录用户,私钥等.可以用自己平时的登录用户,为了安全起见,也可以新增一个用户,这个用户只拥有网站目录的写权限.

配置完后,每次向远程仓库push,自动触发Github Actions.可以看到每一步的运行情况.

本以为这么好用的功能有诸多限制,不能经常使用.没想到限制非常宽松,主要如下:

1. 执行时间限制

	**每月运行时间**：免费用户每月有 **2000 分钟** 的免费运行时间。
	
	**单次工作流程运行时间**：每个工作流程最长运行 **6 小时**。
2. 并发执行限制

	**并发工作流程**：最多同时运行 **20 个工作流程**。
	
	**并发作业**：每个工作流程中最多同时运行 **20 个作业**。

3. 存储空间限制
每个仓库的构建产物存储空间上限为 **500 MB**。

我的网站构建用了不到5分钟,远远达不到限制!

## REFERRENCE

[Github Actions 文档](https://docs.github.com/zh/actions)

[GitHub Actions入门教程-自动部署静态博客](https://zhuanlan.zhihu.com/p/364366127)
