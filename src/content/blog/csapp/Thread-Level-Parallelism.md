---
title: 线程级并行
description: ""
pubDate: "2025-2-12"
categories:
    - tech
tags:
    - csapp
---

# 并行计算硬件
经典的多核处理器:
![](attachments/Pasted%20image%2020250214094826.png)

乱序处理器结构:
![](attachments/Pasted%20image%2020250214095029.png)
超线程的基本思想是,90%的程序没有完全利用这些功能单元.特别是因为缓存缺失而造成阻塞时,所有这些算术单元都处于空闲状态.
将寄存器,操作指令队列,程序计数器等翻倍,这样就能让多个线程运行起来,但共享功能单元.
![](attachments/Pasted%20image%2020250214095608.png)

# 线程级并行
## 将程序分割成多个独立的任务
- 例1:并行求和
	$\sum_{i=0}^{n-1}i=0+1+2+\dots+()n-1)$
	分割成t部分,每个部分范围$\lfloor n / t \rfloor$
	```c
	/* Thread routine for psum-array.c */ 
	void *sum_array(void *vargp) { 
		long myid = *((long *)vargp); /* Extract thread ID */ 
		long start = myid * nelems_per_thread; /* Start element index */ 
		long end = start + nelems_per_thread; /* End element index */ 
		long i; 
		for (i = start; i < end; i++) { psum[myid] += i; } 
		return NULL; 
	}
	```
	为了充分利用寄存器,例程应使用局部变量:
	```c
	/* Thread routine for psum-local.c */ 
	void *sum_local(void *vargp) { 
		long myid = *((long *)vargp); /* Extract thread ID */ 
		long start = myid * nelems_per_thread; /* Start element index */ 
		long end = start + nelems_per_thread; /* End element index */ 
		long i, sum = 0; 
		for (i = start; i < end; i++) { sum += i; } 
		psum[myid] = sum; 
		return NULL; 
	}
	```

对$n=2^{31}$规模的任务,两者的运行时间如下:
![](attachments/Pasted%20image%2020250214102140.png)

对于p核处理器,$T_{k}$是使用k核的运行时间
定义:
- 加速比:$S_{p}=T_{1} / T_{p}$
- 效率比:$E_{p} = S_{p} / p = T_{1} / (p T_{p})$

# 教训
- 采取并行策略:分治
- 在循环内部不要写同步语句,这样会导致运行很慢
- 阿姆达尔定律:如果总是提升某一部分的性能,那么其他部分会称为瓶颈.

# 内存一致性的硬件保障
对每个缓存块标记状态:
- Invalid: Cannot use value
- Shared: Readable copy
- Exclusive: Writeable copy
![](attachments/Pasted%20image%2020250214115924.png)

