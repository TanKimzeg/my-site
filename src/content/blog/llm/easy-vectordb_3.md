---
title: 第三章·FAISS核心功能进阶 | EasyVectorDB
description: 通过“理论解析+核心 API+实战案例”的结构，帮助大家掌握复合索引设计、向量归一化、索引持久化及 GPU 加速等关键技能，解决大规模向量检索中的“精度-效率”平衡问题。
pubDate: 2026 01 15 
categories: 
  - tech
tags:
  - rag
---


## 向量归一化

我在《向量基础》中已经学习过几种衡量向量相似度的方法：余弦相似度、内积、L2距离。

$$\cos(\mathbf{a},\mathbf{b}) = \frac{\mathbf{a}\cdot \mathbf{b}}{\left \| \mathbf{a}\right \| \left \| \mathbf{b}\right \|}$$

归一化后，$\left \| \mathbf{a}\right \| = 1$, $\left \| \mathbf{b}\right \| = 1$，从而

$$\cos(\mathbf{a},\mathbf{b}) = \mathbf{a}\cdot \mathbf{b}$$

即内积。进一步地，L2距离可通过余弦相似度计算得到：

$$\left \| \mathbf{a} - \mathbf{b}\right \|^2 = 2(1-\cos(\mathbf{a}, \mathbf{b}))$$

当余弦相似度越高，L2 距离越小。

**FAISS中的API**可实现这一点：

```python
### 函数作用：对矩阵的每行（向量）做 L2 归一化
faiss.normalize_L2(x)  # x 为 numpy 数组（shape: N×d），原地修改

# 示例
x = np.array([[1,2,3], [4,5,6]], dtype=np.float32)
faiss.normalize_L2(x)
print("归一化后向量：", x)
print("归一化后向量的 L2 范数：", np.linalg.norm(x, axis=1))  # 输出 [1. 1.]
```

## 索引的保存与加载

下载数据集[SIFT1M](https://huggingface.co/datasets/fzliu/sift1m/tree/main)，

**核心API**：

|API 函数|功能描述|注意事项|
|---|---|---|
|`faiss.write_index(index, "index.path")`|将索引序列化保存到本地文件|文件格式为二进制，不可直接编辑|
|`faiss.read_index("index.path")`|从本地文件加载索引，返回索引对象|加载后可直接调用 search 方法，无需重新训练|

模拟“离线训练-保存索引-在线加载-检索”的工程化流程，验证索引保存与加载的一致性。

不愧是高性能库，索引创建的过程非常快！
实验运行记录：

```txt
向量维度d: 128
原始数据形状: (129000000,) (1290000,) (1010000,)
每个查询的近邻数k: 100
解析后数据形状: (1000000, 128) (10000, 128) (10000, 100)
开始训练IVF-PQ索引...
训练完成，开始添加数据库向量...
向量添加完成：共添加 1000000 个向量
查询参数nprobe设置为：50

IVF-PQ索引保存成功！
索引路径：IVF_PQ.index
索引大小：23.52 MB
```

> 我已经体验了CPU版本的FAISS，由于不具备NVIDIA CUDA，无法体验 `faiss-gpu`。
