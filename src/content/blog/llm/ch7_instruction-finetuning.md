---
title: "指令遵循微调 | LLM"
description: 从零构建大语言模型第7章:本章研究对预训练的LLM进行指令微调
pubDate: 2025 09 28 
categories: 
  - tech
tags:
  - llm
---

## 指令遵循微调简介

预训练的LLM在处理特定指令时往往表现不佳:

```
Output text:
 Convert 45 kilometers to meters: Convert 60 kilometers to meters to meters from 12.22 degrees to 12.29 degrees.

You can find the exact
```

## 为监督指令微调准备数据集

下载并格式化指令数据集,以便对预训练的LLM进项指令微调.改数据集包含1100组指令-响应对.

包含了'instruction', 'input', 'output'键值的字典.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter7/figure7.4.png)

将数据列表中的条目转换为Alpaca提示风格的输入格式

将数据集划分为训练集(85%), 验证集(5%)和测试集(10%).

## 将数据组织成训练批次

我们的Dataset需要对数据进行格式化.为此,自定义一个 `InstructionDataset`类, 继承了 `Dataset`应用了 `format_input` 函数,并对所有输入进行了预分词,类似于上一章的 `SpamDataset`. 

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter7/figure7.7.png)

与上一章类似,我们将所有输入填充到相同的长度.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter7/figure7.12.png)

由于我们填充了很多 `<|endoftext|>` 但是只需要保留一个结束符 token ID.所以我们将其他填充符设置为-100.

在 PyTorch 中，cross_entropy 函数的默认设置是 `cross_entropy(..., ignore_index=-100)`，这意味着它会忽略标签为 -100 的目标。对于这部分,就不计算损失了.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter7/figure7.13.png)

按理来说, `target_text` 中的指令部分对应的目标 token ID 也可以忽略,模型在训练时也会专注于生成准确的回答，而不是去记住指令内容，从而有助于减少过拟合。

目前，研究人员对于在指令微调过程中遮蔽指令是否具有普遍效果存在分歧。例如，最近有一篇题为《Instruction Tuning With Loss Over Instructions》的论文表明，不遮蔽指令有助于提升大语言模型的性能.

> 可以做个实验


## 为指令数据集创建Dataloader

将我们自定义的 `comstomized_collate_fn` 传入 `DataLoader` 的 `collate_fn` ,调用这个函数处理batch数据.

## 加载预训练的LLM

本节指定的GPT模型是355M,而不是124M.该模型的存储高达1.42GB!

选择更大模型的原因是 1.24 亿参数的小模型容量有限，难以通过指令微调获得令人满意的效果。

> 下载速度十分缓慢...


## 指令微调LLM

> 到这里,我的笔记本电脑已经无力承载训练负担了

> 在原始 Alpaca 数据集上进行微调

## 提取并保存响应

使用另一个LLM来评估微调模型的响应.

## 评估指令微调后的LLM

利用另一个更大的大语言模型对微调模型的响应进行自动化评估。

> 人才

这里使用了 Ollama运行 llama3模型,把我们训练的结果传递给它,让它打分.计算平均得分

## 结语

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter7/figure7.21.png)

### 接下来如何做

本书的Git仓库还有大量学习资料,我将继续探索.但是在我换新电脑之前,恐怕很难在本地开展实验了.

### 如何在快速变化的前言领域保持领先

当然是阅读最新论文了.
