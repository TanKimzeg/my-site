---
title: "异常控制流(信号和非局部跳转)"
description: ""
pubDate: "Feb 1 2025"
categories:
  - tech
tags:
  - csapp
  - os
---

控制流:处理器从开机到关机只做一件事:读取和执行一系列指令,这些指令就叫CPU的控制流.

# 异常控制流(ECF:Exceptional Control Flow)
ECF存在于计算机系统的所有层次
- 底层机制
	- 1. 异常:由系统状态改变引发,由硬件和操作系统软件共同实现.
- 高层机制
	- 2. 上下文切换
	- 3. 信号
	- 4. 非局部跳转

# 异常(Exception)
异常是将控制权交给操作系统内核,作为对某些事件的回应.
内核是操作系统始终驻留在内存中的部分.
事件如:除以0/算术溢出/页错误/IO请求完成/Ctrl+C.
![](attachments/Pasted%20image%2020250201175658.png)
## 异常表
每种异常事件都有一个异常码,当异常事件k发生时,硬件使用k作为异常表的索引,然后跳转到处理该异常的程序的地址处.
![](attachments/Pasted%20image%2020250201180030.png)
## 异步异常(中断)
由处理器外部设备引发.通过在处理器上设置引脚,向处理器通知这些状态的变化.发生中断后,处理器返回到下一条指令.
例如:
- 计时器中断
	系统有一个内置计时器,每隔几毫秒就中断一次.
	内核用这个机制再次取得对用户程序的控制权.
- I/O中断
	Ctrl+C/收到网络包/收到磁盘数据

## 同步异常
由以下三种引发:
- 陷阱(Traps)
	程序故意引发的.如系统调用.返回到下一条指令
- 错误(Faults)
	非故意但可能可以恢复.如页错误
- 终止(Aborts)
	非故意且不可恢复

### 系统调用
每一个x86-64系统调用都有一个独一无二的ID,如:

ID|名称|描述
---|---|---
0|read|read file
1|write|write file
2|open|open file
3|close|close file
4|stat|get info about file
57|fork|创建进程
59|execve|执行程序
60|_exit|终止进程
62|kill|向进程发送信号

调用 `open(filename, options)`:
```x86asm
00000000000e5d70 <__open>: 
... 
e5d79: b8 02 00 00 00        mov $0x2,%eax # open is syscall #2 
e5d7e: 0f 05                 syscall       # Return value in %rax 
e5d80: 48 3d 01 f0 ff ff     cmp $0xfffffffffffff001,%rax 
... 
e5dfa: c3                    retq
```
%rax包含调用ID;如果open出错,会返回负数的errno,执行对应的错误处理.
![](attachments/Pasted%20image%2020250201183604.png)
### 页错误
磁盘上的一个可执行文件可能很大,根据局部性原理,只有一部分加载到内存中,当执行涉及的内存区域没有被加载过来时就会发生页缺失异常.这时候需要去硬盘中把这部分内存加载进来.
![](attachments/Pasted%20image%2020250201184544.png)
### 无效内存引用
![](attachments/Pasted%20image%2020250201184825.png)
内核向用户进程发送SIGSEGV信号,用户进程segmentation fault 退出.

# 进程(Process)
进程是一个正在运行的程序的实例.
进程的两个关键抽象:
- 逻辑控制流
	每个进程似乎独占CPU:不用担心别的程序会修改寄存器,也无法分辨系统中有其他进程正在运行.
- 私有地址空间
	虚拟内存机制提供,每个进程似乎独占内存:都有内存空间,也不能看到其他进程正在使用的内存.
即使在单核系统上,这些进程实际上是在同一时间并发运行
(我的1vCPU服务器,top界面出现了2 running)
![](attachments/Pasted%20image%2020250201231945.png)
操作系统如何实现多进程调度?
1. 单核系统
	单核处理器 **并发(concurrently)** 处理多个进程
	当异常发生时,操作系统可以决定是否要运行另一个进程
	![](attachments/Pasted%20image%2020250201232845.png)
	进程切换时,将寄存器的值复制到内存中保存,然后调度到下一个待执行的进程
	![](attachments/Pasted%20image%2020250201232903.png)
	它将加载上次保存的寄存器的值,地址空间也将切换.
	**上下文切换(context switch)**就是寄存器和地址空间的切换.
2. 多核系统
	每个核处理一个进程,也会发生上下文切换.
	![](attachments/Pasted%20image%2020250201234209.png)
- 并发,顺序,并行
	 ![](attachments/Pasted%20image%2020250201235607.png)
	 **并发(concurrent)** : A&B,A&C;  **顺序(sequential)** : B&C
	 ![](attachments/Pasted%20image%2020250201235722.png)
	 A&B,A&C **并行(parallel)**
- 上下文切换
	每个进程都是一个逻辑控制流.内核管理进程,通过**上下文切换**,控制流从一个进程切换到另一个进程.
	![](attachments/Pasted%20image%2020250202000758.png)

# 进程控制(Process Control)
## 系统调用的错误处理
Linux系统层面函数一旦发生错误,经常返回-1,并且设置全局变量errno的值来指示原因.返回指针(句柄)的函数发生错误返回空指针.
为了安全,在调用系统函数时,必须检查返回值.例如,我们可以将`fork`函数包装成:
```c
void unix_error(char *msg){
	fprintf(stderr, "%s: %s\n", msg, strerror(errno));
	exit(0);
}
pid_t Fork(void){
	pid_t pid;
	if((pid = fork()) < 0)
		unix_error("Fork error");
	return pid;
}

pid = Fork();
pid_t getpid(void);     /*获取当前进程的PID */
pid_t getppid(void);    /* 获取父进程的PID */
```
## 创建/终止进程
进程处在以下三种状态之一:
1. 运行
	进程正在被执行,或者等待执行并且后面会被内核调度.
2. 停止
	暂停执行,并且在进一步通知之前不会调度.
3. 终止
	永久停止

终止一个进程的三种方式:
1. 收到一个信号,默认是终止进程
2. 从`main`函数正常返回
3. 调用了`exit`函数

### 创建进程:
父进程通过调用`fork`函数能创建一个子进程.子进程是父进程的副本.
`int fork(void)`函数在子进程返回0,在父进程返回子进程的PID.
子进程和父进程并行执行,无法保证哪一个先执行.
> 这部分编程,我已经在网络编程中接触过了

通过进程图(Process Graph)来理解fork:
对于复杂的进程,可以画出进程图来分析,例如:
```c
void fork4()
{
	printf("L0\n");
	if(fork() != 0){
		printf("L1\n");
		if(fork() != 0)
			printf("L2\n");
	}
	printf("Bye\n");
}
```
的进程图:
![](attachments/Pasted%20image%2020250202224500.png)
### 回收fork进程
僵尸进程:当程序终止后仍然占有系统资源
子进程不会自动回收,父进程可以使用`wait`或`waitpid`函数回收子进程,父进程得到子进程退出状态,内核删除僵尸子进程.

- **僵尸(Zombie)**进程的例子:
	1.  子进程退出了,父进程不退出
		```c
		void fork7() { 
			if (fork() == 0) { 
				/* Child */ 
				printf("Terminating Child, PID = %d\n", getpid());
				exit(0); 
			} else { 
				printf("Running Parent, PID = %d\n", getpid()); 
				while (1) ; 
				/* Infinite loop */ 
			} 
		}
		```
		kill父进程后,init进程回收子进程.
	2. 父进程退出了,子进程不退出
		在父进程终止后,子进程依然在活跃.kill子进程后,子进程才终止.
可以看到,如果父进程不管管子进程的话,是可能会导致一些问题的.
- `wait`函数:暂停父进程直到一个子进程终止
	```c
	int wait(int *child_status);
	/* 整数*child_status被设置为子进程退出状态码 */
	```
- `waitpid`函数:暂停当前进程直到特定进程终止

### 加载/运行程序
要在进程内运行不同的程序,使用名为 `exicve` 的函数:
```c
int execve(char *filename, char *argv[], char *envp[]);
```
通过调用 `execve` 函数,进程以全新程序替换当前运行的程序,将丢弃原程序,,堆栈/数据/代码都会被新程序替换只有PID保留.所以 `execve`永远不会返回,除非无法执行.
- 用例
	在子进程中执行
	```shell
	/bin/ls -lt /usr/include
	```
	参数为:
	![](attachments/Pasted%20image%2020250202235349.png)
	```c
	if((pid = Fork())==0){
		/* 子进程运行程序 */
		if(execve(myargv[0], myargv, environ) < 0){
			printf("%s: Command not found.\n", myargv[0]);
			exit(1);
		}	
	}
	```