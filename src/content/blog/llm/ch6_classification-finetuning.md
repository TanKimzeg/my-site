---
title: 用于分类任务的微调 | LLM
description: 从零构建大语言模型第6章:本章学习对预训练的LLM进行分类微调
pubDate: 2025 09 27
categories:
  - tech
tags:
  - llm
---
## 不同类型的微调

微调语言模型最常见的方法是指令微调和分类微调。指令微调通过在一组任务上使用特定指令训练模型，用以提升模型对自然语言提示中任务描述的理解和执行能力.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter6/figure6.2.png)

而本章的重点是分类微调.
在分类微调中,模型被训练用来识别特定的一组类别标签.分类微调模型可视为高度专业化的模型.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter6/figure6.3.png)

> 分类微调则适合需要将数据精确分类为预定义类别的任务，例如情感分析或垃圾短信检测。
> 
> 虽然指令微调用途更广泛，但需要更大的数据集和更多的计算资源，才能训练出能胜任多种任务的模型。相比之下，分类微调所需的数据和计算量更少，但用途局限于模型已训练的特定类别。

## 准备数据集

这里采用了一个包含是垃圾信息和非垃圾信息的文本信息数据集.

首先下载了tsv数据集.数据集的标签中'ham'正常短信比'spam'垃圾短信的出现频率更高.

为了处理不平衡数据集,统一采样为相同数量.(数据平衡处理)

接下来,将字符串类别标签'ham'和'spam'分别转换为整数标签0和1.

这个过程类似于将文本转换为token ID.只不过这了只有两个.

然后将数据集划分为三部分: 70%用于训练集, 10%用于验证集, 20% 用于测试集.


## 创建Dataloader

文本信息长度不一,需要进行填充处理.将所有消息填充到与数据集中最长消息相同的长度.为此,我们使用`<|endoftext|>`作为填充token.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter6/figure6.7.png)

## 使用预训练权重初始化模型

此时的模型还不具备遵循指令方面的能力.

## 添加分类头

为分类任务的微调做准备.为此,我们需要替换原始的输出层.
原输出层将隐藏层表示映射到50257个词汇的词汇表,这里我们用一个较小的输出层将其映射到两个类别: 0和1.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter6/figure6.9.png)

为了让模型准备好进行分类微调，我们首先通过将所有层设为不可训练来冻结模型：

```python
for param in model.parameters():
    param.requires_grad = False
```

接着，按照图 6.9 所示，我们替换掉输出层（model.out_head），该层原本将层输入映射到 50,257 维空间（即词汇表大小）：

```python
# Listing 6.7 Adding a classification layer
torch.manual_seed(123)
num_classes = 2
model.out_head = torch.nn.Linear(
    in_features=BASE_CONFIG["emb_dim"],
    out_features=num_classes
)
```

这个新的输出层 `model.out_head` 的 `requires_grad` 属性默认为 `True`，意味着它是模型训练过程中唯一会被更新的层。

**通过实验发现，微调更多层能够显著提升微调后模型的预测性能.** 所以,将最后一个Transformer模块以及连接该模块和输出层的LayerNorm模块也配置为可训练.我们将它们的
`requires_grad` 设置为 `True` :

```python
for param in model.trf_blocks[-1].parameters():
    param.requires_grad = True
for param in model.final_norm.parameters():
    param.requires_grad = True
```

跟预测输出一样,序列中的最后一个token整合了所有前面token的信息,我们只关注最后一个输出

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter6/figure6.11.png)

> 尝试微调第一个token,与最后一个token的微调对比.

## 计算分类损失和准确率

与50257个输出转换为概率分布,然后通过 `argmax` 函数返回概率最高的位置,从而得出LLM生成的下一个token ID一样.本章中,采用相同的方法来计算模型对于给定输入的预测结果.

```python
predicted_labels = torch.argmax(logits, dim=-1) 
num_examples += predicted_labels.shape[0] 
correct_predictions += (predicted_labels == target_batch).sum().item()
```

损失值的计算仍然采用交叉熵损失函数.唯一的调整是只优化最后一个tokener 不必计算整个序列中的所有token的损失.

## 使用监督数据对模型进行微调

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter6/figure6.15.png)

训练集和测试集准确率之间的轻微差异表明训练数据的过拟合程度较低。通常，验证集的准确率会略高于测试集的准确率，这是因为模型开发过程中通常会通过调整超参数来优化验证集上的表现，而这种优化未必能有效地泛化到测试集上。

## 将LLM用于垃圾短信分类

函数先将文本处理为 token ID，然后使用模型预测一个整数类别标签，并返回对应的类别名称.

## 本章摘要

- 微调 LLM 有不同的策略，包括分类微调（本章）和指令微调（下一章）。
- 分类微调是指将 LLM 的输出层替换为一个小型的分类层。
- 在将文本消息分类为‘垃圾短信’或‘非垃圾短信’的任务中，新的分类层只需要 2 个输出节点；而在之前的章节中，输出节点的数量等于词汇表中的唯一 token 数量，即 50,256。
- 分类微调任务不是像预训练那样预测下一个词，而是训练模型输出正确的类别标签，例如‘垃圾短信’或‘非垃圾短信’。
- 在微调阶段，模型的输入是转换为 token ID 的文本，这与预训练阶段类似。
- 在微调 LLM 之前，我们会加载预训练模型作为基础。
- 评估分类模型需要计算分类准确率，即正确预测的比例。
- 微调分类模型时使用的交叉熵损失函数与预训练 LLM 时相同。
