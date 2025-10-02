---
title: 链接
description: ""
pubDate: "2025-01-31"
categories:
    - tech
tags:
    - csapp
---


# 链接过程
```c
/* main.c */
int sum(int *a, int n);
int array[2] = {1,2};
int main(){
	int val = sum(array, 2);
	return val;
}
```
```c
/* sum.c */
int sum(int *a, int n){
	int i, s = 0;
	for(i=0;i<n;i++){
		s += a[i];	
	}
	return s;
}
```
静态链接
```shell
gcc -Og -o prog main.c sum.c
```
![](attachments/Pasted%20image%2020250201110702.png)

# 使用链接器的原因
1. 模块化
2. 高效
- 时间:修改一部分源文件无需重新编译其他源文件
- 空间:提升复用性(库函数)

# 连接器的行为
1. 符号解析(Symbol Resolution)
- 程序定义和引用符号(函数和全局变量)
- 汇编器将符号定义存储在目标文件的符号表中
	- 符号表是结构体数组,每个成员包含名称,大小,位置等信息
- 符号解析过程中,连接器将每个符号引用跟符号定义关联起来.
	- 三类链接器符号
		1. 全局符号
		模块中能够被其他模块使用的符号,如非static的函数和全局变量
		2. 外部符号
		由其他模块定义的全局符号
		3. 局部符号
		在模块中定义且只能在该模块中使用的符号,如static函数和变量
		- 局部非静态变量存储在堆栈上
		- 局部静态变量存储在.data或.bss中
		```c
		int f(){
			static int x=2;
			return x;
		}
		int g(){
			static int x=1;
			return x;
		}
		int h(){
			int x=5;
			return x;
		}
		```
		虽然 `f()`和 `g()`函数的静态变量都叫x,但编译器用别名(x.1,x.2)会加以区分.
		
	- 强符号和弱符号
		- 强符号:函数定义和已初始化的全局变量
		- 弱符号:未初始化的全局变量
	- 符号规则
		1. 不允许多个同名的强符号
		1. 同名的一个强符号和多个弱符号,选择强符号
			引用弱符号将被解析到强符号的定义处
			```c
			int x=5;
			int y=7;
			void p1(){}
			```
			```c
			double x;
			void p2(){}
			```
			在p2中使用x,会改变y的值!
		1. 多个同名的弱符号,任意选择一个
			使用
			```shell
			gcc -fno-common
			```
			杜绝这种行为.
		
	- 建议
		- 减少使用全局变量
		- 定义时初始化
		- 使用 `static`和 `extern`加以限制

2. 重定向(Relocation)
把分离的代码和数据合并在可执行文件的一个板块内.
![](attachments/Pasted%20image%2020250201141301.png)
在重定向前,编译器生成的目标文件的函数和数据的地址只是它在模块中的偏移量,链接器决定当程序执行时它们存储在哪里,将地址和符号绑定起来.
![](attachments/Pasted%20image%2020250201141713.png)
===========================>>>>>>>>>>>>>>>>>>>>>>
![](attachments/Pasted%20image%2020250201141819.png)


# 三类目标文件
1. 可重定位目标文件( \*.o)
汇编器的输出;可以和其他.o文件由连接器合并为可执行目标文件.

2. 可执行目标文件(a.out)
连接器输出的可执行文件

3. 共享目标文件(\*.so)
动态链接库(dll),运行时加载.

# 可执行可链接格式(ELF)
以上三种目标文件的标准统一格式
![](attachments/Pasted%20image%2020250201113741.png)
1. ELF header
定义了字长,字节序,文件类型,机器类型
2. 段头部表
3. .text
代码
4. .rodata 
只读数据,如跳转表
5. .data
有初始化的全局变量
6. .bss 
未初始化的全局变量
7. .symtab
包含程序全局变量的结构体数组;stactic变量
8. .rel.text
需要在可执行目标文件中重定位的指令
9. .rel.data
需要在可执行目标文件中重定位的数据
10. .debug
`gcc -g`
包含了源代码的行号与机器代码的行号相关联的信息
11. 节头部表
每个section的偏移量和大小.
## 加载可执行目标文件
![](attachments/Pasted%20image%2020250201142208.png)

# 库:打包常用函数
通过静态链接常用函数的源文件,有两种实现方式:
- 将所有常用函数写在一个源文件中,这会导致生成的目标文件冗余
- 将每个函数写在单独的源文件中,这会导致链接命令非常长
为了解决这个问题,引入了链接库的技术.
## 静态链接库(.a文件)
- 原理
	- 链接多个.o文件成一个文档
	- 当连接器遇到未解析的外部引用时,去文档中寻找该符号
	- 如果能找到,将其链接进可执行目标文件
- 创建静态库
	![](attachments/Pasted%20image%2020250201144113.png)
- 使用静态库
	+ 链接器解析外部引用的算法:
		+ 按照命令行顺序扫描.o和.a文件
		+ 扫描过程中,维护一个未解析引用列表
		+ 每次遇到一个新的.o或.a文件,尝试在其中解析未解析引用
		+ 如果到了末尾还有未解析引用,就报linker error
	所以,命令行参数的顺序就十分重要:
	```shell
	gcc -L . libtest.o -lmine
	```
	是正确的写法,而
	```shell
	gcc -L . -lmine libtest.o
	```
	会发生 `undefined reference`.
 	> `-L [dir]` 指定所用到库文件所在目录


## 动态链接库/共享库(.so文件)
- 静态库的缺点:
	- 可执行文件中冗余存储库函数
	- 运行时内存冗余存储库函数
	- 库发生更改,程序需要重新链接
- 共享库:目标文件包含在程序运行时加载的代码和数据.
- 动态链接发生在可执行文件第一次加载或运行时
- 也可以发生在开始运行后(`dlopen()`函数)
	分布式软件/高性能web服务器/库打桩
	```c
	#include <stdio.h>
	#include <stdlib.h>
	#include <dlfcn.h>
	
	int x[2] = {1, 2}; 
	int y[2] = {3, 4}; 
	int z[2]; 
	int main() { 
		void *handle; 
		void (*addvec)(int *, int *, int *, int); 
		char *error; 
		
		/* Dynamically load the shared library that contains addvec() */ 
		handle = dlopen("./libvector.so", RTLD_LAZY); 
		if (!handle) { 
			fprintf(stderr, "%s\n", dlerror()); 
			exit(1); 
		}
		
		/* Get a pointer to the addvec() function we just loaded */ 
		addvec = dlsym(handle, "addvec"); 
		if ((error = dlerror()) != NULL) { 
			fprintf(stderr, "%s\n", error); 
			exit(1); 
		} 
		
		/* Now we can call addvec() just like any other function */ 
		addvec(x, y, z, 2); 
		printf("z = [%d %d]\n", z[0], z[1]);
		 
		/* Unload the shared library */ 
		if (dlclose(handle) < 0) { 
			fprintf(stderr, "%s\n", dlerror()); 
			exit(1); 
		} 
		return 0;
	}
	```
- 共享库可以被多个进程共同使用
加载时的动态链接:
![](attachments/Pasted%20image%2020250201160053.png)

# 库打桩技术
截获对库函数的调用,取而代之执行自己的代码.使用库打桩技术,可以追踪对某个库函数的调用次数,输入和输出值,甚至替换为不同的函数实现.
## 应用举例
```c
/* int.c */
#include <stdio.h>
#include <malloc.h>
int main() { 
	int *p = malloc(32); 
	free(p); 
	return(0); 
}
```
我希望使用库打桩技术,在不修改源代码的前提下,追踪分配的地址和大小信息.
有三种实现方式,分别在编译时,链接时和运行时.

- 编译时
	编写 `mymalloc.c`:
	```c
	#ifdef COMPILETIME
	#include <stdio.h>
	#include <malloc.h>

	/* malloc wrapper func */
	void *mymalloc(size_t size){
		void *ptr = malloc(size);
		... // 追踪指针信息
		return ptr;	
	}

	/* free wrapper func */
	void myfree(void *ptr){
		free(ptr);
		... // 追踪指针信息
	}
	#endif
	```
	编写头文件 `malloc.h`:
	```c
	#define malloc(size) mymalloc(size)
	#define free(size) free(size)

	void *mymalloc(size_t size);
	void myfree(void *ptr);
	```
	GCC构建:
	```shell
	$ make
	gcc -Wall -DCOMPILETIME -c mymalloc.c 
	gcc -Wall -I. -o intc int.c mymalloc.o

	$ ./intc
	...输出地址和大小信息
	```
	> `-I [dir]` 参数添加头文件的路径
	> `-D[define]` 参数预定义宏
	
- 链接时
	编写 `mymalloc.c`文件:
	```c
	#ifdef LINKTIME 
	#include <stdio.h>
	void *__real_malloc(size_t size); 
	void __real_free(void *ptr); 
	
	/* malloc wrapper function */ 
	void *__wrap_malloc(size_t size) { 
		void *ptr = __real_malloc(size); /* Call libc malloc */ 
		printf("malloc(%d) = %p\n", (int)size, ptr); 
		return ptr; 
	} 
	
	/* free wrapper function */ 
	void __wrap_free(void *ptr) { 
		__real_free(ptr); /* Call libc free */ 
		printf("free(%p)\n", ptr); 
	} 
	#endif	
	```
	gcc构建:
	```shell
	linux> make intl 
	gcc -Wall -DLINKTIME -c mymalloc.c 
	gcc -Wall -c int.c 
	gcc -Wall -Wl,--wrap,malloc -Wl,--wrap,free -o intl 
	int.o mymalloc.o 
	linux> make runl 
	./intl 
	malloc(32) = 0x1aa0010 
	free(0x1aa0010)
	```
	> `-Wl`将后面的逗号替换为空格
	> 使用 `--wrap=symbol`,`symbol`也是一个函数时,对`symbol`的引用会解析为`__wrap_symbol`函数.
	> 另外还有一个`__real_symbol`函数,只声明不定义时,对其调用会解析到真正的`symbol`函数.
	> 即:
	>	- `malloc` -> `__wrap_malloc`
	>	- `__real_malloc` -> `malloc`
- 运行时
	编写`mymalloc.c`:
	```c
	#ifdef RUNTIME 
	#define _GNU_SOURCE 
	#include 
	#include 
	#include 
	
	/* malloc wrapper function */ 
	void *malloc(size_t size) { 
		void *(*mallocp)(size_t size); 
		char *error; 
		mallocp = dlsym(RTLD_NEXT, "malloc"); /* Get addr of libc malloc */ 
		if ((error = dlerror()) != NULL) { fputs(error, stderr); exit(1); } 
		char *ptr = mallocp(size); /* Call libc malloc */ 
		printf("malloc(%d) = %p\n", (int)size, ptr); 
		return ptr; 
	}

	/* free wrapper function */
	 void free(void *ptr) { 
		 void (*freep)(void *) = NULL; 
		 char *error; 
		 if (!ptr) return; 
		 freep = dlsym(RTLD_NEXT, "free"); /* Get address of libc free */ 
		 if ((error = dlerror()) != NULL) { fputs(error, stderr); exit(1); } 
		 freep(ptr); /* Call libc free */ 
		 printf("free(%p)\n", ptr); 
	 } 
	 #endif
	```
	gcc构建:
	```shell
	linux> make intr 
	gcc -Wall -DRUNTIME -shared -fpic -o mymalloc.so mymalloc.c -ldl 
	gcc -Wall -o intr int.c 
	linux> make runr 
	(LD_PRELOAD="./mymalloc.so" ./intr) 
	malloc(32) = 0xe60010 
	free(0xe60010) 
	```
	> `LD_PRELOAD`环境变量告诉动态连接器优先在`mymalloc.so`中寻找未解析引用.
	> `dlsym(RTLD_NEXT, "malloc")`让动态链接器寻找下一个`malloc`函数指针