---
title: String类源码阅读 | Java
description: "java.lang.String类的源码分析"
pubDate: 2025 10 15
categories:
  - tech
tags:
  - java
---

众所周知, 现代字符串是非常复杂的数据结构, 涉及内存布局, 编码格式, 不可变性等多个方面. Java的String类是Java编程语言中用于表示字符串的核心类, 位于`java.lang`包中. 它提供了丰富的方法来操作字符串, 同时在设计上也考虑了性能和内存效率.

## String简介

String类表示不可变的字符序列. 一旦创建, String对象的内容就不能被修改. 这种不可变性带来了线程安全和性能优化的好处, 因为多个引用可以共享同一个String实例而不必担心数据被意外修改.

## 内部表示

String内部实现了序列化,可比较等方法.包含字符数组,哈希值等字段.

```java
private final char value[];
private int hash; // Cached hash code
```

## 构造方法

几种初始化方法,将字符串的value复制过来(怎么感觉在套娃).对于参数是char[]和切片的构造方法,hash未初始化.

BMP(基本多文种平面)字符使用单个char表示,而补充字符使用一对char(代理项)表示.所以Java的String在内部使用UTF-16编码.

## 比较方法

1. `equals` 系列方法

2. `compareTo`: 比较两个字符串的字典顺序

3. 比较器 `CaseInsensitiveComparator`

## 查找方法

1. `startsWith`

2. `endsWith`: 调用 `startsWith` 方法实现

3. `indexOf` 和 `lastIndexOf`: 查找子字符串或字符在字符串中的位置, 支持从指定索引开始查找.查找不到返回 -1.
4. `contains`: 判断字符串是否包含指定的字符序列, 底层调用 `indexOf`

## 字符串哈希

$$ hash(s) = s[0] \times 31^{n-1} + s[1] \times 31^{n-2} + \ldots + s[n-1] \times 31^{0} $$

`hashCode` 方法计算字符串的哈希值, 并缓存结果以提高性能. 31是一个常用的素数, 选择它是因为乘法可以通过位移和减法来优化.

```java
public int hashCode() {
    int h = hash;
    if (h == 0 && value.length > 0) {
        char val[] = value;

        for (int i = 0; i < value.length; i++) {
            h = 31 * h + val[i];
        }
        hash = h;
    }
    return h;
}
```

## 总结

大量的字符串操作方法, 以及对不可变性的设计, 使得Java的String类既强大又高效. 理解其内部实现有助于更好地使用字符串, 并在性能敏感的场景中做出更明智的选择.

Java的char类型使用UTF-16编码, 这意味着它可以表示从U+0000到U+FFFF的字符(基本多文种平面, BMP), 以及通过代理项对表示从U+10000到U+10FFFF的补充字符. 这使得Java能够支持全球范围内的多种语言和符号.
