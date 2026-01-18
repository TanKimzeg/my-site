---
title: 第一章·FAISS入门与环境搭建 | EasyVectorDB
description: 本章节将带大家从FAISS的核心认知出发，完成环境搭建，并通过核心数据结构解析与基础示例实践，建立对FAISS的完整入门认知，为后续进阶学习奠定基础。
pubDate: 2026 01 12 
categories: 
  - tech
tags:
  - rag
---
[EasyVectorDB 向量数据库学习指南](https://datawhalechina.github.io/easy-vecdb/)

## FAISS核心定位与生态

三大核心向量数据库对比

|特性|Annoy|Faiss|Milvus|
|---|---|---|---|
|**定位**|轻量级静态索引|高性能科研工具|企业级云原生数据库|
|**开发商**|Spotify|Facebook AI Research|Zilliz|
|**核心优势**|极简、快速、低内存|算法丰富、GPU加速|分布式、高可用、企业级|
|**适用规模**|百万-千万级|千万-十亿级|十亿级以上|
|**部署复杂度**|极简|中等|较高|
|**典型应用**|音乐推荐、内容推荐|图像检索、科研实验|企业知识库、大规模推荐|

> FAISS是“向量检索库”而非完整的“数据库”，不具备传统数据库的事务、权限管理等特性，若需企业级高可用服务，需结合Milvus等向量数据库或自行封装服务化组件。

## FAISS环境搭建

FAISS的安装也非常简单，在all-in-rag的课程中，我用过FAISS作为向量数据库。

```shell
uv init
uv add faiss-cpu
```

> 好想拥有一台有独显的计算机啊~~

## FAISS核心数据结构

### Index类体系

基类Index定义了所有向量索引都必须实现的核心方法，这些方法构成了FAISS的基础API，主要包括：

- **add(x)**：将向量数据x添加到索引中，x的形状为（num_vectors, dimension），数据类型需为float32（FAISS的标准数据类型）。
- **search(x, k)**：在索引中检索与x最相似的k个向量，返回距离数组（distances）和索引数组（indices）。
- **reset()**：清空索引中的所有向量数据，重置索引状态。
- **save(filename)/load(filename)**：将索引保存到磁盘或从磁盘加载索引，便于持久化存储。
- **is_trained**：属性，返回布尔值，表示索引是否已“训练”完成（部分近似索引需先训练才能使用）。
- **ntotal**：属性，返回索引中存储的向量总数。

FAISS提供了数十种Index派生类，根据检索精度可分为“精确检索索引”和“近似检索索引”两大类。

### 数据格式与维度要求

- **数据类型**：FAISS仅支持32位浮点数（float32）类型的向量，若输入的是Python列表或NumPy的float64数组，需先进行类型转换，否则会报错。
- **数据结构**：输入向量需为二维数组，形状为（num_vectors, dimension），其中num_vectors是向量的数量，dimension是单个向量的维度（所有向量维度必须一致）。 FAISS的索引对象在创建时会固定向量维度（由构造函数的参数指定），后续添加的向量必须与该维度一致，否则会抛出维度不匹配的错误。

- **数据来源适配**：

  - **NumPy数组**：FAISS的首选输入格式，可直接通过add()方法添加。

  - **PyTorch/TensorFlow张量**：需先转换为NumPy数组，再转换为float32类型，例如：`tensor.numpy().astype('float32')`。

  - **Python列表**：需先通过 `np.array()` 转换为NumPy数组，再处理类型和形状。

### ID映射机制

默认情况下，FAISS为添加到索引的向量分配自增的整数ID（从0开始），但在实际应用中，我们常需要将向量与自定义ID（如图片ID、文本ID）关联。FAISS通过IndexIDMap包装类实现这一功能。

IndexIDMap的作用是为基础索引（如IndexFlatL2）添加ID映射层，允许用户在添加向量时指定自定义ID，步骤如下：

```python
import faiss
import numpy as np

dimension = 128
num_vectors = 100

# 1. 生成向量和自定义ID（例如图片ID：10001~10100）
vectors = np.random.random((num_vectors, dimension)).astype('float32')
custom_ids = np.arange(10001, 10001 + num_vectors).astype('int64')  # 自定义ID需为int64类型

# 2. 创建基础索引，并使用IndexIDMap包装
base_index = faiss.IndexFlatL2(dimension)
index = faiss.IndexIDMap(base_index)  # 包装后支持自定义ID

# 3. 添加向量时指定自定义ID（add_with_ids方法）
index.add_with_ids(vectors, custom_ids)
print("索引中的向量数量：", index.ntotal)

# 4. 检索时返回的是自定义ID
query_vector = np.random.random((1, dimension)).astype('float32')
k = 5
distances, indices = index.search(query_vector, k)

print("查询结果自定义ID：", indices)  # 输出10001~10100范围内的ID
print("查询结果距离：", distances)
```

- **自定义ID类型**：必须为64位整数（int64），否则会导致ID映射错误。
- **ID唯一性**：添加的自定义ID需唯一，若重复添加相同ID，后续添加的向量会覆盖之前的向量。
- **索引操作兼容性**：包装后的IndexIDMap支持基础索引的所有方法（如search、reset），但部分近似索引（如IndexIVFPQ）需先训练基础索引，再进行包装和添加ID。

## FAISS基础API

|API方法|功能描述|关键参数|
|---|---|---|
|faiss.IndexFlatL2(d)|创建基于L2距离的精确检索索引|d：向量维度|
|index.add(x)|向索引添加向量|x：形状为（N, d）的float32数组|
|index.search(x, k)|检索与x最相似的k个向量|x：查询向量数组；k：返回结果数|
|index.save(filename)|将索引保存到磁盘|filename：保存路径|
|faiss.read_index(filename)|从磁盘加载索引|filename：索引路径|
|index.reset()|清空索引中的所有向量|无|
|index.ntotal|属性，获取索引中的向量总数|无|
