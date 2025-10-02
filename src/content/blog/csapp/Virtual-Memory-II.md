---
title: "虚拟内存(系统)"
description: ""
pubDate: "Feb 6 2025"
categories:
  - tech
tags:
  - csapp
  - os
---

# Intel x86-64 i7/Linux内存系统
i7处理器架构:
![](attachments/Pasted%20image%2020250206172220.png)
## 符号:
- 基本量
	- $N=2^m$:虚拟地址空间
	- $M=2^m$:物理地址空间
	- $P=2^p$:页大小(字节)
- 虚拟地址(VA)组成
	- TLBI:TLB索引
	- TLBT:TLB tag
	- VPO:虚拟页偏移量
	- VPN:虚拟页码
- 物理地址(PA)组成
	- PPO:物理地址偏移量(等于VPO)
	- PPN:物理页码
	- CO:缓存行中的偏移量
	- CI:缓存索引
	- CT:缓存tag

## 地址翻译
下图把整个地址翻译过程描述得非常清晰:
![](attachments/Pasted%20image%2020250206173424.png)

## 第1~3级PTE
![](attachments/Pasted%20image%2020250206174113.png)
- P: Child page table present in physical memory (1) or not (0).
- R/W: Read-only or read-write access access permission for all reachable pages.
- U/S: user or supervisor (kernel) mode access permission for all reachable pages.
- WT: Write-through or write-back cache policy for the child page table
- A: Reference bit (set by MMU on reads and writes, cleared by socware).
- PS: Page size either 4 KB or 4 MB (defined for Level 1 PTEs only).
- Page table physical base address: 40 most significant bits of physical page table address (forces page tables to be 4KB aligned)
- XD: Disable or enable instruc;on fetches from all pages reachable from this PTE.
## 第4级PTE
![](attachments/Pasted%20image%2020250206175028.png)
不再是下一级的页表基址,而是页的物理地址.
第6位和第7位有变化:
- D: Dirty bit (set by MMU on writes, cleared by socware)

## 页表翻译
![](attachments/Pasted%20image%2020250206175410.png)
已经多次呈现.

## 加速L1内存访问
![](attachments/Pasted%20image%2020250206182631.png)
由于VPO和PPO是一样的,在进行地址翻译的同时,把VPO发送给L1缓存,就可以先对tag位进行筛选,筛选的结果与地址翻译的结果结合,从而加速了缓存查找.

## Linux进程的虚拟地址空间
![](attachments/Pasted%20image%2020250206183123.png)
> [!think]
> 为什么要有kernel virtual memory?这块不是很懂.

Linux系统将虚拟内存组织成一块一块的区域:
![](attachments/Pasted%20image%2020250206184609.png)

三种异常:
![](attachments/Pasted%20image%2020250206184855.png)
1. Segmentation fault:访问不存在的页,不在vm_start和vm_end区间内.
2. Prtection exception:违反了权限(Linux报Segmentation fault).
3. 正常的页错误.

# 内存映射
虚拟内存的区域初始化的时候,和磁盘上的对象关联起来,这个过程叫做内存映射.
初始化的内容来自那个文件,将其复制到内存.文件可以是:
- 磁盘上的常规文件.如可执行文件.
	初始化的页的数据就是其中的section
- 匿名文件,包含的全是0
	第一次引用这个页时(first fault),创建一个全为0的页(demand-zero page).
	一旦这个页被写入后,就和其他页一样.
	写入的页被复制到内核维护的专门的交换文件(swap file).
## 共享对象(Share Object)
利用内存映射可以实现进程间共享对象,因为进程可以映射虚拟内存的区域到同一个对象.
![](attachments/Pasted%20image%2020250207100746.png)
因为这个共享对象有一个唯一的名字,所以内核可以检查有没有其他进程映射到那个对象.如果有,那么内核就把虚拟地址倒影的区域映射到相同的物理地址.

## 私有写时复制对象(Private Copy-on-write Object)
这个区域的页表标记为私有写时复制.PTE的私有区域被标记为只读.向私有页写的指令会触发protection fault.异常处理将创建一个新的R/W页,然后在这个新的页上写.
![](attachments/Pasted%20image%2020250207102141.png)

## `fork`函数
以上私有COW技术提供了高效的`fork`思路.
进行`fork`时,内核只复制所有的内核数据结构:`mm_struct`, `vm_arear_struct`以及页表.
然后内核把两个进程中的每个页都标记为只读,把每一个`vm_area_struct`标记为私有写时复制(COW).
当`fork`函数返回时,每个进程都有相同的地址空间.两个进程读的时候,它们会共享这些区域;当进程要写时,会根据写时复制机制,创建一个新页.

## `execve`函数
删除当前进程的所有`vm_arear_struct`和页表.为新区域创建新的`vm_area_struct`和页表.然后初始化.
![](attachments/Pasted%20image%2020250207112009.png)
最后把程序计数器%rip设置为代码区域的入口.
一切仅仅是做了映射,修改内核中的数据结构.直到访问时遇到页错误才加载到内存中.

## 用户级内存映射
```c
void *mmap(void *start, int len, int prot, int flags, int fd, int offset);
```
![](attachments/Pasted%20image%2020250207112924.png)
将虚拟地址start映射到文件描述符fd偏移量offset起len字节的数据.
prot指定保护类型:PROT_READ,PROT_WRITE...
flag指定文件对象类型:MAP_ANON(匿名文件),MAP_PRIVATE,MAP_SHARED...
返回指向映射区域的指针(如果start被占用,有操作系统选择)
### 用例:复制文件无需`read`
```c
void mmapcopy(int fd, int size){
	/* Ptr to memory mapped area */
	char *buf;
	if(!(buf = mmap(NULL, size, PRO_READ, MAP_PRIVATE, fd,0)))
		unix_error("mmap error");
	if(write(1, buf, size)<0)    /* stdout: 1 */
		unix_erro("write error");
	return;
}

int amin(int argc, char **argv){
	struct stat stat; 
	int fd; 
	
	/* Check for required cmd line arg */ 
	if (argc != 2) { printf("usage: %s \n", argv[0]); exit(0); } 
	
	/* Copy input file to stdout */ 
	if((fd = open(argv[1], O_RDONLY, 0)) < 0) unix_error("open error");
	if(fstat(fd, &stat) < 0) unix_error("fstart error"); 
	mmapcopy(fd, stat.st_size); 
	exit(0);
}
```