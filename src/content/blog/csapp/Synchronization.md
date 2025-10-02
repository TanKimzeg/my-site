---
title: 同步
description: ""
pubDate: "2025-2-11"
categories:
    - tech
tags:
    - csapp
---


# 线程内存模型
- 概念模型
	- 多个线程在单个进程的上下文中运行.
	- 每个线程都有自己独立的线程上下文:线程ID,栈,栈指针,程序计数器,条件码,寄存器值
	- 所有线程共享剩余的进程上下文,进程上下文由内核维护.
- 实际上,线程是共享的,不设保护,一个线程的栈能访问另一个线程的栈.

## 变量内存映射
- 全局变量:任何全局变量,虚拟内存只包含一个示例
- 局部变量:每个线程的栈包含局部变量的一个示例
- 局部静态变量:任何局部静态变量,虚拟内存只包含一个示例,只供该函数使用

# 同步(Synchronization)线程
```c
/* badcnt.c */
/* Global shared variable */ 
volatile long cnt = 0; /* Counter */ 
int main(int argc, char **argv) { 
	long niters; 
	pthread_t tid1, tid2; 
	niters = atoi(argv[1]); 
	Pthread_create(&tid1, NULL, thread, &niters); 
	Pthread_create(&tid2, NULL, thread, &niters); 
	Pthread_join(tid1, NULL); 
	Pthread_join(tid2, NULL); 
	
	/* Check result */ 
	if (cnt != (2 * niters)) 
		printf("BOOM! cnt=%ld\n", cnt); 
	else printf("OK cnt=%ld\n", cnt); 
		exit(0); 
}

/* Thread routine */ 
void *thread(void *vargp) { 
	long i, niters = *((long *)vargp); 
	for (i = 0; i < niters; i++) cnt++; 
	return NULL; 
}
```
这个程序会发生同步错误.
`voatile`是保证编译器将变量从内存存取的关键字.
导致了cnt变量自增操作的非原子性.
分析竞争时,甚至需要从汇编层面观察:
```x86asm
	movq (%rdi), %rcx 
	testq %rcx,%rcx 
	jle .L2 
	movl $0, %eax            H:Head
.L3: 
	movq cnt(%rip),%rdx      L:Load cnt
	addq $1, %rdx            U:Update cnt
	movq %rdx, cnt(%rip)     S:Store cnt
	addq $1, %rax 
	cmpq %rcx, %rax 
	jne .L3                  T:Tail
.L2:
```
L,U,S是三个关键操作,却没有保证原子性,那么,当线程被调度打断后,就会出现不一致的情况.这一点我在数据库课程中也见识过了.
## 进度图
在并行线程中,一条线段是一个原子事务.
通过过程图来分析上述过程:
![](attachments/Pasted%20image%2020250211222712.png)
堆全局变量cnt进行操作的临界区不应该被交错,两个临界区交错的区域称为不安全区.
真实一目了然!这样解释很有意思!

## 信号量(Semaphore)
使用信号量是一个基础的解决办法.
信号量:非负全局整数同步变量.由两个内核函数P和V操作.
- P(s)
	- 如果s非零,那么s减1并立即返回
		- 检测和减小操作是原子性的
	- 如果s是0,那么挂起线程直到s变成非零由V函数重启.
	- 重启后,P减小s并将控制权返回给调用者
- V(s)
	- 将s增加1(增加操作是原子性的)
	- 如果有线程阻塞在P操作上,重启其中一个线程,然后P操作可以减小s
利用这个非负的属性,可以实现对临界区的互斥访问.
```c
#include <semaphore.h>
int sem_init(sem_t *s, 0, unsigned int val);} /* s = val */ 
int sem_wait(sem_t *s); /* P(s) */ 
int sem_post(sem_t *s); /* V(s) */
```
## 互斥锁
- 基本思想:
	- 将一个信号量*mutex*初始化为1,共享变量
	- 将临界区用*P(mutex)*和*V(mutex)*包裹起来,实现了"加锁"的操作.
- 术语:
	- 二进制信号量:总是为0或1
	- mutex:用于**互斥(mutual exclusion)**的二进制信号量
		- P操作:加锁
		- V操作:解锁或释放
		- 持有互斥锁:互斥锁以加锁但未释放
	- 计数信号量(Counting semaphore):计数器

修改循环的代码:
```c
for (i = 0; i < niters; i++) { 
	P(&mutex); 
	cnt++; 
	V(&mutex); 
}
```
现在,过程图变成这样:
![](attachments/Pasted%20image%2020250211233255.png)

## 协调对共享资源的访问
- 基本思想
	- 使用信号量通知其他线程
	- 使用计数信号量追踪资源的状态
- 两个经典例子:
	- 生产者-消费者问题
	- 读写问题

### 生产者-消费者问题
![](attachments/Pasted%20image%2020250212182944.png)
生产者等待空位,向缓冲区放入物品,然后通知消费者
消费者等待物品,从缓冲区移除物品,然后通知生产者
需要锁和两个计数信号量:
- mutex:向缓冲区加互斥锁
- slots:空位数
- items:物品数
数据结构:
```c
#include "csapp.h"
typedef struct { 
	int *buf; /* Buffer array */ 
	int n; /* Maximum number of slots */ 
	int front; /* buf[(front+1)%n] is first item */ 
	int rear; /* buf[rear%n] is last item */ 
	sem_t mutex; /* Protects accesses to buf */ 
	sem_t slots; /* Counts available slots */ 
	sem_t items; /* Counts available items */ 
} sbuf_t; 

void sbuf_init(sbuf_t *sp, int n); 
void sbuf_deinit(sbuf_t *sp); 
void sbuf_insert(sbuf_t *sp, int item); 
int sbuf_remove(sbuf_t *sp);

/* Create an empty, bounded, shared FIFO buffer with n slots */ 
void sbuf_init(sbuf_t *sp, int n) { 
	sp->buf = Calloc(n, sizeof(int)); 
	sp->n = n; /* Buffer holds max of n items */ 
	sp->front = sp->rear = 0; /* Empty buffer iff front == rear */ 
	Sem_init(&sp->mutex, 0, 1); /* Binary semaphore for locking */ 
	Sem_init(&sp->slots, 0, n); /* Initially, buf has n empty slots */ 
	Sem_init(&sp->items, 0, 0); /* Initially, buf has 0 items */ 
} 

/* Clean up buffer sp */ 
void sbuf_deinit(sbuf_t *sp) { Free(sp->buf); }
/* Insert item onto the rear of shared buffer sp */ 
void sbuf_insert(sbuf_t *sp, int item) { 
	P(&sp->slots); /* Wait for available slot */ 
	P(&sp->mutex); /* Lock the buffer */ 
	sp->buf[(++sp->rear)%(sp->n)] = item; /* Insert the item */ 
	V(&sp->mutex); /* Unlock the buffer */ 
	V(&sp->items); /* Announce available item */ 
}
/* Remove and return the first item from buffer sp */ 
int sbuf_remove(sbuf_t *sp) { 
	int item; P(&sp->items); /* Wait for available item */ 
	P(&sp->mutex); /* Lock the buffer */ 
	item = sp->buf[(++sp->front)%(sp->n)]; /* Remove the item */ 
	V(&sp->mutex); /* Unlock the buffer */ 
	V(&sp->slots); /* Announce available slot */ 
	return item; 
}
```
### 读写问题
- 读取线程只读文件
- 写线程修改文件
- 写线程必须对文件有互斥锁
- 读取线程不限量

多样的读写问题:
1. 第一类读写问题(有利于读)
	读方不应该等待,除非写方已经取得使用权
	读操作就算比写操作后来,也具有更高优先级
1. 第二类读写问题(有利于写)
	一旦写操作就绪,尽快实行
	读操作就算比写操作先来,也要等写操作
3. 两种策略都有发生饥饿的风险

第一类读写问题:
- Writers:
	```c
	void writer(void) { 
		while (1) { 
			P(&w); 
			
			/* Critical section */ 
			/* Writing happens */ 
			
			V(&w); 
		} 
	}
	```
- Readers:
	```c
	int readcnt; /* Initially = 0 */ 
	sem_t mutex, w; /* Initially = 1 */ 
	void reader(void) { 
		while (1) { 
			P(&mutex); 
			readcnt++; 
			if (readcnt == 1) /* First in */ 
				P(&w); 
			V(&mutex); 
			
			/* Critical section */ 
			/* Reading happens */ 
			
			P(&mutex); 
			readcnt--; 
			if (readcnt == 0) /* Last out */ 
				V(&w); 
			V(&mutex); 
		} 
	}
	```

### 线程池并发服务器
![](attachments/Pasted%20image%2020250212200018.png)
之前的服务器不断地创建销毁线程,造成了性能的浪费.不如提前准备好一个线程池,有任务时从线程池取出线程进行处理.
在这个模型中,主线程提供的客户端请求相当于生产者,线程池相当于消费者.
代码还是很精妙的:
```c
sbuf_t sbuf; /* Shared buffer of connected descriptors */ 
int main(int argc, char **argv) { 
	int i, listenfd, connfd; 
	socklen_t clientlen; 
	struct sockaddr_storage clientaddr; 
	pthread_t tid; 
	
	listenfd = Open_listenfd(argv[1]); 
	sbuf_init(&sbuf, SBUFSIZE); 
	for (i = 0; i < NTHREADS; i++) /* Create worker threads */ 
		Pthread_create(&tid, NULL, thread, NULL); 
	while (1) { 
		clientlen = sizeof(struct sockaddr_storage); 
		connfd = Accept(listenfd, (SA *) &clientaddr, &clientlen); 
		sbuf_insert(&sbuf, connfd); /* Insert connfd in buffer */ 
	} 
}
void *thread(void *vargp) { 
	Pthread_detach(pthread_self()); 
	while (1) { 
		int connfd = sbuf_remove(&sbuf); /* Remove connfd from buf */ 
		echo_cnt(connfd); /* Service client */ 
		Close(connfd); 
	} 
}

static int byte_cnt; /* Byte counter */ 
static sem_t mutex; /* and the mutex that protects it */ 
static void init_echo_cnt(void) { Sem_init(&mutex, 0, 1); byte_cnt = 0; }

void echo_cnt(int connfd) { 
	int n; char buf[MAXLINE]; 
	rio_t rio; 
	static pthread_once_t once = PTHREAD_ONCE_INIT; 
	
	Pthread_once(&once, init_echo_cnt);  // 只有第一个运行到这里的线程会执行
	Rio_readinitb(&rio, connfd); 
	while((n = Rio_readlineb(&rio, buf, MAXLINE)) != 0) { 
		P(&mutex); 
		byte_cnt += n; 
		printf("thread %d received %d (%d total) bytes on fd %d\n", (int) pthread_self(), n, byte_cnt, connfd); 
		V(&mutex); 
		Rio_writen(connfd, buf, n); 
	} 
}
```

# 线程安全
如果一个函数能够被多个并发线程调用而不影响正确结果的是线程安全的函数.
线程只应使用线程安全的函数.
四种线程不安全的函数:
1. 不保护共享变量的函数
2. 在多次调用中追踪状态的函数
	将状态存储在某个全局变量,私有或公共全局变量中.多个线程将访问该状态.
3. 返回指向同一个位置(静态变量)的指针的函数
	每一次调用的结果都被覆写
	```c
	/* lock-and-copy version */ 
	char *ctime_ts(const time_t *timep, char *privatep) { 
		char *sharedp; 
		
		P(&mutex); 
		sharedp = ctime(timep); 
		strcpy(privatep, sharedp); 
		V(&mutex); 
		return privatep; 
	}
	```
4. 任何调用线程不安全函数的函数🤣
## 可重入函数
可重入函数是线程安全函数的一个子类.
如果函数不访问共享变量,就是可重入函数.
使第二类线程不安全函数变安全唯一办法是让它变成可重入函数.共享变量作为参数传入.

## 死锁
如果一个进程等待一个永远不会成立的条件,就进入了死锁.
进程1取得A的锁,等待B解锁
这时候进程1 被打断,调度到进程2
进程2取得B的锁,等待A解锁
```c
int main() { 
	pthread_t tid[2]; 
	Sem_init(&mutex[0], 0, 1); /* mutex[0] = 1 */ 
	Sem_init(&mutex[1], 0, 1); /* mutex[1] = 1 */ 
	Pthread_create(&tid[0], NULL, count, (void*) 0); 
	Pthread_create(&tid[1], NULL, count, (void*) 1); 
	Pthread_join(tid[0], NULL); 
	Pthread_join(tid[1], NULL); 
	printf("cnt=%d\n", cnt); exit(0); 
} 

void *count(void *vargp) { 
	int i; 
	int id = (int) vargp; 
	for (i = 0; i < NITERS; i++) { 
		P(&mutex[id]); P(&mutex[1-id]); 
		cnt++; 
		V(&mutex[id]); V(&mutex[1-id]); 
	} 
	return NULL; 
}
```

Tid[0] | Tid[1]
---|---
P(s0)|P(s1)
P(s1)|P(s0)
cnt++|cnt++
V(s0)|V(s1)
V(s1)|V(s0)

进度图:
![](attachments/Pasted%20image%2020250212205837.png)
如果以一个固定的顺序取得资源的锁就可以解决这个问题:

Tid[0] | Tid[1]
---|---
P(s0)|P(s0)
P(s1)|P(s1)
cnt++|cnt++
V(s0)|V(s1)
V(s1)|V(s0)

![](attachments/Pasted%20image%2020250212210221.png)

