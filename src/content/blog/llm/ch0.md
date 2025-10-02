---
title: 学习资料与环境配置 | LLM
description: 开了新坑:从零构建大语言模型(LLMs From Scratch)
pubDate: 2025 09 20
categories:
  - tech
tags:
  - llm
---

```shell
git clone --depth=1 https://github.com/rasbt/LLMs-from-scratch.git
cd LLMs-from-scratch
uv sync
```

出现了
```
Using CPython 3.13.0
Creating virtual environment at: .venv
Resolved 191 packages in 24m 23s
error: Distribution `tensorflow==2.18.1 @ registry+https://pypi.mirrors.ustc.edu.cn/simple/` can't be installed because it doesn't have a source distribution or wheel for the current platform

hint: You're using CPython 3.13 (`cp313`), but `tensorflow` (v2.18.1) only has wheels with the following Python ABI tags: `cp310`, `cp311`, `cp312`
```

这时候需要在`pyprojext.toml`中把

```toml
requires-python = ">=3.10,<=3.13"
```

改成

```toml
requires-python = ">=3.10,<=3.12"
```

再次执行即可


[LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch)

[从零构建大语言模型(中文版)](https://skindhu.github.io/Build-A-Large-Language-Model-CN)

本想着装一台新电脑,有独立显卡再来学这些深度学习,最近先学C++和数据库系统.但C++丑陋的语法让我难以接受,入门失败.数据库系统也比我想象中的要复杂得多,离开CMU15-445的bustub从零开始用Rust写DBMS可是一项浩瀚的工程.无奈只好暂时搁置(课程视频我还是在看的,在实习单位用空闲时间看,写的是纸质版的笔记).

我想起了前段时间发现的这个入门大语言模型的教程(上次入门还是在大一,那些自傲的家伙把我抛弃了,真是给他们闹麻了.如果他们知道我现在的水平会不会后悔少了一个打工的牛马呢?)

我对这群趋之若鹜的人十分鄙夷,代码都不会写几行,整天嘴上说自己研究什么"越狱","微调"装B,说着说着自己都信了.自知自己数学垃圾甚至不敢选机器学习的课,纯纯笑料.人与人之间,性格差异怎么会这么大,怎么能无耻到这个地步.靠着这一嘴到处混人际关系,得到了不少帮助.

这玩意火了这么多年,不知道水了多少虚假论文,成就了多少人的功名,救了多少混圈子的人.可是真正有贡献的成果才几个呢?除此之外的垃圾"成果"有什么实际意义呢?

从上世纪发明的传统机器学习算法,到Hinton的手写体识别网络,再到Transformer架构,近年火出圈的GPT,靠的还不是全网海量的数据砸钱训练出来的.一上大学就开始搞这个,属实是本末倒置.基础不牢,是走不远的.大一的时候,我就看了*Attention is All You Need*原文,自己思考了几天,我就基本上知道是怎么回事了.加上高中的时候,我已经学过微积分和线性代数,可以说有着得天独厚的条件,但我洞察到水平还差得远,于是从编程基础开始学习.越是别人趋之若鹜的事物,越要冷静观察.他们不过是几个赚足了信息差的本科生,装得牛逼轰轰,带我不过是想让我给他们当牛马,每天高强度看文献给他们汇报想法.虽然当时我还不知道我想要干什么,但我知道这肯定不是我想要的.

> 弃我去者,昨日之日不可留.当我重新看到这些东西的时候,我已经不是当年的我了
