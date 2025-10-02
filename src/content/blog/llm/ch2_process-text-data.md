---
title: 处理文本数据 | LLM
description: 从零构建大语言模型第2章:本章讲解如何将文本数据转换为词嵌入
pubDate: 2025 09 21
categories:
  - tech
tags:
  - llm
---

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter2/figure2.1.png)

## 理解词嵌入
深度神经网络模型，包括 LLM，往往无法直接处理原始文本。这是因为文本是离散的分类数据，它与实现和训练神经网络所需的数学运算不兼容。因此，我们需要一种方法将单词表示为连续值向量。

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter2/figure2.2.png)

不同的数据源在转换成嵌入时需要用到不同的技术.这些张量就存储了数据的信息.

> mark一下检索增强技术([RAG](https://waytoagi.feishu.cn/wiki/PUUfwNkwqielBOkbO5RcjnTQnUd)),与向量数据库有关联!当用户提交一个查询时，首先将这个查询也编码成一个向量，然后去承载外部知识库的向量数据库中检索（检索技术有很多种）与问题相关的信息。检索到的信息被作为额外的上下文信息输入到LLM中，LLM会将这些外部信息与原始输入结合起来，以更准确和丰富的内容生成回答。

> 尽管GPT在文本生成任务中表现强大，但它们依赖的是预训练的知识，这意味着它们的回答依赖于模型在预训练阶段学习到的信息。这种方式导致了几个问题：
> - **知识的时效性：** 模型的知识基于它的预训练数据，因此无法获取最新的信息。比如，GPT-3 的知识截止到 2021 年，无法回答最新的事件或发展。
> - **模型大小的限制：** 即使是大型模型，所能存储和运用的知识也是有限的。如果任务涉及特定领域（如医学、法律、科学研究），模型在预训练阶段可能没有涵盖足够的信息。
> - **生成的准确性：** 生成模型可能会凭空编造信息（即“幻觉现象”），导致生成内容不准确或虚假。


Word2Vec的核心思想是，出现在相似上下文中的词通常具有相似的含义。因此可以聚类:

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter2/figure2.3.png)

我们的向量数据库也是这样聚类索引的.

## 文本分词
将输入文本拆分为单个token，这是创建 LLM 嵌入所需的预处理步骤。这些token可以是单个单词或特殊字符，包括标点符号

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter2/figure2.4.png)

将英文文本分词,忽略空格(对于空格敏感的Python代码就不能忽略).这里使用了一个简单的正则表达式来分割文本:

```python
preprocessed = re.split(r'([,.:;?_!"()\']|--|\s)', raw_text)
preprocessed = [item.strip() for item in preprocessed if item.strip()]
print(len(preprocessed))
```

## 将token转换为token IDs
我以前其实已经见过类似的处理[^1],只是没有意识到这是转换为嵌入向量的中间步骤.

我们需要构建一个词汇表.这个词汇表定义了每个独特单词和特殊字符与唯一整数的映射.

为`SimpleTokenizerV1`类实现`encode`和`decode`方法.

`encode`将token转换为id,`decode`将id转换为token.

目前,如果遇到不再词汇表里的单词会转换失败.

## 添加特殊上下文token
为了处理一些特殊文本,需要引入特殊token:
- [BOS]（序列开始）：这个token表示文本的起始位置，指示 LLM 内容的开始。
- [EOS]（序列结束）：这个token位于文本的末尾，在连接多个无关文本时特别有用，类似于 <|endoftext|>。例如，在合并两个不同的维基百科文章或书籍时， [EOS] token指示一篇文章结束和下一篇文章开始。
- [PAD]（填充）：在使用大于 1 的批量大小数据集训练 LLM 时，批量可能包含不同长度的文本。为了确保所有文本长度一致，较短的文本会用 [PAD] token进行扩展或填充，直到达到批量中最长文本的长度。

对于我们的简单LLM来说,引入两种特殊token就够了:
`<|endoftext|>`和`<|unk|>`

在遇到不在词汇表中的单词时使用一个<|unk|> token。此外，我们还会在不相关的文本之间添加一个特殊的`<|endoftext|>` token。例如，在对多个独立文档或书籍进行GPT类大语言模型的训练时，通常会在每个文档或书籍之前插入一个token，以连接前一个文本源，如图2.10所示。这有助于大语言模型理解，尽管这些文本源在训练中是连接在一起的，但它们实际上是无关的。

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter2/figure2.10.png)

修改`SimpleTokenizerV2`类以支持特殊token.

填充(PAD)token的目的是对齐batch以便并行训练,告知模型忽略即可.

此外，用于 GPT 模型的分词器也不使用 <|unk|> 标记来表示词汇表之外的词。相反，GPT 模型采用字节对编码分词器，它将单词分解为子词单元.

## 字节对编码(Byte pair encoding)
字节对编码(BPE)是一种更复杂的分词方案.

现成的一个名为`tiktoken`的Python库使用Rust非常高效地实现了BPE算法!

BPE不需要`<|unk|>`也能正确编码和解码未知词汇的原因:
将不在其预定义词汇表中的单词分解为更小的子词单元甚至单个字符，使其能够处理超出词汇表的单词。因此，得益于BPE算法，如果分词器在分词过程中遇到一个不熟悉的单词，它可以将其表示为一系列子词token或字符.

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter2/figure2.11.png)

> 字节对编码是一种基于统计的方法，它会先从整个语料库中找出最常见的字节对（byte pair），然后把这些字节对合并成一个新的单元。


## 使用滑动窗口进行数据采样
LLM通过预测文本中的下一个单词进行预训练.通过滑动窗口方法从训练数据集中提取输入-目标对.

其实,这个采样策略我也在同一个地方见到[^1].

采样过程中有几个参数: `batch_size`, `max_length`, `stride`,即批次大小/上下文大小和步幅

适当地调整步幅,这是为了全面利用数据集（我们不跳过任何单词），同时避免批次之间的重叠，因为更多的重叠可能会导致过拟合.

```
Inputs: 
	tensor([[ 40, 367, 2885, 1464], 
			[ 1807, 3619, 402, 271], 
			[10899, 2138, 257,7026], 
			[15632, 438, 2016, 257], 
			[ 922, 5891, 1576, 438], 
			[ 568, 340, 373, 645], 
			[ 1049, 5975, 284, 502], 
			[ 284, 3285, 326, 11]]) 

Targets: 
	tensor([[ 367, 2885, 1464, 1807], 
			[ 3619, 402, 271, 10899], 
			[ 2138, 257, 7026, 15632], 
			[ 438, 2016, 257, 922], 
			[ 5891, 1576, 438, 568], 
			[ 340, 373, 645, 1049], 
			[ 5975, 284, 502, 284], 
			[ 3285, 326, 11, 287]])
```

## 构建词嵌入层
对于GPT类大语言模型（LLM）来说，连续向量表示（Embedding）非常重要，原因在于这些模型使用深度神经网络结构，并通过反向传播算法（backpropagation）进行训练。

> 1. **向量嵌入的作用**
> 连续向量表示不仅让文本数据可以进入神经网络，还帮助模型捕捉和表示文本之间的语义关系。例如：
> - **同义词或相似词**：在向量空间中，相似的单词可以有接近的向量表示。这种语义相似性帮助模型理解上下文，并在生成文本时提供参考。
> - **上下文关系**：GPT 等 LLM 模型不仅依赖单词级别的向量表示，还会考虑句子或段落上下文，形成动态嵌入，从而生成更具连贯性的文本。
> 2. **反向传播算法的要求**
 > 深度神经网络通过**反向传播算法**进行训练，反向传播的本质是利用梯度下降法来更新网络的权重，以最小化损失函数（loss function）。反向传播要求每一层的输入、输出和权重都能够参与梯度计算，而梯度计算只能应用于数值数据。
> - **自动微分与梯度计算**：在反向传播中，神经网络会根据损失函数的导数来计算梯度，这个过程依赖于自动微分（automatic differentiation）。为了计算每层的梯度，输入的数据必须是数值形式（即向量），否则无法对离散的文本数据求导。
> - **梯度更新权重**：每次更新网络权重时，神经网络会根据每一层的输入和输出来调整权重，以更好地学习数据的模式。如果输入不是数值形式，就无法实现梯度更新，从而无法通过反向传播训练网络。

`torch`中有一个`nn.Embedding`提供嵌入操作:

```python
import torch
embedding_layer = torch.nn.Embedding(num_emb, output_dim)
print(embedding_layer.weight)
```

就能看到一个形状为[num_emb, output_dim]的初始权重矩阵.可以看到，嵌入层的权重矩阵由比较小的随机值组成。这些值将在LLM训练过程中作为LLM优化的一部分被优化.每一行代表词汇表中一个token的权重.

这样,我们就可以对输入转化为嵌入了:
![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter2/figure2.16.png)

## 位置编码
因为只要是相同的词,就映射为同一个embedding,所以它对token的位置或顺序没有概念.因此向LLM注入额外的位置信息是有帮助的。

解决的办法就是添加绝对位置嵌入和相对位置嵌入.

1. 绝对位置嵌入

对于输入序列中的每个位置，都会将一个唯一的绝对位置嵌入向量添加到token的嵌入向量中，以传达其确切位置。

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter2/figure2.18.png)

2. 相对位置嵌入
相对位置嵌入强调的是token之间的相对位置或距离。这意味着模型学习的是“相隔多远”的关系，而不是“在什么确切位置”。这样的优势在于，即使模型在训练时没有接触过不同的长度，它也可以更好地适应各种长度的序列。

选择哪种类型的位置嵌入通常取决于特定的应用和所处理数据的性质。

```python
context_length = max_length
pos_embedding_layer = torch.nn.Embedding(context_length, output_dim)
pos_embeddings = pos_embedding_layer(torch.arange(context_length))
print(pos_embeddings.shape)
```
`torch.arange(context_length)`包含一个从0到最大输入长度-1的整数序列.
在实际中,如果输入文本长度超出所支持的上下文长度,此时我们需要对文本进行截断 .

把这些现在看起来随机的位置嵌入直接加到token嵌入,就得到了优化的具有位置信息的输入嵌入.现在,就算是相同的token,其嵌入也不同了.

```python
input_embeddings = token_embeddings + pos_embeddings
```
现在可作为LLM的核心模块的输入嵌入.

## 本章摘要
- LLM 需要将文本数据转换为数值向量，这称之为嵌入，因为它们无法处理原始文本。嵌入将离散数据（如单词或图像）转化为连续的向量空间，从而使其能够与神经网络操作兼容。
- 作为第一步，原始文本被分解为token，这些token可以是单词或字符。然后，这些token被转换为整数表示，称为token ID。
- 可以添加特殊token，如 <|unk|> 和 <|endoftext|>，以增强模型的理解能力，并处理各种上下文，例如未知单词或无关文本之间的边界分隔。
- 用于像 GPT-2 和 GPT-3 这样的 LLM 的字节对编码（BPE）分词器，可以通过将未知单词分解为子词单元或单个字符，高效地处理这些单词。
- 我们在分词后的文本数据上采用滑动窗口方法，以生成用于 LLM 训练的输入-目标对。
- 在 PyTorch 中，嵌入层作为一种查找操作，用于检索与token ID 对应的向量。生成的嵌入向量提供了token的连续表示，这在训练像 LLM 这样的深度学习模型时至关重要。
- 虽然token嵌入为每个token提供了一致的向量表示，但它们并没有考虑token在序列中的位置。为了解决这个问题，存在两种主要类型的位置嵌入：绝对位置嵌入和相对位置嵌入。OpenAI 的 GPT 模型采用绝对位置嵌入，这些位置嵌入向量会与token嵌入向量相加，并在模型训练过程中进行优化。

---
在线文档至此就结束了,可是我发现仓库里还有一些notebook.我来看看有什么内容吧~~

## 多种BPE实践比较
在`ch02/02_bonus_bytepair-encoder`里有几种GPT-2的BPE调用和性能表现比较.

## 嵌入层和常规线性层的比较
在`ch02/03_bonus_embedding-vs-matmul`里,解释了嵌入层和独热编码的全连接层是等同的.

独热编码(onehot)将整数索引放进一个零一矩阵里面来表示索引的位置:
```python
idx = idx = torch.tensor([2, 3, 1])
onehot = torch.nn.functional.one_hot(idx)
print(onehot)
```

```
tensor([[0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 1, 0, 0]])
```

```python
torch.manual_seed(123)
linear = torch.nn.Linear(num_idx, out_dim, bias=False)
print(linear.weight)
```
`linear.weight`形状是[out_dim, num_idx]

```python
linear.weight = torch.nn.Parameter(embedding.weight.T)
linear(onehot.float())
```

![](https://sebastianraschka.com/images/LLMs-from-scratch-images/bonus/embeddings-and-linear-layers/4.png)

而Linear的调用执行了矩阵乘法:
- Next, we initialize a `Linear` layer, which carries out a matrix multiplication $X W^\top$:

因此,除了初始化的矩阵随机数不同外,两种操作是等价的.但onehot占用内存更大,矩阵乘法更慢.

## `dataloader`的使用
在`ch02/04_bonus_dataloader-intuition`中简单解释了一下`dataloader`的使用,没什么特别的内容.

## 从零构建BPE
在`ch02/05_bpe-from-scratch`详细讲解了如何从零构建一个BPE,就是上面"多种BPE实践比较"中使用的BPE之一.



[^1]: Zhou K, Yu H, Zhao W X, et al. Filter-enhanced MLP is all you need for sequential recommendation[C]//Proceedings of the ACM web conference 2022. 2022: 2388-2399.
