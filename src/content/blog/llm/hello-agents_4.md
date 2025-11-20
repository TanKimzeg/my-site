---
title: 第四部分 综合案例进阶 | Hello-Agents
description: Hello-Agents第四部分 综合案例进阶。包含三个项目:智能旅行助手、自动化深度研究智能体、构建赛博小镇。
pubDate: 2025 11 16 
categories: 
  - tech
tags:
  - llm
  - agent
---

## 智能旅行助手

Python是强类型语言,却不要求在代码中写类型.这使得它具有贴近自然语言的风格,却限制了在工程上的进一步发挥.因此,我一直推荐养成在代码中加入类型注释的习惯.近年来随着Python工程项目的增多,越来越多项目都包含类型注释.有利于IDE的检查和自动补全.

Pydantic在此基础上提供了进一步的严格数据验证。Pydantic 的基础是`BaseModel`类，所有的数据模型都需要继承这个类。每个字段都可以指定类型，Pydantic 会自动进行类型检查和转换。

字段定义使用`Field`函数，它可以指定默认值、描述、验证规则等。`...`表示这个字段是必填的，如果创建对象时没有提供这个字段，Pydantic 会抛出异常。

还可以自定义验证器。

```python
from pydantic import BaseModel, field_validator

class WeatherInfo(BaseModel):
    temperature: int
    
    @field_validator('temperature',mode='before')
    def parse_temperature(cls,v):
        """解析温度字符串："16°C" -> 16"""
        if isinstance(v,str):
            v = v.replace('°C','').replace('℃','').strip()
            return int(v)
        return v
```

### 多智能体协作设计

旅行助手采用了多角色的设计。

- **AttractionSearchAgent(景点搜索专家)**专注于搜索景点信息。它只需要理解用户的偏好(比如"历史文化"、"自然风光")，然后调用高德地图的 POI 搜索工具，返回相关的景点列表。它的提示词很简单，只需要说明如何根据偏好选择关键词，如何调用工具。

- **WeatherQueryAgent(天气查询专家)**专注于查询天气信息。它只需要知道城市名称，然后调用天气查询工具，返回未来几天的天气预报。它的任务非常明确，几乎不会出错。

- **HotelAgent(酒店推荐专家)**专注于搜索酒店信息。它需要理解用户的住宿需求(比如"经济型"、"豪华型")，然后调用 POI 搜索工具，返回符合要求的酒店列表。

- **PlannerAgent(行程规划专家)**负责整合所有信息。它接收前三个 Agent 的输出，加上用户的原始需求(日期、预算等)，然后生成完整的旅行计划。它不需要调用任何外部工具，只需要专注于信息的整合和行程的安排。

为此给每一个智能体设计自己的提示词。

### 前后端分离

文档居然还详细介绍了前后端的核心代码，帮助我们完全了解此项目。如果是我的项目，我甚至不会用这么多文字去介绍前端的技术细节、组件和功能。

## 自动化深度研究智能体

## 构建赛博小镇
