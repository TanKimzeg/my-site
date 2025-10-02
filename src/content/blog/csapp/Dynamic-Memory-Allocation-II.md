---
title: 程序优化(进阶概念)
description: ""
pubDate: "Feb 7 2025"
categories:
    - tech
tags:
    - csapp
---

(续)
## 显式空闲块列表
这是一个空闲块的列表,而非隐式列表那样的所有块的列表.
![](attachments/Pasted%20image%2020250207181225.png)
Next和Prev都是指向空闲块的指针.
仍然需要脚标来合并.
![](attachments/Pasted%20image%2020250207184658.png)
### 分配块
![](attachments/Pasted%20image%2020250207184810.png)

### 释放块
插入策略:新释放的块插入到链表的什么位置?
- 插入链表第一个节点LIFO:简单省事,但碎片化比按地址排序严重
- 按地址排序:addr(prev) < addr(curr) < addr(next)
	需要搜索

#### LIFO
	
![](attachments/Pasted%20image%2020250207171729.png)
1. Case 1
	![](attachments/Pasted%20image%2020250207233408.png)

2. Case 2
	![](attachments/Pasted%20image%2020250207233454.png)

3. Case 3
	![](attachments/Pasted%20image%2020250207233645.png)

4. Case 4
	![](attachments/Pasted%20image%2020250207233712.png)
	

### 总结
现在,分配时间是空闲块数量呈线性相关关系而不是堆的大小.
合并 操作比较复杂,也需要额外的开销.
不足以高效的通用于现实分配器.
维护多种大小的空闲列表,每个列表都是一个显式列表.

## 隔离空闲块列表
每类尺寸的块大小都有自己的空闲列表
![](attachments/Pasted%20image%2020250208000254.png)
### 分配大小为n的块
- 搜寻合适大小的块列表m>n
- 如果找到合适的块,分割并放置碎片到合适的列表里(可选)
- 如果找不到,尝试更大块类
- 如果最后找不到,向操作系统请求增加堆(调用`sbrk()`)

### 释放块:
合并,放到合适的列表中

### 优点
高吞吐量,高内存利用率


# 垃圾回收机制
自动回收堆分配的空间,应用不用调用`free`函数.
内存管理器如何知道内存何时可以被释放?
将内存视为有向图
不在堆中但包含指向堆的指针叫做根节点(寄存器/栈/全局变量).
指针是图的边,块是图的节点.
![](attachments/Pasted%20image%2020250208002600.png)
如果存在从根节点到节点的路径,该节点就是可达的.
不可达的节点是垃圾.
## 标记清扫收集(Mark and Sweep Collection)
当空间耗尽后:
在每个块的头部设置额外的标记位:从根节点开始,标记每一个可达块.再次扫描所有块,将不可达的块释放.
![](attachments/Pasted%20image%2020250208003722.png)

# 内存相关的危险
把变量当成指针,读取未初始化数据,覆写内存,悬空指针多次释放指针内存泄漏
## 处理内存Bug
- 调试器:GDB
- 数据结构一致性检查器
	静默运行,出错时打印错误
- valgrid:二分检查
- `setenv MALLOC_CHECK_ 3`
