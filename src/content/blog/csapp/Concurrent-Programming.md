---
title: 并发编程
description: ""
pubDate: "Feb 11 2025"
categories:
    - tech
tags:
    - csapp
---

# 并发程序的典型问题
我在shell lab中使用信号机制的混乱程度让我印象深刻,并发程序确实容易有各种bug.
- 竞争:结果与系统进程调度有关.
- 死锁:对某些系统资源的锁定引发永远的等待.
	例如,主函数使用了`printf`函数,取得了stdout的锁定.这时候被一个信号打断了,信号处理函数又使用`printf`函数往stdout打印内容,stdout被占用就会一直等待.
- 活锁/饥饿/公平

# 并发服务器
我之前自学网络编程的时候,自己写过一个FTP并发服务器,所以现在对这些概念理解起来很容易hh.
创建并发服务器的方法:
- [[并发编程#基于进程|基于进程]]
	- 内核自动调度逻辑流
	- 每个逻辑流有私有地址空间
- 事件驱动
	- 程序手动管理逻辑流
	- 所有逻辑流共享地址空间
	- I/O复用
- 基于线程
	- 内核自动调度逻辑流
	- 每个逻辑流共享地址空间
	- 以上两种的结合

## 基于进程
我做的并发服务器就是这个方法,放几个图加深一下印象就行,不必赘述.
![](attachments/Pasted%20image%2020250211120225.png)
```c
/* echoserverp.c */

int main(int argc, char **argv) { 
	int listenfd, connfd; 
	socklen_t clientlen; 
	struct sockaddr_storage clientaddr; 
	Signal(SIGCHLD, sigchld_handler); 
	listenfd = Open_listenfd(argv[1]); 
	while (1) { 
		clientlen = sizeof(struct sockaddr_storage); 
		connfd = Accept(listenfd, (SA *) &clientaddr, &clientlen); 
		if (Fork() == 0) { 
			Close(listenfd); /* Child closes its listening socket */ 
			echo(connfd); /* Child services client */ 
			Close(connfd); /* Child closes connection with client */ 
			exit(0); /* Child exits */ 
		} 
		Close(connfd); /* Parent closes connected socket (important!) */ 
	} 
}

void sigchld_handler(int sig) { while (waitpid(-1, 0, WNOHANG) > 0) ; return; }
```
- 优点:简单
- 缺点:开销较大,子进程不共享变量

## 基于I/O多路复用的并发事件驱动服务器
见CS:APP 686
我看了一下书里的代码,基本思想就是维护一个客户端池(一个文件描述符表),然后用死循环调用`select`函数,能监视它们是否准备好读.
一旦发现`listen`准备好读,添加客户端池;一旦发现客户端套接字准备好读,处理该客户端套接字.

现代高性能Web服务器(nginx),都是基于I/O复用.优点是开销小;缺点是代码比较复杂.

## 基于线程
"线程是轻量级的进程"

进程 = 进程上下文 + 代码,数据,堆栈
![](attachments/Pasted%20image%2020250211165558.png)
进程 = 线程+ 代码,数据,堆,内核上下文
![](attachments/Pasted%20image%2020250211165754.png)
这只是视角的不同!
- 每个线程有自己的逻辑控制流
- 每个线程共享代码,数据,内核上下文
- 每个线程有自己的栈
- 每个线程有线程TID

```c
/* echoservert.c */
int main(int argc, char **argv) { 
	int listenfd, *connfdp; 
	socklen_t clientlen; 
	struct sockaddr_storage clientaddr; 
	pthread_t tid; 
	
	listenfd = Open_listenfd(argv[1]); 
	while (1) { 
		clientlen=sizeof(struct sockaddr_storage); 
		connfdp = Malloc(sizeof(int)); 
		*connfdp = Accept(listenfd, (SA *) &clientaddr, &clientlen); 
		Pthread_create(&tid, NULL, thread, connfdp);
	}
}
/* Thread routine */ 
void *thread(void *vargp) { 
	int connfd = *((int *)vargp); 
	Pthread_detach(pthread_self()); 
	Free(vargp); 
	echo(connfd); 
	Close(connfd); 
	return NULL; 
}
```
![](attachments/Pasted%20image%2020250211172356.png)

在使用线程时需要小心的是,由于线程共享变量,也不对自己的栈设置保护,一个线程向另一个线程传递局部变量(的指针)是危险的行为.正因如此,上面echo服务器才使用了`malloc`将变量放在堆里而不是栈里.



