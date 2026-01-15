---
title: RAG原理与实践 | LLM
description: "检索增强生成(RAG)原理与实践"
pubDate: 2025 10 25
categories:
  - tech
tags:
  - llm
  - rag
---

## 第一章 解锁RAG

RAG和Agent是最近很火的两种工程化AI应用.在我实习的中厂,他们也在弄.让我来一探究竟!从RAG开始吧.

[All in RAG](https://datawhalechina.github.io/all-in-rag/#)

在前面的博客文章中,我已经学习了LLM的架构.跟着教程前几节,熟悉RAG的概念,并搭建了学习环境.学完本教程,我希望能够搭建一个自己的知识库,甚至给学校的文档搭建RAG,用于投大创.

在第一章中,我认为首先要弄清楚几个关键问题:

- LLM为什么需要RAG?
- 如何给LLM提供RAG?

### 四步构建RAG

稍微修改并仓库提供的代码:

```txt
content='根据提供的上下文，文中举了以下例子：\n\n1.  **自然界中的羚羊**：羚羊出生后通过试错学习站立和奔跑，以适应环境。\n2.  **股票交易**：通过不断买卖股票，并根据市场反馈来学习如何最大化奖励。\n3.  **玩雅达利 游戏（如Breakout和Pong）**：通过不断试错来学习如何通关。\n4.  **选择餐馆**：利用是去已知的最喜欢的餐馆； 探索是尝试新的餐馆。\n5.  **做广告**：利用是采取已知最优的广告策略；探索是尝试新的广告策略。\n6.  **挖油**：利用是在已知有油的地方挖；探索是在新的地方尝试挖油。\n7.  **玩游戏（如《街头霸王》）**：利用是总是采取某种特定策略（如蹲角落出脚）；探索是尝试新的招式或策略。' additional_kwargs={'refusal': None} response_metadata={'token_usage': {'completion_tokens': 190, 'prompt_tokens': 5550, 'total_tokens': 5740, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 5504}, 'prompt_cache_hit_tokens': 5504, 'prompt_cache_miss_tokens': 46}, 'model_name': 'deepseek-chat', 'system_fingerprint': 'fp_ffc7281d48_prod0820_fp8_kvcache', 'id': 'c3375f8d-8515-49ac-83b1-c1ed4f7681ae', 'service_tier': None, 'finish_reason': 'stop', 'logprobs': None} id='run--132584c0-6b64-478c-b3e6-0be1f5ec91e4-0' usage_metadata={'input_tokens': 5550, 'output_tokens': 190, 'total_tokens': 5740, 'input_token_details': {'cache_read': 5504}, 'output_token_details': {}}
```

示例代码完成了RAG的关键四个步骤:

1. 数据准备
2. 索引构建
3. 查询与检索
4. 生成集成

## 第二章 数据准备

### 数据加载

我们的外部知识来源于各种非结构化数据.需要从HTML,markdown,word文档,PDF等格式中加载给大模型提供提示词.好在许多开源库已经做到了这一点.例如我之前使用的python-docx就能解析word文档.

这边使用的是[Unstructured库](https://docs.unstructured.io/open-source/core-functionality/partitioning)

```python
from unstrucured.partition.auto import partition
```

**partition函数参数解析：**

- `filename`: 文档文件路径，支持本地文件路径
- `content_type`: 可选参数，指定MIME类型（如"application/pdf"），可绕过自动文件类型检测
- `file`: 可选参数，文件对象，与filename二选一使用
- `url`: 可选参数，远程文档URL，支持直接处理网络文档
- `include_page_breaks`: 布尔值，是否在输出中包含页面分隔符
- `strategy`: 处理策略，可选"auto"、"fast"、"hi_res"等
- `encoding`: 文本编码格式，默认自动检测

> 示例代码跑不出来,运行速度太慢了...

### 文本分块

文本分块（Text Chunking）是构建RAG流程的关键步骤。其核心原理是将加载后的长篇文档，切分成更小、更易于处理的单元。这些被切分出的文本块，是后续向量检索和模型处理的**基本单位**。

#### 基础分块策略

##### 固定大小分块

这是最简单直接的分块方法。

```python
from langchain.text_splitter import CharacterTextSplitter 
from langchain_community.document_loaders import TextLoader
```

LangChain的实现更准确地应该称为"段落感知的自适应分块"，块大小会根据段落边界动态调整。

##### 递归字符分块

**与固定大小分块的关键差异**：

- 固定大小分块遇到超长段落时只能发出警告并保留。
- 递归分块会继续使用更细粒度的分隔符（句子→单词→字符）直到满足大小要求。

```python
text_splitter = RecursiveCharacterTextSplitter(
  separators=["\n\n", "\n", "。", "，", " ", ""], # 分隔符优先级 
  chunk_size=200, 
  chunk_overlap=10, 
)
```

**分隔符配置**：

- **默认分隔符**：`["\n\n", "\n", " ", ""]`
- **多语言支持**：对于无词边界语言（中文、日文、泰文），可添加：

```python
separators=[
    "\n\n", "\n", " ",
    ".", ",", "\u200b",      # 零宽空格(泰文、日文)
    "\uff0c", "\u3001",      # 全角逗号、表意逗号
    "\uff0e", "\u3002",      # 全角句号、表意句号
    ""
]
```

**编程语言特化支持**： `RecursiveCharacterTextSplitter` 能够针对特定的编程语言（如Python, Java等）使用预设的、更符合代码结构的分隔符。它们通常包含语言的顶级语法结构（如类、函数定义）和次级结构（如控制流语句），以实现更符合代码逻辑的分割。

```python
# 针对代码文档的优化分隔符
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,  # 支持Python、Java、C++等
    chunk_size=500,
    chunk_overlap=50
)
```

##### 语义分块

调用嵌入模型,在语义主题发生显著变化的地方进行分块

##### 基于文档结构的分块

针对结构清晰的 Markdown 文档，利用其标题层级进行分块是一种高效且保留了丰富语义的方法。LangChain 提供了 `MarkdownHeaderTextSplitter` 来处理。

- **局限性与组合使用**: 单纯按标题分割可能会导致一个问题：某个章节下的内容可能非常长，远超模型能处理的上下文窗口。为了解决这个问题，`MarkdownHeaderTextSplitter` 可以与其它分块器（如 `RecursiveCharacterTextSplitter`）**组合使用**。具体流程是：

    1. 第一步，使用 `MarkdownHeaderTextSplitter` 将文档按标题分割成若干个大的、带有元数据的逻辑块。
    2. 第二步，对这些逻辑块再应用 `RecursiveCharacterTextSplitter`，将其进一步切分为符合 `chunk_size` 要求的小块。由于这个过程是在第一步之后进行的，所有最终生成的小块都会**继承**来自第一步的标题元数据。
- **RAG应用优势**: 这种两阶段的分块方法，既保留了文档的宏观逻辑结构（通过元数据），又确保了每个块的大小适中，是处理结构化文档进行RAG的理想方案。

#### ChunkViz：简易的可视化分块工具

[ChunkViz](https://chunkviz.up.railway.app/)

## 第三章 索引构建

### 向量数据库

```python
loaded_vectorstore = FAISS.load_local(
    local_faiss_path,
    embedding_model,
    allow_dangerous_deserialization=True
)
# 相似性搜索
query = "droupout 的作用是什么?"
results = loaded_vectorstore.similarity_search(
    query,
    k=1,
    filter={"categories": {"$gte": ["tech"]}}  # 示例过滤条件
)
```

效果不错!

```txt
FAISS index has been saved to ./faiss_index_store

查询: 'droupout 的作用是什么?'
相似度最高的段落:

Dropout 在深度学习中是一种技术，即在训练过程中随机忽略一些隐藏层单元，实际上将它们“丢弃”。这种方法有助于防止过拟合，确保模型不会过于依赖任何特定的隐藏层单元组合。

![](https://skindhu.github.io/Build-A-Large-Language-Model-CN/Image/chapter3/figure3.22.png)

当对注意力权重矩阵应用 50% 的 dropout 时，矩阵中一半的元素会被随机设置为零。为了补偿有效元素的减少，矩阵中剩余元素的值会被放大 1/0.5 = 2 倍。这个缩放操作至关重要，可以在训练和推理阶段保持注意力机制的整体权重平衡，确保注意力机制在这两个阶段的平均影响保持一致。
```

## 第四章 检索优化

- [ ] 待补充

## 第五章 生成集成

- [ ] 待补充

### 第八章 项目实战一（基础篇）

看完这一章，我跟着编写了一个简单的
[博客文章RAG检索应用](https://github.com/TanKimzeg/blog-articles-rag)，进一步可以构建自己的外部知识库。

## 总结

我们深入了解了RAG的核心原理和实践步骤。从数据准备、文本分块，到索引构建、查询与检索，最后实现生成集成，每一步都至关重要。RAG不仅提升了LLM在特定领域的表现，还为我们提供了一种有效利用外部知识的方法。希望大家能够将所学应用到实际项目中，打造出更智能、更高效的AI系统。
