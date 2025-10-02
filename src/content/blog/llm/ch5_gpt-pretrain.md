---
title: 在无标记的数据集上进行预训练 | LLM
description: 从零构建大语言模型第5章:本章对上一章实现的GPT模块进行预训练,最后加载GPT-2的预训练权重
pubDate: 2025 09 25
categories:
  - tech
tags:
  - llm
---

本章的核心是实现训练函数对LLM进行预训练

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter5/figure5.1.png)

## 文本损失值的计算

从输入文本到 LLM 生成文本的整体流程，该流程通过五个步骤实现。

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter5/figure5.4.png)

在上一章中我们可以看到,模型生成的文本与目标文本不同,因为它尚未训练.接下来,通过"损失来数值化评估模型生成文本的质量.这不仅有助于衡量生成文本的质量，还为实现训练函数提供了基础，训练函数主要通过更新模型权重来改善生成文本的质量。

文本评估过程的一部分是衡量生成的 token 与正确预测目标之间的差距。本章后面实现的训练函数将利用这些信息来调整模型权重，使生成的文本更接近（或理想情况下完全匹配）目标文本。

也就是说要提高正确目标token ID所在位置的softmax概率.

> **反向传播**:如何最大化目标token的softmax值?整体思路是通过更新模型权重.权重更新通过一种称为反向传播的过程来实现，这是一种训练深度神经网络的标准技术.
> 反向传播需要一个损失函数，该函数用于计算模型预测输出与实际目标输出之间的差异（此处指与目标 token ID 对应的概率）。这个损失函数用于衡量模型预测与目标值的偏差程度。

交叉熵损失函数:

$$Loss=-\sum_{t=1}^{T}\ln P(y_{t}|x,\theta)$$
其中:
- $T$是序列长度
- $y_{t}$是在位置t上的目标token
- $P(y_{t}|x,\theta)$是模型在参数$\theta$下对目标token $y_{t}$的条件概率


使用对数可以避免**数值下溢**.概率值同时发生需要相乘,但是越乘越接近0.取对数就越来越大,符合损失越大的直观感受.

Pytorch内置`cross_entropy`函数.在使用它之前,需要先将张量展平:

```python
logits_flat = logits.flatten(0, 1)
targets_flat = targets.flatten()
print("Flattened logits:", logits_flat.shape)
print("Flattened targets:", targets_flat.shape)
```

得到的张量维度如下：

```python
Flattened logits: torch.Size([6, 50257])
Flattened targets: torch.Size([6])
```

最后计算交叉熵损失:

```python
loss = torch.nn.functional.cross_entropy(logits_flat, targets_flat)
print(loss)
```

## 计算训练集和验证集的损失

我们使用一个非常小的文本数据集，即伊迪丝·华顿的短篇小说《判决》.

将数据集分割为训练集(train loader)和验证集(validation loader).

制作Dataloader后,取出批次分别计算损失值,再计算所有批次的平均损失,得到训练集和验证集的损失值.

## 训练LLM

重点采用一种简单的训练循环方式来保证代码简洁易读

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter5/figure5.11.png)

## 通过解码策略控制生成结果的随机性

前一章中的 `generate_text_simple` 函数,选取词汇表中得分最高的token作为生成的token.接下来介绍两种控制生成文本随机性的和多样性的方法: `temperature scaling` 和 `top-k sampling`.

### Temperature scaling

在生成下一个词时加入概率选择.
之前的`torch.argmax`选择概率最高的token作为下一个词,这也叫贪心解码.为了生成更加多样化的文本,可以将 `argmax` 替换为一种从概率分布中进行采样的函数: `torch.multinomial`.

我们可以通过一种称为`temperature scaling`的方法进一步控制分布和选择过程，所谓`temperature scaling`，其实就是将 logits 除以一个大于 0 的数.

当 temperature 设置为小于1时，生成的分布会更加尖锐; 反之,生成的分布更接近均匀分布.这是因为指数函数的形状.放大后,大数较小数的差异更大,缩小后大数较小数的差异变小.

$$P(x_{i})=\frac{\exp\left( \frac{z_{i}}{T} \right)}{\sum \exp(\frac{z_{j}}{T})}$$

### Top-k采样

`temperature scaling`的概率采样方法有时会导致生成语法不正确或完全不合逻辑的内容.

我们引入了另一种称为`top-k 采样`的概念，当与概率采样和`temperature scaling`结合使用时，可以提升文本生成效果。

在 top-k 采样中，我们可以将采样限制在最有可能的前 k 个 token 内，并通过将其他 token 的概率设为零，将它们排除在选择之外.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter5/figure5.15.png)

实现top-k过程,首先选出最大的三个token:

```python
top_k = 3
top_logits, top_pos = torch.topk(next_token_logits, top_k)
print("Top logits:", top_logits)
print("Top positions:", top_pos)
```

我们应用Pytorch的 `torch.where` 函数,将非top-3的token的logit值设为-inf:

```python
new_logits = torch.where(
    condition=next_token_logits < top_logits[-1],   #A
    input=torch.tensor(float('-inf')),              #B
    other=next_token_logits                         #C
)
print(new_logits)

#A 识别出小于 top 3 最小值的 logits
#B 将这些较小的 logits 赋值为负无穷大
#C 保留所有其他 token 的原始 logits
```

我们现在可以应用`temperature scaling` 和`multinomial`函数来进行概率采样，从这 3 个非零概率得分中选择下一个 token。

### 对文本生成函数进行调整

整合以上方法,编写新的`generate`函数

## 在Pytorch中加载和保存模型权重

保存模型:

```python
torch.save(model.state_dict(), "model.pth")
```

加载模型权重:

```python
model = GPTModel(GPT_CONFIG_124M)
model.load_state_dict(torch.load("model.pth"))
model.eval()
```

在推理阶段，我们不希望随机丢弃网络中学到的任何信息。通过使用 `model.eval()`，模型会切换到推理阶段的评估模式，从而禁用 dropout 层。

如果计划继续训练模型,那么建议同时保存优化器状态

AdamW 等自适应优化器会为每个模型参数存储额外信息。AdamW 使用历史数据动态调整每个模型参数的学习率。没有这些信息时，优化器会重置，模型可能无法有效学习，甚至无法正确收敛，进而失去生成连贯文本的能力。可以使用 `torch.save` 保存模型和优化器的状态，方法如下：

```python
torch.save({
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    },
    "model_and_optimizer.pth"
)
```

接下来，我们可以按以下步骤恢复模型和优化器的状态：首先通过 `torch.load` 加载保存的数据，然后使用 `load_state_dict` 方法恢复状态：

```python
checkpoint = torch.load("model_and_optimizer.pth")
model = GPTModel(GPT_CONFIG_124M)
model.load_state_dict(checkpoint["model_state_dict"])
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4, weight_decay=0.1)
optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
model.train();
```

## 从OpenAI加载预训练权重

OpenAI 公开了 GPT-2 模型的权重，使我们不必投入数十万甚至数百万美元自行在大规模语料上重新训练模型。

OpenAI提供了多种规模的模型权重.包括124M,355M,744M和1558M.不同大小的GPT-2模型在总体架构上保持一致,但注意力头和Transformer模块等组件的重复次数以及嵌入维度大小有所不同.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter5/figure5.17.png)

OpenAI 在多头注意力模块的线性层中使用了偏置向量，以实现查询（query）、键（key）和值（value）矩阵的计算。偏置向量在现代 LLM 中已不再常用，因为它们对提升模型性能没有帮助，因而不再必要。然而，由于我们使用的是预训练权重，为了保持一致性，仍需启用这些偏置向量.

```python
torch.manual_seed(123)
token_ids = generate(
    model=gpt,
    idx=text_to_token_ids("Every effort moves you", tokenizer),
    max_new_tokens=25,
    context_size=NEW_CONFIG["context_length"],
    top_k=50,
    temperature=1.5
)
print("Output text:\n", token_ids_to_text(token_ids, tokenizer))
```

> 模型加载成功.通过设置不同的seed,temperature,top_k,可以输出不同的文本,temperature越大,文本变得莫名其妙.
