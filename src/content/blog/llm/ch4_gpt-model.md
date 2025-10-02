---
title: 从零开始实现一个用于文本生成的GPT模型 | LLM
description: 从零构建大语言模型第4章:本章实现了Transformer模块,进一步实现了GPT模型
pubDate: 2025 09 24
categories:
  - tech
tags:
  - llm
---

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter4/figure4.1.png)

## 实现LLM的架构
![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter4/figure4.2.png)

```python
torch.manual_seed(123)
model = DummyGPTModel(GPT_CONFIG_124M)
logits = model(batch)
print("Output shape:", logits.shape)
print(logits)
```

模型的输出通常被称为logits,它的形状是[batch,text_len,vocab_size].嵌入层的维度为 50,257，因为每个维度对应词汇表中的一个唯一 token。在之后的处理中，我们会将这些 50,257 维向量转换回 token ID，然后再解码成单词。

## 使用LayerNorm对激活值进行标准化
本节中，我们将实现层归一化，以提高神经网络训练的稳定性和效率。

### LayerNorm的工作原理
![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter4/figure4.5.png)

神经网络层包含一个线性层，后接一个非线性激活函数 ReLU，这是神经网络中的标准激活函数。
```python
torch.manual_seed(123)
batch_example = torch.randn(2, 5)          #A
layer = nn.Sequential(nn.Linear(5, 6), nn.ReLU())
out = layer(batch_example)
print(out)

#A 创建2个训练样本，每个样本有5个维度（特征）
```

实现层归一化，以提高神经网络训练的稳定性和效率。改操作包括减去均值,并除以标准差.

现在将这个过程封装到一个Pytorch模块中,以便后续使用:

```python
# Listing 4.2 A layer normalization class
class LayerNorm(nn.Module):
    def __init__(self, emb_dim):
        super().__init__()
        self.eps = 1e-5
        self.scale = nn.Parameter(torch.ones(emb_dim))
        self.shift = nn.Parameter(torch.zeros(emb_dim))

    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        norm_x = (x - mean) / torch.sqrt(var + self.eps)
        return self.scale * norm_x + self.shift
```

## 实现带有GELU激活函数的前馈神经网络
实现一个小型神经网络子模块

 `GELU(x) = x ⋅ Φ(x)`，其中 Φ(x) 是标准正态分布的原函数。计算开销更低的近似实现:

$$GELU(x)≈0.5⋅x⋅(1+tanh[(2/π)​⋅(x+0.044715⋅x3])$$

使用 GELU 激活函数实现一个小型的神经网络模块 FeedForward:

```python
# Listing 4.4 A feed forward neural network module
class FeedForward(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(cfg["emb_dim"], 4 * cfg["emb_dim"]),
            GELU(),
            nn.Linear(4 * cfg["emb_dim"], cfg["emb_dim"]),
        )

def forward(self, x):
    return self.layers(x)
```

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter4/figure4.9.png)

输出的张量形状与输入张量形状相同.

FeedForward模块对模型的泛化能力起到了关键作用.

> 尽管该模块的输入和输出维度相同，但在内部，它首先通过第一个线性层将嵌入维度扩展到一个更高维度的空间。之后再接入非线性 GELU 激活，最后再通过第二个线性层变换回原始维度。这样的设计能够探索更丰富的表示空间。扩展后的高维空间可以让模型“看到”输入数据中更多的隐藏特征，提取出更丰富的信息。然后在收缩回低维度时，这些丰富的特征被整合到了输入的原始维度表示中，使模型最终的输出包含更多的上下文和信息。

>[!note]
> 主观设计的产物.

## 添加残差连接
快捷连接最初是在计算机视觉中的深度网络（尤其是残差网络）提出的，用于缓解梯度消失问题。梯度消失是指在训练中指导权重更新的梯度在反向传播过程中逐渐减小，导致早期层（靠近输入端的网络层）难以有效训练

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter4/figure4.12.png)

>[!note]
>如何理解梯度消失现象?为什么有这种问题?

快捷连接可以通过将某一层的输出直接传递给更深层来跳过==**一个或多个**==层，有助于缓解深度神经网络训练中的梯度消失问题。

## 连接注意力层与线性层(Transformer模块)
![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter4/figure4.13.png)

Transformer 模块的输出维度与输入维度保持一致.

## 实现GPT模型
![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter4/figure4.15.png)

在参数量为 1.24 亿的 GPT-2 模型中，该模块重复了 12 次，这一数量通过 `GPT_CONFIG_124M` 配置字典中的`n_layers`参数指定。在 GPT-2 最大的 15.42 亿参数模型中，Transformer 模块重复了 36 次。

最后一个 Transformer 模块的输出会经过一个最终的LayerNorm步骤，然后进入线性输出层。该层将 Transformer 的输出映射到一个高维空间（在本例中为 50,257 维，对应于模型的词汇表大小），以预测序列中的下一个词。

### 分析模型规模
#### 参数数量
统计模型中参数张量的总参数量:

```python
total_params = sum(p.numel() for p in model.parameters())
print(f"Total number of parameters: {total_params:,}")
```

输出如下:

```
Total number of parameters: 163,009,536
```

GPT 模型的参数量为 1.24 亿，但代码输出的实际参数量却是 1.63 亿，这是为什么呢？

原因在于 GPT-2 架构中使用了一种称为‘权重共享’的概念，这意味着 GPT-2 架构将 token 嵌入层的权重复用于输出层。为了更好地理解这一点，我们可以来看一下在模型中初始化的 token 嵌入层和线性输出层的形状：

```
print("Token embedding layer shape:", model.tok_emb.weight.shape)
print("Output layer shape:", model.out_head.weight.shape)
```

从打印结果可以看到，这两层的权重形状相同：

```
Token embedding layer shape: torch.Size([50257, 768])
Output layer shape: torch.Size([50257, 768])
```

token 嵌入层和输出层的参数量很大，因为分词器词汇表中包含 50,257 个 token。这两层的作用都是在嵌入维度和词汇表大小之间映射.根据权重共享原则，我们可以从 GPT-2 模型的总参数量中去除输出层的参数量。

```python
total_params_gpt2 = total_params - sum(p.numel() for p in model.out_head.parameters())
print(f"Number of trainable parameters considering weight tying: {total_params_gpt2:,}")
```

输出如下：

```
Number of trainable parameters considering weight tying: 124,412,160
```

如我们所见，模型现在的参数量为 1.24 亿，与 GPT-2 原始模型的规模一致。

权重共享能够减少模型的整体内存占用和计算复杂度。然而，根据我的经验，==分别使用独立的 token 嵌入层和输出层会使训练效果和模型性能更佳，因此在我们的 GPT 模型实现中，我们使用了独立的嵌入层和输出层。==现代大语言模型也是如此。

#### 参数所需内存
假设每个参数为32位浮点数,占用4字节,我们得出模型总大小位621.83MB.

## 生成文本
![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter4/figure4.16.png)

给定输入上下文后,逐步生成文本.每次迭代中,输入上下文会不断拓展,是模型能够生成连贯且符合上下文的内容.

模型每一步输出与词汇表大小相同的张量[context_size, vocab_size],表示下一个潜在的token.取出最后一个(即预测,形状为[1,vocab_size]),通过`softmax`转换为概率分布.找到最高概率对应的索引,取得token ID.将token ID 解码回文本,从而得到下个token.这样就达到了目的.

在实践中,我们会多次迭代这一过程,直到生成的token数量达到要求.

`ch04/01_main-chapter-code/gpt.py`的`generate_text_simple`就是这一过程.

> 其实`softmax`函数和取最大值是重复的,因为`softmax`单调.

`model.eval()`方法会自动禁用训练时使用的随机组件`dropout()`.

目前的模型生成的是一些随机的内容,因为模型还没经过训
练,使用随机权重.
