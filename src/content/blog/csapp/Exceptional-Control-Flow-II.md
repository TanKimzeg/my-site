---
title: "异常控制流(信号和非局部跳转)"
description: ""
pubDate: "Feb 2 2025"
categories:
  - tech
tags:
  - csapp
  - os
---


# Linux进程层次结构
启动系统时创建的第一个进程时init进程,它的PID是1.系统上其他所有进程都是init进程的子进程.
init进程启动后会创建守护进程.然后是登录进程login shell.
![](attachments/Pasted%20image%2020250203150254.png)

# 信号(Signal)
信号是一条信息,通知进程系统中发生了某类事件.
信号是由内核发出的(其他进程可以请求内核发出信号)
信号携带的信息是一个整数ID(1~30).如:

ID|名称|默认行为|反映事件
---|---|---|---
2|SIGINT|终止|Ctrl+C
9|SIGKILL|终止|kill
11|SIGSEGV|终止并转储核心|Segmentation fault
14|SIGALRM|终止|计时器信号
17|SIGCHLD|忽略|子进程停止或终止

## 发送信号
内核发送信号的原因:
- 内核发现某些事件
- 另一个进程请求内核传递信号给另一个进程.

内核通过更新目标进程的**上下文**来实现发送信号的功能.
### 进程组(Process Group)
每一个进程属于某一个进程组.
![](attachments/Pasted%20image%2020250203160042.png)

`getpgrp()`: 获取当前进程的进程组.
`setpgid()`: 改变进程的进程组.
1. /bin/kill程序能够向进程和进程组发送信号:
	```shell
	kill -9 24818
	```
	(向24818进程发送ID 9:SIGKILL信号)
	```shell
	kill -9 -24817
	```
	(向进程组24817发送SIGKILL信号).
2. keyboard interrupt.
Ctrl+C:向前台进程组的所有进程发送SIGINT(终止)
Ctrl+Z:向前台进程组的所有进程发送SIGSTP(暂停)

## 接收信号
目标程序接到信号后,以某种方式对信号做出回应.
回应方式:
- 忽略信号
- 终止进程
- 捕获信号,然后执行响应的信号处理机制(有点像异常处理[[异常控制流(异常和进程)#异常表]])
	![](attachments/Pasted%20image%2020250203153948.png)

假设内核从异常处理中返回,准备将控制权交付给进程p
![](attachments/Pasted%20image%2020250203163848.png)
> 不要忘了,上下文切换是通过异常来处理的

内核先计算进程p待处理且未阻塞的信号:
`pnb = peding & ~blocked`
如果 `pnb==0` ,将控制权交付进程p.
如果 `pnb!=0` ,逐个处理非零位的信号,这将引发进程p的信号处理,直到所有非零位处理完成.
> [!understanding] 
> 我的理解是,这些信号是在p进程暂停时发来的,在重新运行p前内核要先处理掉这些待处理信号.

每个信号类型有对应的默认处理行为,为以下几种之一:
- 终止
- 终止并转储核心
- 停止直到SIGCONT继续执行
- 忽略

我们可以使用一个叫做`signal`的系统调用来修改默认行为:
```c
handler_t *signal(int signum, handler_t *handler);
```
参数handler的不同值:
- SIG_IGN: 忽略signum类型的信号.
- SIG_DFL: 执行signum类型信号的默认行为
- 指定的信号处理函数.程序收到signum类型信号后会执行对应的信号处理函数,该信号处理函数返回后程序回到之前的位置继续执行.

信号处理程序与主程序运行在同一个进程里,是主程序的并发流.
![](attachments/Pasted%20image%2020250203173014.png)
![](attachments/Pasted%20image%2020250203173057.png)
信号处理程序也可以被其他信号处理程序打断,但不能被同种信号打断:
![](attachments/Pasted%20image%2020250203173323.png)

## 待处理信号
**待处理(pending)**信号:已经由内核发出但还未收到.
任何时候,一种类型的待处理信号只能有一个,多余的忽略.

进程无法阻止信号的到来,但是可以**阻塞(blocked)**对信号的处理/响应.

对于每个进程,内核维护一个32位的**待处理/阻塞向量(pending and blocked bit vector)**.
- pending: 代表待处理信号的集合.
	当k信号传递时,设置第k位;当k信号接收时,清除第k位.(这也是一类待处理信号只有1个的原因)
- blocked: 代表阻塞信号的集合.
	通过`sigprocmask`函数设置或清除(signal mask).
	1. 隐式阻塞机制
		内核阻塞正被处理的信号作为待处理信号.例如:
		SIGINT处理函数不能被另一个SIGINT信号打断.
	2. 显示阻塞/解除阻塞
		`sigprocmask`函数以及配套的 `sigemptyset, sigfullset, sigaddset, sigdelset`.
		用例:
		```c
		sigset_t mask, prev_mask; 
		sigemptyset(&mask); 
		sigaddset(&mask, SIGINT); 
		
		/* Block SIGINT and save previous blocked set */
		sigprocmask(SIG_BLOCK, &mask, &prev_mask); 
		 {
			/* Code region that will not be interrupted by SIGINT */ 
		 }
		/* Restore previous blocked set, unblocking SIGINT */ 
		sigprocmask(SIG_SETMASK, &prev_mask, NULL);
		```
## 安全的信号处理函数
信号处理非常复杂,因为它是并发流,涉及并发编程的理解.我现在还不是很理解.
编写安全的信号处理函数的准则:
- G0: Keep your handlers as simple as possible
	- 如:Set a global flag and return
- Call only async-signal-safe func&ons in your handlers
	- printf, sprintf, malloc, and exit are not safe!
- Save and restore errno on entry and exit
	- So that other handlers don’t overwrite your value of errno
- Protect accesses to shared data structures by temporarily blocking all signals.
	- To prevent possible corrup;on
- Declare global variables as volatile
	- To prevent compiler from storing them in a register
- Declare global flags as volatile sig_atomic_t
	- flag: variable that is only read or wriien (e.g. flag = 1, not flag++)
	- Flag declared this way does not need to be protected like other globals

函数是**异步信号安全**的,如果它可重入或不能被其他信号打断.(使用 `man 7 signal`查看异步信号安全的函数).

这部分实在难以言说,只好在代码中体会.
父进程通过信号管理子进程的时候存在"竞争"的关系,也就是执行语句的原子性.如果处理信号的语句没有良好的原子性,在处理一半的时候信号传过来了,就会导致不一致的行为.
对比以下代码段:
```c
/* procmask1.c */
int main(int argc, char **argv) { 
	int pid; 
	sigset_t mask_all, prev_all; 
	Sigfillset(&mask_all); 
	Signal(SIGCHLD, handler); 
	initjobs(); /* Initialize the job list */ 
	
	while (1) { 
		if ((pid = Fork()) == 0) { /* Child */ 
			Execve("/bin/date", argv, NULL); 
		} 
		Sigprocmask(SIG_BLOCK, &mask_all, &prev_all); /* Parent */ 
		addjob(pid); /* Add the child to the job list */ 
		Sigprocmask(SIG_SETMASK, &prev_all, NULL); 
	} 
	exit(0); 
}

void handler(int sig) { 
	int olderrno = errno; 
	sigset_t mask_all, prev_all; 
	pid_t pid; 
	
	Sigfillset(&mask_all); 
	while ((pid = waitpid(-1, NULL, 0)) > 0) { /* Reap child */ 
		Sigprocmask(SIG_BLOCK, &mask_all, &prev_all); 
		deletejob(pid); /* Delete the child from the job list */ 
		Sigprocmask(SIG_SETMASK, &prev_all, NULL); 
	} 
	if (errno != ECHILD) Sio_error("waitpid error"); 
	errno = olderrno; 
}
```
问题在于子进程在父进程没来得及`addjob()`之前就结束了,`handler()`函数会删除列表中不存在的元素,然后父进程再把一个已经结束的进程加入工作列表.
所以对其修改如下:
```c
int main(int argc, char **argv) { 
	int pid; 
	sigset_t mask_all, mask_one, prev_one; 
	
	Sigfillset(&mask_all); Sigemptyset(&mask_one); 
	Sigaddset(&mask_one, SIGCHLD); 
	Signal(SIGCHLD, handler); 
	initjobs(); /* Initialize the job list */ 
	
	while (1) { 
	Sigprocmask(SIG_BLOCK, &mask_one, &prev_one); /* Block SIGCHLD */ 
		if ((pid = Fork()) == 0) { /* Child process */ 
			Sigprocmask(SIG_SETMASK, &prev_one, NULL); /* Unblock SIGCHLD */ 
			Execve("/bin/date", argv, NULL); 
		} 
	Sigprocmask(SIG_BLOCK, &mask_all, NULL); /* Parent process */ 
	addjob(pid); /* Add the child to the job list */ 
	Sigprocmask(SIG_SETMASK, &prev_one, NULL); /* Unblock SIGCHLD */ 
	} 
	exit(0); 
}
```
显式等待信号:
```c
int sigsuspend(const sigset_t *mask);
```
相当于有原子性的`pause()`函数.
```c
volatile sig_atomic_t pid; 

void sigchld_handler(int s) { 
	int olderrno = errno; 
	pid = Waitpid(-1, NULL, 0); /* Main is waiting for nonzero pid */ 
	errno = olderrno; 
} 

void sigint_handler(int s) { }

int main(int argc, char **argv) { 
	sigset_t mask, prev; 
	Signal(SIGCHLD, sigchld_handler); 
	Signal(SIGINT, sigint_handler); 
	Sigemptyset(&mask); 
	Sigaddset(&mask, SIGCHLD); 
	
	while (1) { 
		Sigprocmask(SIG_BLOCK, &mask, &prev); /* Block SIGCHLD */ 
		if (Fork() == 0) /* Child */
			 exit(0); 
			 
		/* Wait for SIGCHLD to be received */ 
		pid = 0; 
		while (!pid) 
			Sigsuspend(&prev); 
			
		/* Optionally unblock SIGCHLD */ 
		Sigprocmask(SIG_SETMASK, &prev, NULL); 
		/* Do some work after receiving SIGCHLD */ 
		printf("."); 
	} 
	exit(0); 
}
```
`sigsuspend(&prev)`函数在执行的时候,会在内部原子性地解除信号阻塞,然后是`pause()`函数,最后重新加上信号阻塞.

# C非本地跳转:setjmp/longjmp
从深层嵌套中立即返回
```c
int setjmp(jum_buf j);
void longjmp(jmp_buf j, int i);
```
`setjmp`在jmp_buf中存储当前位置的栈指针记住当前位置,返回0.
`longjmp`返回到`setjmp`的位置,`setjmp`返回i.
```c
/* Deeply nested function foo */ 
void foo(void) { 
	if (error1) longjmp(buf, 1); 
	bar(); 
} 

void bar(void) { 
	if (error2) longjmp(buf, 2); 
}

jmp_buf buf; 
int error1 = 0; 
int error2 = 1; 

void foo(void), bar(void); 

int main() { 
	switch(setjmp(buf)) { 
	case 0: foo(); break; 
	case 1: printf("Detected an error1 condition in foo\n"); break; 
	case 2: printf("Detected an error2 condition in foo\n"); break; 
	default: printf("Unknown error condition in foo\n"); 
	} 
	exit(0); 
}
```

> 太晦涩了,不易深究...
