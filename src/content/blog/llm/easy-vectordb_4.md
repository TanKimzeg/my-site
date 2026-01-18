---
title: 第四章·FAISS性能调优与评估 | EasyVecotrDB
description: 本章聚焦参数调优，提升召回率和检索速度。
pubDate: 2026 01 16 
categories: 
  - tech
tags:
  - rag
---

## 检索性能评估指标

四大核心评估指标详解：

|指标名称|核心定义|业务意义|
|---|---|---|
|**Recall@k（召回率）**|在 Top-k 检索结果中，被正确找回的真实最近邻占所有真实最近邻的比例（真实最近邻由精确搜索获得）|衡量近似检索的准确性，反映“漏检”程度，是 ANN 最核心的效果指标|
|**QPS（Queries Per Second）**|系统在单位时间内可处理的查询请求数量|衡量系统吞吐能力，决定是否能支撑高并发在线服务|
|**延迟（Latency）**|单次查询从请求到返回结果的耗时，通常统计 p50 / p95 / p99|衡量系统响应速度，直接影响实时体验（如搜索、推荐、对话系统）|
|**索引构建时间（Build Time）**|从原始向量数据构建完整索引结构所需的时间|衡量索引初始化与更新成本，影响离线构建效率与在线更新可行性|

[SIFT1M](https://huggingface.co/datasets/fzliu/sift1m/tree/main)是向量检索领域的“标准测试集”，包含100万条128维SIFT特征向量（数据库向量）和1万条查询向量，且提供查询向量对应的真实Top-100结果，是评估FAISS性能的理想数据。

先以 `IndexINFFlat` 为例，感受一下 Recall@10的指标：

```python
nlist = 100
nprobe = 5

quantizer = faiss.IndexFlatL2(d)
index_ivf = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)
```

我将本章代码整理在一个 `.ipynb` 笔记本中运行，十分方便：

```shell
uv add ipykernel
```

即可启用python内核服务。

1.4节代码的运行结果：

```log
---使用暴力搜索生成 Ground Truth---
---训练 IVF100---
开始构建 IVF100 索引 ...
---IVF 检索---

===== IVF100 四大核心指标 =====
Recall@10:        0.9361
Latency:          0.796 ms / query
QPS:              1257
Build Time:       1.20 s
```

## 核心参数调优

以下是高频索引的关键参数：

|索引类型|核心参数|参数作用|调优趋势（准确率↑/效率↑）|
|---|---|---|---|
|IVF系列（如IVF+Flat/PQ）|nlist（聚类数）|控制数据库向量的分区粒度|nlist↑→聚类更细→准确率↑、效率↓（需配合nprobe调整）|
|IVF系列|nprobe（查询聚类数）|控制查询时的搜索范围|nprobe↑→搜索范围更广→准确率↑、效率↓（核心调优参数）|
|PQ系列（如IVF+PQ）|M（子向量数）|将向量拆分为M个子向量分别量化|M↑→量化精度更高→准确率↑、内存占用↑|
|HNSW系列|ef/efConstruction|ef：查询深度；efConstruction：构建图的深度|ef↑→搜索更充分→准确率↑、效率↓|

在向量基础和第二章，我已经学习过这些关键参数。

Faiss 的索引参数分为两类，调优策略不同：

|类型|说明|示例|调优成本|
|---|---|---|---|
|**静态参数**|索引创建时确定，需重新训练 / 构建索引才能修改|IVF 的`nlist`、HNSW 的`M`、PQ 的`m`|高|
|**动态参数**|运行时可直接修改，无需重新构建索引|IVF 的`nprobe`、HNSW 的`efSearch`|低|

三种扫参方法：

|方法|原理|优点|缺点|
|---|---|---|---|
|随机搜索|从参数空间中随机采样组合|实现简单、计算量小、不易陷入局部最优|精度较低，可能错过最优参数|
|网格搜索|遍历参数空间的笛卡尔积（穷举）|结果稳定、能找到全局最优（参数范围小时）|计算量随参数维度指数增长（维度灾难）|
|贝叶斯搜索|基于贝叶斯概率模型，利用历史试验结果指导后续参数采样（Optuna 实现）|效率高、精度高（尤其适合高维参数）|实现稍复杂，依赖优化框架|

通过安装Optuna

```shell
uv add optuna
```

开始使用贝叶斯搜索。

实验运行结果：

```txt

==================================================
开始随机搜索调优HNSW参数...

随机搜索第1/20组参数：{'m': 4, 'ef_construction': 300, 'ef_search': 50}
Recall@10: 0.7136, QPS: 38145, 构建时间: 109.70s

随机搜索第2/20组参数：{'m': 16, 'ef_construction': 200, 'ef_search': 100}
Recall@10: 0.9873, QPS: 12221, 构建时间: 149.87s

随机搜索第3/20组参数：{'m': 8, 'ef_construction': 100, 'ef_search': 30}
Recall@10: 0.8143, QPS: 46277, 构建时间: 65.64s

随机搜索第4/20组参数：{'m': 8, 'ef_construction': 100, 'ef_search': 30}
Recall@10: 0.8152, QPS: 43411, 构建时间: 65.06s

随机搜索第5/20组参数：{'m': 4, 'ef_construction': 300, 'ef_search': 30}
Recall@10: 0.6226, QPS: 75766, 构建时间: 97.72s

随机搜索第6/20组参数：{'m': 32, 'ef_construction': 200, 'ef_search': 20}
Recall@10: 0.8919, QPS: 39085, 构建时间: 138.66s

随机搜索第7/20组参数：{'m': 8, 'ef_construction': 300, 'ef_search': 50}
Recall@10: 0.8983, QPS: 44597, 构建时间: 120.76s

随机搜索第8/20组参数：{'m': 16, 'ef_construction': 300, 'ef_search': 100}
Recall@10: 0.9880, QPS: 14138, 构建时间: 164.48s

随机搜索第9/20组参数：{'m': 4, 'ef_construction': 200, 'ef_search': 30}
Recall@10: 0.6163, QPS: 86063, 构建时间: 66.11s

随机搜索第10/20组参数：{'m': 8, 'ef_construction': 300, 'ef_search': 30}
Recall@10: 0.8295, QPS: 65579, 构建时间: 131.73s

随机搜索第11/20组参数：{'m': 4, 'ef_construction': 100, 'ef_search': 100}
Recall@10: 0.7794, QPS: 32039, 构建时间: 31.17s

随机搜索第12/20组参数：{'m': 8, 'ef_construction': 200, 'ef_search': 20}
...
```

通过这样扫参，可以确定性能优秀的参数。

## 大规模向量检索

- 分片索引（Sharding）
- 分布式检索（Cluster）
- 内存占用优化
