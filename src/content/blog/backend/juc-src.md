---
title: JUC源码阅读 | Java
description: "java.util.concurrent包的源码分析"
pubDate: 2025 10 22
categories:
  - tech
tags:
  - java
---

## 引言: 什么是JUC?

JUC，全称为Java Util Concurrent，是Java标准库中的一个重要包，提供了一系列用于并发编程的工具和类。它包含了线程池、并发集合、锁机制等，极大地简化了多线程编程的复杂性。

## 前置知识: Unsafe类简介

在深入JUC源码之前，了解`Unsafe`类是非常重要的。`Unsafe`类提供了一些底层操作的能力，如直接内存访问、原子操作等。虽然它并不是Java标准API的一部分，但JUC中的许多类都依赖于它来实现高效的并发控制。

`sun.misc.Unsafe`类提供了一系列的C++操作:

- **内存操作**: 直接分配和释放内存，绕过Java堆。
- **原子操作**: 提供了原子性的读写操作，如`compareAndSwap`。
- **线程调度**: 提供了线程挂起和恢复的低级操作。

`Unsafe`类的声明都是本地方法,依赖于外部的C++代码实现。[native方法在java中介绍及使用图解](https://blog.csdn.net/weixin_43629719/article/details/88823090).

## JUC中的核心组件

概述: [Java并发编程之concurrent包](https://zhuanlan.zhihu.com/p/412635774)

### `AbstractQueuedSynchronizer` (AQS)

我本来是直接生啃AQS的源码的,但是看不明白具体细节的目的.没办法,只好去找资料学习了一下.
[AQS详解](https://javaguide.cn/java/concurrent/aqs.html)讲得很好,推荐阅读.

### `atomic`包

`java.util.concurrent.atomic`包提供了一组原子变量类，如`AtomicInteger`、`AtomicLong`等。这些类利用了`Unsafe`类的原子操作方法，实现了高效的无锁并发编程。我们以简单的`AtomicInteger`为例，来看一下它的实现原理。

```java
public class AtomicInteger extends Number implements java.io.Serializable {
    private static final long serialVersionUID = 6214790243416807050L;

    private static final Unsafe unsafe = Unsafe.getUnsafe();
    private static final long valueOffset;

    static {
        try {
            valueOffset = unsafe.objectFieldOffset
                (AtomicInteger.class.getDeclaredField("value"));
        } catch (Exception ex) { throw new Error(ex); }
    }

    private volatile int value;

    public final int get() {
        return value;
    }

    public final void set(int newValue) {
        value = newValue;
    }

    public final boolean compareAndSet(int expect, int update) {
        return unsafe.compareAndSwapInt(this, valueOffset, expect, update);
    }
}
```

其实依赖`Unsafe`类的`compareAndSwapInt`方法,就实现了原子性的更新操作.

### `Condition`接口

`Condition`接口是JUC中用于**线程间通信**的一个重要组件。它类似于传统的`Object`类中的`wait()`和`notify()`方法，但提供了更灵活和强大的功能。通过`Condition`，线程可以等待特定的条件被满足，然后再继续执行。

很多锁实现类（如`ReentrantLock`）都提供了`Condition`的实现: `newCondition()`方法.

常用方法:

- `await()`: 使当前线程等待，直到被唤醒。
- `signal()`: 唤醒一个等待的线程。
- `signalAll()`: 唤醒所有等待的线程。

### `ReentrantLock`(可重入锁)

`ReentrantLock`是对 AQS 的独占模式(Exclusive)的一个具体实现.
可重入的意思是: 同一个线程可以多次获取锁而不会导致死锁。

### `Semaphore`(信号量)

`Semaphore` 是对 AQS 的共享模式(Shared)的一个具体实现.
信号量用于控制对某个资源的访问数量,可以用来实现限流.

### `CountDownLatch`(倒计时锁)

`CountDownLatch` 也是对 AQS 的共享模式(Shared)的一个具体实现.
倒计时锁允许一个或多个线程等待其他线程完成操作后再继续执行.
