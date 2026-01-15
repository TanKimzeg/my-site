---
title: 向量ANN搜索算法 | EasyVectorDB
description: ANN（Approximate Nearest Neighbors）搜索是一种用于在高维空间中快速查找最近邻的算法。与暴力搜索不同，ANN搜索通过引入近似计算，在保持较高召回率的同时，显著减少了计算复杂度。
pubDate: 2026 01 13 
categories: 
  - tech
tags:
  - rag
---

ANN（Approximate Nearest Neighbors）搜索是一种用于在高维空间中快速查找最近邻的算法。与暴力搜索不同，ANN搜索通过引入近似计算，在保持较高召回率的同时，显著减少了计算复杂度。

## INF算法

倒排文件索引。（Inverted File Index）：使用 K-Means 将向量聚成多个簇（Cluster），搜索时只在最相近的几个簇内查找。

### 第一阶段：索引构建

1. 聚类训练

 使用聚类算法（通常是K-mean算法）将所有向量划分成nlist个簇。nlist是一个关键参数，它决定了空间划分的粒度。每个簇都有一个中心点，称为​​质心（centroid）​​。所有这些质心构成了一个“质心表”。

2. 向量分配

 遍历数据集中的每一个向量，计算它与所有质心的距离（如欧氏距离）。将每个向量分配到​​距离它最近的那个质心​​所对应的簇中。

3. 形成倒排表

 为每一个簇建立一个​​倒排列表​​。这个列表就像图书馆每个分类书架上的图书清单，它记录了所有属于这个簇的​​向量的ID以及向量本身​​（或它的压缩表示）。至此，索引构建完成。

```python
class SimpleKMeans:
    """简化的K-means实现用于IVF聚类"""
    def __init__(self, n_clusters=3, max_iters=100):
        self.n_clusters = n_clusters
        self.max_iters = max_iters
        self.centroids = None
        self.labels_ = None
    def fit(self, X: np.ndarray):
        n_samples, n_features = X.shape
        # 1. 随机初始化质心
        random_indices = np.random.choice(n_samples, self.n_clusters, replace=False)
        self.centroids = X[random_indices]
        for iteration in range(self.max_iters):
            # 2. 分配每个点到最近的质心
            distances = euclidean_distances(X, self.centroids)
            labels = np.argmin(distances, axis=1)
            # 3. 更新质心位置
            new_centroids = np.array([X[labels == i].mean(axis=0) for i in range(self.n_clusters)])
            # 检查收敛
            if np.allclose(self.centroids, new_centroids):
                break
            self.centroids = new_centroids
            self.labels_ = labels
        return self
```

### 第二阶段：查询处理

1. 定位最近簇：计算查询向量与质心表中所有nlist个簇的距离
2. 选择候选簇： 根据上一步的距离结果，选择距离最近的 nprobe个簇作为候选簇。​​nprobe是IVF算法中最关键的调优参数之一​​： nprobe越小，搜索范围越小，​​速度越快，但可能漏掉一些真正近邻（召回率降低）​​。 nprobe越大，搜索范围越大，​​召回率越高，但计算量增大，速度变慢​​。
3. 簇内精细比较：在选定的 nprobe个候选簇的倒排列表中，进行精细的距离计算。
 具体方式取决于IVF的变体：

- IVF-Flat：直接使用原始的、未压缩的向量与查询向量进行精确距离计算。这种方式精度最高，但内存占用也最大。
- IVF-PQ：为了进一步节省内存和加速计算，会对簇内向量使用乘积量化（Product Quantization） 进行压缩。搜索时使用近似距离计算，这是一种用少量精度换取巨大存储和计算效率提升的策略。

4. 结果合并与返回：将所有候选簇中的向量根据与查询向量的距离进行排序，最终返回 Top-K 个最相似的向量作为结果。

```python
class SimpleIVF:
    """简化的IVF实现"""
    def __init__(self, n_clusters=3, n_probe=2):
        self.n_clusters = n_clusters
        self.n_probe = n_probe  # 搜索时探测的簇数量
        self.kmeans = None
        self.inverted_lists = None  # 倒排列表
        self.centroids = None
        self.is_trained = False
        self.data = None
    
    def train(self, data):
        """训练IVF索引：对数据进行聚类"""
        print("开始训练IVF索引...")
        self.kmeans = SimpleKMeans(n_clusters=self.n_clusters)
        self.kmeans.fit(data)
        self.centroids = self.kmeans.centroids
        self.is_trained = True
        print(f"训练完成，得到{self.n_clusters}个簇")
    
    def build_index(self, data):
        """构建倒排索引"""
        if not all([self.is_trained, self.data, self.centroids]):
            self.train(data)
        self.data = data
        
        # 初始化倒排列表
        self.inverted_lists = defaultdict(list)
        
        # 将每个向量分配到最近的簇
        distances = euclidean_distances(data, self.centroids)
        labels = np.argmin(distances, axis=1)
        
        # 构建倒排列表：簇ID -> 该簇中所有向量的索引
        for idx, label in enumerate(labels):
            self.inverted_lists[label].append(idx)
        
        print("倒排索引构建完成:")
        for cluster_id, items in self.inverted_lists.items():
            print(f"  簇{cluster_id}: {len(items)}个向量")

    def search(self, query: np.ndarray, k=5):
        """IVF搜索：先找最近的簇，然后在簇内搜索"""
            
        # 1. 粗略搜索：找到最近的n_probe个簇
        distances_to_centroids = euclidean_distances(query.reshape(1, -1), self.centroids)[0]
        nearest_cluster_indices = np.argsort(distances_to_centroids)[:self.n_probe]
        
        # 2. 精细搜索：在选中的簇内进行暴力搜索
        if self.inverted_lists is None or self.data is None:
            raise ValueError("倒排列表未构建，请先调用build_index()方法。")
        candidate_indices = []
        for cluster_idx in nearest_cluster_indices:
            candidate_indices.extend(self.inverted_lists[cluster_idx])
        
        if not candidate_indices:
            return [], []
        
        # 在候选向量中计算距离
        candidate_vectors = self.data[candidate_indices]
        distances = euclidean_distances(query.reshape(1, -1), candidate_vectors)[0]
        
        # 获取最近的k个结果
        if k > len(distances):
            k = len(distances)
            
        nearest_indices_within_candidates = np.argsort(distances)[:k]
        
        # 映射回原始索引
        final_indices = [candidate_indices[i] for i in nearest_indices_within_candidates]
        final_distances = distances[nearest_indices_within_candidates]
        
        return final_indices, final_distances
    
    def brute_force_search(self, query: np.ndarray, k=5):
        """暴力搜索作为对比基准"""
        if self.data is None:
            raise ValueError("数据未加载，请先构建索引或提供数据。")

        distances = euclidean_distances(query.reshape(1, -1), self.data)[0]
        nearest_indices = np.argsort(distances)[:k]
        return nearest_indices, distances[nearest_indices]
```

> 代码经过我的优化可直接运行无类型错误警告。

下面直观展示INF算法的训练、构建和查询过程：

![INF算法训练、构建和查询过程](https://datawhalechina.github.io/easy-vectordb/images/IVF%E7%AE%97%E6%B3%95%E7%BB%93%E6%9E%9C.png)

## PQ算法

PQ（**Product Quantization，乘积量化**）是一种**高效的向量压缩与近似距离计算方法**，  
主要应用于大规模向量检索中，用于降低**存储成本**和**计算开销**，同时保持较高的近似精度。

PQ 的核心思想是：

> **将高维向量拆分为多个子向量，在子空间内进行独立量化，再通过查表法快速计算近似距离。**

### 向量分块

假设原始向量$\mathbf{x}\in{\mathbb{R}^D}$,将其划分为$m$个子空间：
$$\mathbf{x}=[\mathbf{x}_{1},\mathbf{x}_{2},\dots \mathbf{x}_{m}],\mathbf{x}_{i}\in \mathbb{R}^{D/m}$$,每个子向量在对应的子空间独立处理，减少维度对量化的复杂性。

### 子空间量化

1. 对每个子空间 $\mathbf{x}_{i}$ 构建一个**子码本（Codebook）**： 使用聚类算法（如 K-Means）将该子空间向量划分为 $k$ 个聚类中心：$$C_{i}={c_{i,1},c_{i,2},…,c_{i,k}}$$
2. 将每个子向量 $\mathbf{x}_{i}$ 替换为其最近的聚类中心编号 $q_{i}$：$qi=\text{arg min}_{j}\left \|  xi−c_{i,j} \right \|$
3. 最终，一个高维向量被表示为一组整数索引：$\mathbf{x}≈[q1,q2,…,qm]$

✅ 这就是 PQ 的核心压缩方式，将浮点向量转为低位整数索引，大幅节省存储。

### 近似距离计算

当有查询向量 $\mathbf{y}$ 时：

1. 将查询向量同样划分为 $m$ 个子向量：$\mathbf{y}=[\mathbf{y}_{1},\mathbf{y}_{2},…,\mathbf{y}_{m}]$
2. 对每个子向量 $\mathbf{y}_{i}$ 与对应子码本 $C_{i}$ 计算**子空间距离表**：$D_{i}[j]=\left \| \mathbf{y}_{i}−c_{i,j} \right \| ^2,j=1,…,k$
3. 向量 $\mathbf{x}$ 与 $\mathbf{y}$ 的近似距离可通过查表法快速计算：$\left \| \mathbf{y}−\mathbf{x} \right \|^2≈∑_{i=1}^mD_{i}[q_{i}]$

```python
class ProductQuantization:
    """乘积量化算法实现"""
    
    def __init__(self, dim:int, M=8, K=256):
        """
        初始化PQ参数
        
        参数:
        - M: 子空间数量（将向量分割成多少段）
        - K: 每个子空间的聚类中心数量（必须是2的幂次，如256=2^8）
        """
        self.M = M
        self.K = K
        self.codebooks = None  # 码本：存储每个子空间的聚类中心
        self.sub_dim = dim // M  # 每个子空间的维度
        self.is_trained = False
    
    def train(self, vectors: np.ndarray, max_iter=100):
        """
        训练PQ码本
        
        参数:
        - vectors: 训练数据，形状为 (n_vectors, dim)
        - max_iter: K-means最大迭代次数
        """
        n_vectors, dim = vectors.shape
        
        # 检查维度是否可被M整除
        if dim % self.M != 0:
            raise ValueError(f"向量维度{dim}不能被M={self.M}整除")
        
        self.sub_dim = dim // self.M
        self.codebooks = np.zeros((self.M, self.K, self.sub_dim), dtype=np.float32)
        
        print(f"开始训练PQ码本: {dim}维向量分割为{self.M}个子空间，每个子空间{self.sub_dim}维")
        print(f"每个子空间使用K={self.K}个聚类中心")
        
        # 对每个子空间分别进行K-means聚类
        for m in range(self.M):
            print(f"训练子空间 {m+1}/{self.M}...")
            
            # 提取当前子空间的数据
            sub_vectors = vectors[:, m*self.sub_dim:(m+1)*self.sub_dim]
            
            # 使用K-means聚类
            # kmeans2返回聚类中心和每个点所属的簇标签
            centroids, labels = kmeans2(sub_vectors, self.K, iter=max_iter, minit='points')
            self.codebooks[m] = centroids.astype(np.float32)
        
        self.is_trained = True
        print("PQ码本训练完成!")
        return self.codebooks
    
    def encode(self, vectors: np.ndarray):
        """
        将向量编码为PQ码
        
        参数:
        - vectors: 待编码的向量，形状为 (n_vectors, dim)
        
        返回:
        - codes: PQ编码，形状为 (n_vectors, M)，每个元素是0到K-1的整数
        """
        if not self.is_trained or self.codebooks is None:
            raise ValueError("请先训练PQ码本")
        
        n_vectors = vectors.shape[0]
        codes = np.zeros((n_vectors, self.M), dtype=np.uint8)
        
        for m in range(self.M):
            # 提取当前子空间的向量
            sub_vectors = vectors[:, m*self.sub_dim:(m+1)*self.sub_dim]
            
            # 为每个子向量找到最近的聚类中心
            labels, _ = vq(sub_vectors, self.codebooks[m])
            codes[:, m] = labels
        
        return codes
    
    def decode(self, codes: np.ndarray):
        """
        将PQ码解码为近似向量
        
        参数:
        - codes: PQ编码，形状为 (n_vectors, M)
        
        返回:
        - approx_vectors: 近似向量，形状为 (n_vectors, dim)
        """
        if not self.is_trained or self.codebooks is None:
            raise ValueError("请先训练PQ码本")
        
        n_vectors = codes.shape[0]
        dim = self.M * self.sub_dim
        approx_vectors = np.zeros((n_vectors, dim), dtype=np.float32)
        
        for m in range(self.M):
            # 用聚类中心替换编码
            approx_vectors[:, m*self.sub_dim:(m+1)*self.sub_dim] = \
                self.codebooks[m][codes[:, m]]
        
        return approx_vectors
    
    def build_distance_table(self, query):
        """
        构建查询向量的距离表（ADC: Asymmetric Distance Computation）
        
        参数:
        - query: 查询向量，形状为 (dim,)
        
        返回:
        - dist_table: 距离表，形状为 (M, K)
        """
        if not self.is_trained or self.codebooks is None:
            raise ValueError("请先训练PQ码本")
        
        dist_table = np.zeros((self.M, self.K), dtype=np.float32)
        
        for m in range(self.M):
            # 提取查询向量的子向量
            query_sub = query[m*self.sub_dim:(m+1)*self.sub_dim]
            
            # 计算查询子向量到当前子空间所有聚类中心的距离
            dist_table[m] = cdist([query_sub], self.codebooks[m], 'sqeuclidean')[0]
        
        return dist_table
    
    def search(self, query: np.ndarray, codes: np.ndarray, top_k=5):
        """
        使用PQ进行近似最近邻搜索
        
        参数:
        - query: 查询向量，形状为 (dim,)
        - codes: 数据库向量的PQ编码，形状为 (n_vectors, M)
        - top_k: 返回最相似的top_k个结果
        
        返回:
        - indices: 最近邻的索引
        - distances: 对应的距离
        """
        if not self.is_trained:
            raise ValueError("请先训练PQ码本")
        
        # 构建距离表
        dist_table = self.build_distance_table(query)
        
        n_vectors = codes.shape[0]
        distances = np.zeros(n_vectors, dtype=np.float32)
        
        # 计算每个数据库向量与查询向量的近似距离
        for i in range(n_vectors):
            for m in range(self.M):
                # 累加每个子空间的距离
                distances[i] += dist_table[m, codes[i, m]]
        
        # 返回距离最小的top_k个结果
        indices = np.argsort(distances)[:top_k]
        return indices, distances[indices]

    def brute_force_search(self, query: np.ndarray, vectors: np.ndarray, top_k=5):
        """
        暴力搜索作为基准对比
        """
        distances = cdist([query], vectors, 'sqeuclidean')[0]
        indices = np.argsort(distances)[:top_k]
        return indices, distances[indices]
```

### 小结

**PQ 的核心优势**：

- **高压缩率**：将浮点向量压缩为整数索引，存储占用大幅下降；
- **高效距离计算**：通过查表法快速估算距离，降低计算量；
- **可组合性强**：可与 IVF、HNSW 等索引结构结合，实现高效大规模检索；
- **近似精度可调**：通过调整子向量数 $m$ 和聚类中心数 $k$ 平衡精度与存储。

经过我的实验，子空间数量M在召回率上起的作用比K大，而且在实验场景下慢于暴力搜索，说明这段Python代码的缓存优化很差。

```log
============================================================
PQ算法演示
生成训练数据...
训练数据: (5000, 128)
数据库数据: (10000, 128)
开始训练PQ码本: 128维向量分割为8个子空间，每个子空间16维
每个子空间使用K=256个聚类中心
训练子空间 1/8...
训练子空间 2/8...
训练子空间 3/8...
训练子空间 4/8...
训练子空间 5/8...
训练子空间 6/8...
训练子空间 7/8...
训练子空间 8/8...
PQ码本训练完成!
训练耗时: 2.2187秒
编码耗时: 0.0486秒
压缩比: 24.26x
原始大小: 5000.00 KB
压缩后: 206.12 KB

搜索结果对比:
PQ搜索    - 找到5个最近邻, 耗时: 0.023889秒
暴力搜索 - 找到5个最近邻, 耗时: 0.008069秒
速度提升: 0.34倍

PQ结果索引: [   0 1000 4472  512 4080]
PQ结果距离: [ 6.1899347 11.832801  12.133605  12.273722  12.286916 ]
暴力搜索结果索引: [   0 5260 9000 2456 5820]
暴力搜索结果距离: [ 0.         15.6129819  16.08607458 16.3027682  16.46445402]
Top-5召回率: 20.00% (1/5)
============================================================
PQ算法演示
============================================================
生成训练数据...
训练数据: (5000, 128)
数据库数据: (10000, 128)
开始训练PQ码本: 128维向量分割为8个子空间，每个子空间16维
每个子空间使用K=512个聚类中心
训练子空间 1/8...
训练子空间 2/8...
训练子空间 3/8...
训练子空间 4/8...
训练子空间 5/8...
训练子空间 6/8...
训练子空间 7/8...
训练子空间 8/8...
PQ码本训练完成!
训练耗时: 3.4817秒
编码耗时: 0.0739秒
压缩比: 14.96x
原始大小: 5000.00 KB
压缩后: 334.12 KB

搜索结果对比:
PQ搜索    - 找到5个最近邻, 耗时: 0.022838秒
暴力搜索 - 找到5个最近邻, 耗时: 0.005850秒
速度提升: 0.26倍

PQ结果索引: [ 716 1980 9648 8016 6556]
PQ结果距离: [13.538303 14.167534 14.455566 14.779416 14.861414]
暴力搜索结果索引: [   0 5260 9000 2456 5820]
暴力搜索结果距离: [ 0.         15.6129819  16.08607458 16.3027682  16.46445402]
Top-5召回率: 0.00% (0/5)
============================================================
PQ算法演示
============================================================
生成训练数据...
训练数据: (5000, 128)
数据库数据: (10000, 128)
开始训练PQ码本: 128维向量分割为16个子空间，每个子空间8维
每个子空间使用K=256个聚类中心
训练子空间 1/16...
训练子空间 2/16...
训练子空间 3/16...
训练子空间 4/16...
训练子空间 5/16...
训练子空间 6/16...
训练子空间 7/16...
训练子空间 8/16...
训练子空间 9/16...
训练子空间 10/16...
训练子空间 11/16...
训练子空间 12/16...
训练子空间 13/16...
训练子空间 14/16...
训练子空间 15/16...
训练子空间 16/16...
PQ码本训练完成!
训练耗时: 4.5288秒
编码耗时: 0.0869秒
压缩比: 17.59x
原始大小: 5000.00 KB
压缩后: 284.25 KB

搜索结果对比:
PQ搜索    - 找到5个最近邻, 耗时: 0.045630秒
暴力搜索 - 找到5个最近邻, 耗时: 0.004990秒
速度提升: 0.11倍

PQ结果索引: [   0 7760 3736  652 8548]
PQ结果距离: [ 4.175756 13.200957 13.299522 13.447816 13.517618]
暴力搜索结果索引: [   0 5260 9000 2456 5820]
暴力搜索结果距离: [ 0.         15.6129819  16.08607458 16.3027682  16.46445402]
Top-5召回率: 20.00% (1/5)
============================================================
PQ算法演示
============================================================
生成训练数据...
训练数据: (5000, 128)
数据库数据: (10000, 128)
开始训练PQ码本: 128维向量分割为32个子空间，每个子空间4维
每个子空间使用K=256个聚类中心
训练子空间 1/32...
训练子空间 2/32...
训练子空间 3/32...
训练子空间 4/32...
训练子空间 5/32...
训练子空间 6/32...
训练子空间 7/32...
训练子空间 8/32...
训练子空间 9/32...
训练子空间 10/32...
训练子空间 11/32...
训练子空间 12/32...
训练子空间 13/32...
训练子空间 14/32...
训练子空间 15/32...
训练子空间 16/32...
训练子空间 17/32...
训练子空间 18/32...
训练子空间 19/32...
训练子空间 20/32...
训练子空间 21/32...
训练子空间 22/32...
训练子空间 23/32...
训练子空间 24/32...
训练子空间 25/32...
训练子空间 26/32...
训练子空间 27/32...
训练子空间 28/32...
训练子空间 29/32...
训练子空间 30/32...
训练子空间 31/32...
训练子空间 32/32...
PQ码本训练完成!
训练耗时: 5.6275秒
编码耗时: 0.1133秒
压缩比: 11.35x
原始大小: 5000.00 KB
压缩后: 440.50 KB

搜索结果对比:
PQ搜索    - 找到5个最近邻, 耗时: 0.088496秒
暴力搜索 - 找到5个最近邻, 耗时: 0.003024秒
速度提升: 0.03倍

PQ结果索引: [   0 9000 5820 9200 5564]
PQ结果距离: [ 1.4812891 14.158425  14.903692  15.362539  15.634869 ]
暴力搜索结果索引: [   0 5260 9000 2456 5820]
暴力搜索结果距离: [ 0.         15.6129819  16.08607458 16.3027682  16.46445402]
Top-5召回率: 60.00% (3/5)
```

## HNSW算法

HNSW（**Hierarchical Navigable Small World**，分层可导航小世界图）是一种基于图结构的**近似最近邻（ANN）搜索算法**。

### 图结构的构建

1. 随机分配层级
 每个向量被随机分配到某一层，层数越高，节点越少，数量分布遵循指数衰减规律。

2. 逐层插入新节点
 当新向量$\mathbf{v}$进入系统时，从给它分配的那一层开始往下逐层插入新节点。在当前层，从入口点开始，运用BFS算法找到与$\mathbf{v}$最接近的一系列节点。这一系列节点更新它们的邻居集合，把新节点加进邻居集合里面（邻居集合有修剪）。其中最近的那个节点作为下一层的入口点。同时，在下一层，加入新节点及其刚刚搜索到的邻居集合。

 也就是说，上一层有的节点，一定存在于下一层中。

3. 查询阶段
 从最高层的入口节点开始，运用BFS算法找到与查询向量$\mathbf{q}$最接近的一个节点，作为下一层的入口节点。
 逐步向下，直到最底层逐步缩小搜索范围，节点密度逐渐增大，返回最近邻居中前k个结果。

经过我的实验，在固定`np.random.seed(41)`的情况下，召回率有时为0%，有时为100%，这很诡异你知道吗……

然后我发现代码里面有`random.random()` 问题可能出在这里。`np.random.seed()`与系统的 `random.seed()` 并不一致。果然，当我把`random_level()`函数里面的`random.random`改用 `np`里面的random，并且设置 `np.random.seed(42)` 后，就可以稳定100%了；而设置 `random.seed(41)`后，就效果稳定0%，召回的样本也都一摸一样。这启示我们可以通过精心选择seed来达到SOTA😆。

```python
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import euclidean_distances


class SimpleHNSW:
    """简化的HNSW实现，用于学习演示"""
    
    def __init__(
            self, 
            max_elements=1000, 
            M: int=10, 
            ef_construction: int=50, 
            max_layers: int=6
        ) -> None:
        """
        初始化HNSW索引
        
        参数:
        - max_elements: 最大元素数量
        - M: 每个节点的最大连接数
        - ef_construction: 构建时的搜索范围
        - max_layers: 最大层数
        """
        self.max_elements = max_elements
        self.M = M  # 每个节点的最大连接数
        self.ef_construction = ef_construction  # 构建时的搜索范围
        self.max_layers = max_layers  # 最大层数
        
        # 存储所有数据点
        self.data_points = []
        # 每层的图结构（邻接表），每层是一个字典，key是节点ID，value是邻居列表
        self.layers = [defaultdict(list) for _ in range(max_layers)]
        # 全局入口点（最高层的节点）
        self.entry_point = None
        self.entry_level = -1  # 入口点所在的最高层级
        
    def _random_level(self) -> int:
        """随机生成节点的层级（指数分布）"""
        level = 0
        while np.random.random() < 0.5 and level < self.max_layers - 1:
            level += 1
        return level
    
    def _euclidean_distance(
            self, a: np.ndarray, b: np.ndarray
        ) -> np.float64:
        """计算欧氏距离"""
        return np.sqrt(np.sum((a - b) ** 2))
    
    def _search_layer(
            self, query: np.ndarray, entry_point: int, ef: int, layer: int
        ) -> list[tuple[np.float64, int]]:
        """
        在指定层搜索最近邻
        
        参数:
        - query: 查询向量
        - entry_point: 搜索起始点
        - ef: 搜索范围（返回的候选点数量）
        - layer: 搜索的层级
        """
        if entry_point is None or entry_point not in self.layers[layer]:
            return []
            
        visited = set([entry_point])
        # 候选集：存储(距离, 节点ID)元组，从入口点开始
        candidates: list[tuple[float, int]] = [(self._euclidean_distance(query, self.data_points[entry_point]), entry_point)]
        # 使用堆来维护候选集（这里简化为列表排序）
        results = []
        
        while candidates and len(results) < ef:
            # 获取距离最近的候选点
            candidates.sort(key=lambda x: x[0])
            current_dist, current_point = candidates.pop(0)
            
            # 检查是否应该将当前点加入结果
            if (not results or current_dist < results[-1][0]) and len(results) < ef:
                results.append((current_dist, current_point))
                results.sort(key=lambda x: x[0])  # 保持结果按距离排序
            
            # 探索当前点的所有邻居节点
            for neighbor in self.layers[layer][current_point]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    dist = self._euclidean_distance(query, self.data_points[neighbor])
                    candidates.append((dist, neighbor))
        
        return results

    def add_point(self, point: np.ndarray) -> None:
        """
        向HNSW中添加新点
        
        参数:
        - point: 要添加的数据点向量
        """
        if len(self.data_points) >= self.max_elements:
            raise ValueError("达到最大容量")
        
        point_id = len(self.data_points)  # 新点在data_points中的id索引
        self.data_points.append(point)
        
        # 确定新点的层级
        level = self._random_level()
        
        # 如果是第一个点，设为入口点
        if self.entry_point is None:
            self.entry_point = point_id
            self.entry_level = level
            for l in range(level + 1):
                self.layers[l][point_id] = []  # 在新点的每一层创建空邻居列表
            return
        
        # 从最高层开始搜索，找到每层的最近邻
        current_point = self.entry_point
        current_max_level = self.entry_level
        
        # 从顶层开始搜索，找到每层的入口点
        for l in range(current_max_level, level, -1):
            if l < len(self.layers):
                results = self._search_layer(point, current_point, 1, l)
                if results:
                    current_point = results[0][1]  # 更新为最近的点
        
        # 从新点的最高层开始，逐层向下插入并建立连接
        for l in range(min(level, current_max_level), -1, -1):
            # 在当前层搜索ef_construction个最近邻
            results = self._search_layer(point, current_point, self.ef_construction, l)
            
            # 选择前M个最近邻作为连接
            neighbors = [idx for _, idx in results[:self.M]]
            
            # 在新点的当前层创建连接
            self.layers[l][point_id] = neighbors.copy()
            
            # 双向连接：邻居也连接到新点
            for neighbor in neighbors:
                if len(self.layers[l][neighbor]) < self.M:
                    # 邻居连接数未满，直接添加
                    self.layers[l][neighbor].append(point_id)
                else:
                    # 如果邻居连接数已满，替换最远的连接
                    neighbor_neighbors = self.layers[l][neighbor]
                    distances = [self._euclidean_distance(self.data_points[neighbor], 
                                                         self.data_points[n]) for n in neighbor_neighbors]
                    max_idx = np.argmax(distances)  # 找到最远的邻居
                    # 如果新点更近，则替换最远的邻居
                    if self._euclidean_distance(self.data_points[neighbor], point) < distances[max_idx]:
                        neighbor_neighbors[max_idx] = point_id
            
            # 更新当前点用于下一层的搜索
            if results:
                current_point = results[0][1]
        
        # 如果新点的层级比当前入口点高，更新入口点
        if level > self.entry_level:
            self.entry_point = point_id
            self.entry_level = level
    
    def search(
            self, query: np.ndarray, k: int=5, ef_search: int=50
        ) -> list[tuple[int, np.float64]]:
        """
        在HNSW中搜索最近邻
        
        参数:
        - query: 查询向量
        - k: 返回的最近邻数量
        - ef_search: 搜索时的候选集大小（越大精度越高但速度越慢）
        
        返回:
        - 包含(节点ID, 距离)的列表，按距离升序排列
        """
        if self.entry_point is None:
            return []
        
        current_point = self.entry_point
        current_level = self.entry_level
        
        # 从顶层开始搜索
        for l in range(current_level, 0, -1):
            results = self._search_layer(query, current_point, 1, l)
            if results:
                current_point = results[0][1]  # 更新为每层的入口点
        
        # 在最底层进行精细搜索
        results = self._search_layer(query, current_point, ef_search, 0)
        
        # 返回前k个结果
        return [(idx, dist) for dist, idx in results[:k]]

if __name__ == "__main__":
    # --- 1. 数据生成 ---

    def generate_sample_data(n_samples: int=200, dim: int=2):
        """生成示例数据：四个分离的高斯分布簇"""
        # 创建四个簇
        cluster1 = np.random.normal(loc=[2, 2], scale=0.3, size=(n_samples//4, dim))
        cluster2 = np.random.normal(loc=[8, 3], scale=0.4, size=(n_samples//4, dim))  
        cluster3 = np.random.normal(loc=[5, 8], scale=0.35, size=(n_samples//4, dim))
        cluster4 = np.random.normal(loc=[3, 6], scale=0.4, size=(n_samples - 3*(n_samples//4), dim))
        
        data = np.vstack([cluster1, cluster2, cluster3, cluster4])
        return data

    # --- 3. 性能演示 ---

    def demonstrate_hnsw_performance():
        """演示HNSW性能对比"""
        import time
        print("=" * 60)
        print("HNSW算法性能演示")
        print("=" * 60)
        
        # 生成测试数据
        data = generate_sample_data(500, 2)
        print(f"生成{len(data)}个二维数据点")
        
        # 创建HNSW索引
        hnsw = SimpleHNSW(max_elements=1000, M=9, ef_construction=50, max_layers=5)
        
        # 批量添加数据
        print("构建HNSW索引...")
        start_time = time.time()
        for i, point in enumerate(data):
            hnsw.add_point(point)
            if (i + 1) % 100 == 0:
                print(f"已添加{i + 1}个点")
        
        construction_time = time.time() - start_time
        print(f"HNSW索引构建完成，耗时: {construction_time:.4f}秒")
        
        # 选择查询点
        query_point = np.array([5.0, 5.0])
        print(f"\n查询点: {query_point}")
        
        # 使用HNSW搜索
        start_time = time.time()
        # hnsw_results, search_path = hnsw.search_with_path(query_point, k=5, ef_search=30)
        hnsw_results = hnsw.search(query_point, k=5, ef_search=30)
        hnsw_time = time.time() - start_time
        
        # 暴力搜索作为基准
        start_time = time.time()
        distances = euclidean_distances(query_point.reshape(1, -1), data)[0]
        bf_indices = np.argsort(distances)[:5]
        bf_distances = distances[bf_indices]
        bf_time = time.time() - start_time
        
        # 显示结果对比
        print(f"\n搜索结果对比:")
        print(f"HNSW搜索 - 找到{len(hnsw_results)}个最近邻, 耗时: {hnsw_time:.6f}秒")
        print(f"暴力搜索 - 找到{len(bf_indices)}个最近邻, 耗时: {bf_time:.6f}秒")
        
        print(f"\n速度提升: {bf_time/hnsw_time:.2f}倍")
        
        print(f"\nHNSW结果索引: {[idx for idx, _ in hnsw_results]}")
        print(f"HNSW结果距离: {[dist for _, dist in hnsw_results]}")
        print(f"暴力搜索结果索引: {bf_indices}")
        print(f"暴力搜索结果距离: {bf_distances}")
        
        # 检查召回率
        hnsw_indices_set = set(idx for idx, _ in hnsw_results)
        bf_indices_set = set(bf_indices)
        intersection = hnsw_indices_set & bf_indices_set
        recall = len(intersection) / len(bf_indices_set)
        print(f"召回率: {recall:.2%} ({len(intersection)}/{len(bf_indices_set)})")
        
        return hnsw, data, query_point, hnsw_results, bf_indices, None

    # 1. 运行标准演示
    np.random.seed(42)
    hnsw, data, query, hnsw_results, bf_results, search_path = demonstrate_hnsw_performance()

```

> 在 `np.random.seed(41)` 下要让 `M=34`刚好100%，小于34都是0。而在`np.random.seed(42)` 下 `M`大于8即可实现100%。水平之差，令人汗颜！（Yau语）好多地方都用42，42真的是一个幸运种子吗？

> 在这种随时要求数组有序的场景下，可以使用堆排序来优化。（回想起做算法题的时光）

```python
============================================================
HNSW算法性能演示
============================================================
生成500个二维数据点
构建HNSW索引...
已添加100个点
已添加200个点
已添加300个点
已添加400个点
已添加500个点
HNSW索引构建完成，耗时: 0.5738秒

查询点: [5. 5.]

搜索结果对比:
HNSW搜索 - 找到5个最近邻, 耗时: 0.000388秒
暴力搜索 - 找到5个最近邻, 耗时: 0.000408秒

速度提升: 1.05倍

HNSW结果索引: [440, 381, 411, 472, 418]
HNSW结果距离: [np.float64(1.2645024960453435), np.float64(1.3700870317527636), np.float64(1.3777320706338358), np.float64(1.3849682052776706), np.float64(1.5048714197321411)]
暴力搜索结果索引: [440 381 411 472 418]
暴力搜索结果距离: [1.2645025  1.37008703 1.37773207 1.38496821 1.50487142]
召回率: 100.00% (5/5)
```

但是当我改用标准库的 `heapq` 后，速度反而大幅降低：

```python
    def _search_layer(self, query, entry_point, ef, layer):
        """
        在指定层搜索最近邻
        
        参数:
        - query: 查询向量
        - entry_point: 搜索起始点
        - ef: 搜索范围（返回的候选点数量）
        - layer: 搜索的层级
        """
        if entry_point is None or entry_point not in self.layers[layer]:
            return []
            
        visited = set([entry_point])
        # 候选集：存储(距离, 节点ID)元组，从入口点开始
        candidates = []
        heapq.heappush(candidates, (self._euclidean_distance(query, self.data_points[entry_point]), entry_point))
        # 使用堆来维护候选集（这里简化为列表排序）
        results = []
        
        while candidates and len(results) < ef:
            # 获取距离最近的候选点
            current_dist, current_point = heapq.heappop(candidates)
            
            # 检查是否应该将当前点加入结果
            if not results or current_dist < results[-1][0]:
                heapq.heappush(results, (current_dist, current_point))
            
            # 探索当前点的所有邻居节点
            for neighbor in self.layers[layer][current_point]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    dist = self._euclidean_distance(query, self.data_points[neighbor])
                    heapq.heappush(candidates, (dist, neighbor))

        return heapq.nsmallest(ef, results, key=lambda x: x[0])
    
```

有人知道是怎么回事吗？我记得我做算法题的时候这个heapq效果也不佳，列表内置的 `sort` 方法已经优化完了……

```python
============================================================
HNSW算法性能演示
============================================================
生成500个二维数据点
构建HNSW索引...
已添加100个点
已添加200个点
已添加300个点
已添加400个点
已添加500个点
HNSW索引构建完成，耗时: 0.6132秒

查询点: [5. 5.]

搜索结果对比:
HNSW搜索 - 找到5个最近邻, 耗时: 0.001595秒
暴力搜索 - 找到5个最近邻, 耗时: 0.000447秒

速度提升: 0.28倍

HNSW结果索引: [440, 381, 411, 472, 418]
HNSW结果距离: [np.float64(1.2645024960453435), np.float64(1.3700870317527636), np.float64(1.3777320706338358), np.float64(1.3849682052776706), np.float64(1.5048714197321411)]
暴力搜索结果索引: [440 381 411 472 418]
暴力搜索结果距离: [1.2645025  1.37008703 1.37773207 1.38496821 1.50487142]
召回率: 100.00% (5/5)
```

> 原因概括（简短）：
>
> - heapq 的 push/pop 是逐次操作，每次都是 O(log n) 的开销；而 list.sort 是一次性在 C 层执行的 timsort，处理大量元素时通常比在 Python 循环里反复维护堆更快。
> - 你现在在循环里频繁对 results 做 push/heap 操作（甚至循环内排序），导致大量 Python 层的开销，因而比一次性收集然后 sort 要慢。
> - heapq 合适的场景是需要流式、逐次取最小/最大值或维护固定大小 top-k；若能先收集再排序，list.sort 通常更快。

## LSH算法

LSH 算法原理（Locality-Sensitive Hashin）是这些算法里面最简单的。我们高中学过解析几何，都知道对于直线
$$l:Ax+By+C=0$$

一个点$(x_{0},y_{0})$带进去$Ax_{0}+By_{0}+C$的符号决定了这个点是在直线的“上方”还是“下方”。总之符号相同的点在同一侧。推广到高维空间也如此。因此这就诞生了一种聚类算法，即两个向量的余弦相似度很高，那么大概率会被超平面划分到同一侧。为了提升准确性，这样的平面越多越可靠。

### 第一步：构建随机超平面

- 在$d$维度空间生成 `hash_size` 个向量：

$$
\begin{pmatrix}
\mathbf{r_{1}} \\ \mathbf{r_{2}}
 \\ \dots
 \\ \mathbf{r_{k}}
\end{pmatrix}
$$

- 每个向量的分量服从标准正态分布

    $N(0,1)$
- 每个超平面代表一个随机方向。

> 既然随机方向，为什么不是$[-1,1]$之间随机数就行了呢？为什么还要符合正态分布？

### 第二步：计算哈希签名

对于向量$\mathbf{x}$，通过计算

$$
h_i(\mathbf{x}) = \begin{cases}
 1, & \text{ if } \mathbf{r_{i}} \cdot \mathbf{x} \ge 0 \\
 0, & \text{ otherwise }
\end{cases}
$$

将每个超平面的点积结果拼接成一个字符串：
$\overline{h_{1}(\mathbf{x})h_{2}(\mathbf{x})\dots h_{k}(\mathbf{x})}$

这就是该向量的 **哈希签名**。两个角度相似的向量，更可能被超平面划分到相同侧，因此哈希签名相似。

$$
\begin{bmatrix}
 h_{1}(\mathbf{x}) & h_{2}(\mathbf{x}) & \dots & h_{k}(\mathbf{x})
\end{bmatrix}
=
\mathbf{x} \cdot
\begin{bmatrix}
\mathbf{r_{1}} \\ \mathbf{r_{2}}
 \\ \dots
 \\ \mathbf{r_{k}}
\end{bmatrix}^{T}
$$

### 第三步：构建多个哈希表（Multi-Table Strategy）

- 为了减少碰撞错误（不同向量哈希相同），我们使用多组独立哈希函数。
- 假设有：
  - 每组 k 个哈希函数组成一个 **哈希表（hash table）**
  - 共 L 个这样的表。

每个样本被插入到 L 个不同表中，从而提升召回率。

### 第 4 步：查询（Query）

给定查询向量 ( q )：

1. 计算其在每个哈希表中的签名；
2. 找出所有桶中与其哈希相同的候选样本；
3. 对候选样本计算真实相似度（如余弦或欧式距离）；
4. 返回最相似的 Top-K。

### 小结

试验表明LSH的召回效果不是很好。

- hash_size（哈希大小）：

> 作用：决定每个哈希表的哈希码长度（位数） 影响：值越大，哈希桶划分越精细，相似度判断越准确，但每个桶内的向量可能越少

- num_tables（哈希表数量）：

> 作用：控制使用的独立哈希表数量 影响：值越大，找到真正近邻的概率越高，但内存消耗也会增加
