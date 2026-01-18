---
title: 第五章·FAISS工程化落地实战 | EasyVectoDB
description: 本节聚焦FAISS在实际业务中的工程化应用。
pubDate: 2026 01 17 
categories: 
  - tech
tags:
  - rag
image: /llm/blog-article-rag.png
---

## 文本语义检索实战

文本语义检索是FAISS最典型的应用场景，核心是将非结构化文本转化为结构化向量后，通过相似性搜索实现"语义匹配"而非传统关键词匹配。

1. 数据准备：将Markdown文本切分，提取元数据metadata信息
2. 向量生成：使用 `langchain`的封装借助嵌入模型生成所有段落的嵌入向量
3. 检索库构建：通过FAISS创建索引并保存
4. 结果排序优化：在查询阶段加入结果排序优化模块
5. 接口编写：利用现代的FastAPI库快速开发Web接口
6. 前端页面：通过Vibe Coding生成简洁的前端页面
7. 系统测试：系统可正常运行，返回相关结果。

实现了一个博客文章智慧搜索功能，项目开源在[https://github.com/TanKimzeg/blog-articles-rag](https://github.com/TanKimzeg/blog-articles-rag)。

经过本轮EasyVectorDB的学习，我增强了对FAISS的理解，在之前的 all-in-rag 项目的基础上，重构了代码，实现了对Markdown格式博客文章的语义检索（智慧搜索）。嵌入向量接入FAISS构建检索库，嵌入模型使用 `BAAI/bge-small-zh-v1.5`。后端使用FastAPI开发Web接口。同时编写一系列测试，保持现代的Python代码风格。
本次重构使用了 `pydantic-settings` 的 `BaseSettings` 基类，功能很强大：[Pydantic-Settings](https://docs.pydantic.org.cn/latest/concepts/pydantic_settings)，这是增强Python代码健壮性的优雅实践。

由于使用了`langchain`的封装，没有指定聚类算法，好像默认使用的INFFlat索引？后续可以尝试不同的索引结构，评估性能。

网页效果：

![blog-article-rag](/llm/blog-article-rag.png)

## 图像相似性检索实战

图像检索除了相似性，还有多模态的发展方向。本章提供的代码仅仅是图搜图。

在本章的研究领域，可以构建一个论坛图片相似检索系统，支持输入一张论坛图片图像，返回数据库中视觉特征最相似的论坛图片信息。

1. **数据准备**：收集不同类别的论坛图片图像；
2. **特征提取**：使用ResNet50模型提取所有论坛图片图像的特征向量，确保向量归一化；
3. **检索库构建**：训练FAISS IndexIVFFlat索引并保存，元数据包含论坛图片类别、价格（模拟）、图像路径；
4. **交互功能开发**：基于Streamlit开发简单前端界面，支持图像上传与检索结果展示；
5. **系统优化**：测试不同nprobe值对检索精度和速度的影响，确定最优参数。

## 工程化部署

由于我的数据量不大，我没有开发索引增量接口，每次部署都是从头构建索引。这是以后将本系统接入博客网站时需要改进的地方。

### 索引增量更新

小规模增量：直接添加向量。
适用于每次新增向量数量较少（万级以内）的场景，直接在原有索引上添加新向量，无需重新训练。
