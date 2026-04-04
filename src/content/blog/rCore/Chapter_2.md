---
title: "第二章：批处理系统"
description: "本章讲解如何实现批处理系统 (Batch System)。"
pubDate: 2026 03 10 15:10
categories: 
  - tech
tags:
  - os
  - rust
---

## 引言

**批处理系统** (Batch System) 应运而生，它可用来管理无需或仅需少量用户交互即可运行的程序。批处理系统的核心思想是：将多个程序打包到一起输入计算机。而当一个程序运行结束后，计算机会 _自动_ 加载下一个程序到内存并开始执行。

我们希望一个应用程序的错误不要影响到其它应用程序、操作系统和整个计算机系统。这就需要操作系统能够终止出错的应用程序，转而运行下一个应用程序。这种 _保护_ 计算机系统不受有意或无意出错的程序破坏的机制被称为 **特权级** (Privilege) 机制，它让应用程序运行在用户态，而操作系统运行在内核态，且实现用户态和内核态的隔离。

![批处理系统整体架构](https://rcore-os.cn/rCore-Tutorial-Book-v3/_images/batch-os-detail.png)

Qemu把包含多个app的列表和BatchOS的image镜像加载到内存中，RustSBI（bootloader）完成基本的硬件初始化后，跳转到BatchOS起始位置，BatchOS首先进行正常运行前的初始化工作，即建立栈空间和清零bss段，然后通过 AppManager 内核模块从app列表中依次加载各个app到指定的内存中在用户态执行。app在执行过程中，会通过系统调用的方式得到BatchOS提供的OS服务，如输出字符串等。

## 特权级机制

上一章的Hello, world! 程序是由内核发出来的，严格来说不是应用程序，应用程序也不应该跟内核一起执行。现在为确保操作系统的安全，对应用程序而言，需要限制的主要有两个方面：

- 应用程序不能访问任意的地址空间（这个在第四章会进一步讲解，本章不会涉及）
    
- 应用程序不能执行某些可能破坏计算机系统的指令（本章的重点）

高特权级软件（操作系统）就成为低特权级软件（一般应用）的软件执行环境的重要组成部分。

`ecall` 这条指令和 `eret` 这类指令分别可以用来让 CPU 从当前特权级切换到比当前高一级的特权级和切换到不高于当前的特权级。

RISC-V 架构中一共定义了 4 种特权级：

|级别|编码|名称|
|---|---|---|
|0|00|用户/应用模式 (U, User/Application)|
|1|01|监督模式 (S, Supervisor)|
|2|10|虚拟监督模式 (H, Hypervisor)|
|3|11|机器模式 (M, Machine)|

![执行环境栈](https://rcore-os.cn/rCore-Tutorial-Book-v3/_images/PrivilegeStack.png)

其中 **断点** (Breakpoint) 和 **执行环境调用** (Environment call) 两种异常是通过在上层软件中执行一条特定的指令触发的：执行 `ebreak` 这条指令之后就会触发断点陷入异常；而执行 `ecall` 这条指令时候则会随着 CPU 当前所处特权级而触发不同的异常。从表中可以看出，当 CPU 分别处于 M/S/U 三种特权级时执行 `ecall` 这条指令会触发三种异常。

![](https://rcore-os.cn/rCore-Tutorial-Book-v3/_images/EnvironmentCallFlow.png)

与特权级无关的一般的指令和通用寄存器 `x0` ~ `x31` 在任何特权级都可以执行。而每个特权级都对应一些特殊指令和 **控制状态寄存器** (CSR, Control and Status Register)。

在 RISC-V 中，会有两类属于高特权级 S 模式的特权指令：

- 指令本身属于高特权级的指令，如 `sret` 指令（表示从 S 模式返回到 U 模式）。
    
- 指令访问了 [S模式特权级下才能访问的寄存器](https://rcore-os.cn/rCore-Tutorial-Book-v3/chapter2/4trap-handling.html#term-s-mod-csr) 或内存，如表示S模式系统状态的 **控制状态寄存器** `sstatus` 等。

## 实现应用程序


