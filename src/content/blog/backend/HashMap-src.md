---
title: HashMap源码阅读 | Java
description: "java.util.HashMap类的源码分析"
pubDate: 2025 10 16
categories:
  - tech
tags:
  - java
---

## HashMap简介

HashMap是Java中用于存储键值对的哈希表实现,位于`java.util`包中.它允许通过键快速访问对应的值,并提供了高效的插入、删除和查找操作.HashMap类实现了Map接口,并提供了丰富的方法来操作键值对.HashMap允许键和值为null,并且不保证映射的顺序.文档中指出, HashMap跟HashTable相当,但区别是它是非同步的,允许null键和值,并且性能更好.

哈希表是一种重要的数据结构,网络上也有很多分析,一起来看看它的实现吧!

[HashMap源码分析](https://javaguide.cn/java/collection/hashmap-source-code.html)

## 内部表示

HashMap由数组和链表(或红黑树)组成,即"拉链法".当链表长度大于等于阈值,且当前数组容量大于等于64时,会将链表转换为红黑树,以提高查找效率.HashMap默认的初始化大小是16,负载因子是0.75.之后每次扩充2倍,保持2的幂.

![内部形态](/backend/hashmap-internal.png)

### hash函数

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

将高16位和低16位进行异或,目的应该是为了避免比较差的`hashCode`方法导致的碰撞,减少哈希冲突.

### 普通节点

```java
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    V value;
    Node<K,V> next;

    Node(int hash, K key, V value, Node<K,V> next) {
        this.hash = hash;
        this.key = key;
        this.value = value;
        this.next = next;
    }
    // ...
}
```

### 树节点

```java
static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
    TreeNode<K,V> parent;  // red-black tree links
    TreeNode<K,V> left;
    TreeNode<K,V> right;
    TreeNode<K,V> prev;    // needed to unlink next upon deletion
    boolean red;
    ...
}
```

红黑树是及其复杂的数据结构,我以前看过[动画演示](https://www.bilibili.com/video/BV1piF6erE7Y/),但实现代码十分麻烦...

### tableSizeFor

在jdk-1.8中

```java
static final int tableSizeFor(int cap) {
    int n = cap - 1;
    n |= n >>> 1;
    n |= n >>> 2;
    n |= n >>> 4;
    n |= n >>> 8;
    n |= n >>> 16;
    return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
}
```

而在jdk-25中,已经变成了:

```java
static final int tableSizeFor(int cap) {
    int n = -1 >>> Integer.numberOfLeadingZeros(cap - 1);
    return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
}
```

这个函数的目的是将给定的容量`cap`调整为大于等于`cap`的最小2的幂次方.多看看这种位运算的技巧,有利于活跃思维~~预防老年痴呆~~.

## 公共接口

### `get` 方法

调用内部 `getNode` 方法.通过 `hash(key)` 来快速索引:

```java
first = table[(n - 1) & hash];
```

由于n是2的幂次方,所以`(n - 1)`的二进制表示全是1,相当于取模运算. `[hash % n]`.

找到根节点后,如果是树节点,则调用 `getTreeNode` 方法去查找;否则遍历链表查找.

`containsKey` 方法也是类似的过程.

### `put` 方法

通过内部 `putVal` 方法实现.首先计算hash值,然后定位到对应的桶位置.如果该位置为空,则直接插入新的节点.如果不存在则覆盖.

转换为树的过程`treeifyBin`发生在尾部插入的时候.最后如果当前元素个数超过阈值,则调用 `resize` 方法进行扩容.

### `resize` 方法

功能是初始化或扩充2倍大小.令我称妙的是,由于原大小是2的幂次方,所以扩容后,每个旧桶的位置要么保持不变,要么移动到原位置加上旧容量的位置.

扩充后原一条链变成两条(红黑树调用`split` 方法,同理).通过检查每个节点的hash值与旧容量的与运算结果,决定节点去向.这个过程称为rehash.

Java是有垃圾回收机制的,所以不需要手动释放旧引用节点,只需简单地将旧引用设为null即可.

### 迭代器

HashMap通过内部类实现了多种迭代器,包括键迭代器、值迭代器和条目迭代器.这些迭代器都继承自 `HashMapIterator` 抽象类,该类实现了基本的迭代逻辑,如遍历桶数组和链表/树节点.利用这些迭代器进一步实现了 `keySet()`、`values()` 和 `entrySet()` 方法,分别返回键集合、值集合和条目集合的**视图**.对这些视图的修改会反映到原始的HashMap中.

## 总结

HashMap是Java中非常重要且常用的数据结构,其高效的哈希表实现使得键值对的存储和访问变得快捷.通过数组和链表/红黑树的结合,HashMap能够在大多数情况下提供接近常数时间的复杂度.理解HashMap的内部工作原理有助于我们更好地利用它来解决实际问题.
