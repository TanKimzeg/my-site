---
title: 高速缓存
description: ""
pubDate: "Jan 27 2025"
categories:
    - tech
tags:
    - csapp
---


高速缓存包含在CPU芯片中,完全由硬件管理,用快速SRAM做的,位于存储器旁边的缓存.
![](attachments/Pasted%20image%2020250127221315.png)

# 缓存组织方式
一个存储器的地址有m位,形成M=2^ m个地址,它的高速缓存被设计为S*组*,每个组包含E*行*,每行是由一个B字节的数据*块*,一个指示这行是否包含有意义信息的*有效位*,以及t个*标记位*组成的.
地址组成:
![](attachments/Pasted%20image%2020250128111730.png)
高速缓存组成:
![](attachments/Pasted%20image%2020250128112051.png)
高速缓存大小为:C=B\*E\*S
以上涉及很多符号,但实际上高速缓存由4个基本参数决定,其他的是衍生出来的量.

- 基本参数

参数|描述
---|---
$S=2^s$|组数
$E$|每个组的行数
$B=2^b$|块大小(字节)
$m=\log_{2}M$|主存物理地址位数
- 衍生量

参数|描述
---|---
$M=2^m$|内存地址最大数
$s=\log_{2}S$|组索引位数
$b=\log_{2}B$|块偏移位数
$t=m-(s+b)$|标记位数
$C=B\times E\times S$|高速缓存大小(不包括像有效位和标记位开销)
根据E的不同,高速缓存被分为不同类
## 直接映射高速缓存
E=1的高速缓存称为*直接映射*高速缓存.
读取缓存分为三步:
1. 组选择
	从请求的地址中间抽取s个组索引位,对应到缓存的组
2. 行匹配
	由于每组只有一行,当且仅当设置了有效位并且高速缓存行中的标记与地址中的标记位相匹配时,这一行就含有请求的数据.
	如果不匹配,缓存不命中,那么需要从下一级取出块,替换当前行
3. 字选择
	块偏移提供了所需数据的第一个字节的位置,然后根据数据类型取出多个字节.

这种方式,容易发生[[存储器层次结构#缓存|conflict miss]]

## 组相联高速缓存
1<E<C/B
组选择和字选择与直接映射高速缓存相同,行匹配则需检查多个行的标记位和有效位.如果不命中,取出块替换一个不会马上被使用的行.

## 全相联高速缓存

# 英特尔i7缓存层次结构
![](attachments/Pasted%20image%2020250128120939.png)
L1缓存:4CPU时钟周期
L2缓存:10CPU时钟周期
L3缓存:40~75CPU时钟周期
块大小:64字节

# 编写缓存友好型代码
提高缓存命中率
- 使常用部分更加快
例如常用的函数及其内部循环
- 提高循环中的命中率
	- 重复使用局部变量(时间局部性)
	- 逐元素访问数组(空间局部性)

# 缓存对代码性能的影响
## Memory Moutain
`test`函数:
```c
long data[MAXELEMS]; /* Global array to traverse */ 
/* test - Iterate over first "elems" elements of 
 *        array “data” with stride of "stride", using 
 *        using 4x4 loop unrolling. 
 */ 
int test(int elems, int stride) { 
	long i, sx2=stride*2, sx3=stride*3, sx4=stride*4; 
	long acc0 = 0, acc1 = 0, acc2 = 0, acc3 = 0; 
	long length = elems, limit = length - sx4; 
	
	/* Combine 4 elements at a time */ 
	for (i = 0; i < limit; i += sx4) { 
		acc0 = acc0 + data[i]; 
		acc1 = acc1 + data[i+stride]; 
		acc2 = acc2 + data[i+sx2]; 
		acc3 = acc3 + data[i+sx3]; 
	} 
	
	/* Finish any remaining elements */ 
	for (; i < length; i++) { 
		acc0 = acc0 + data[i]; 
	} 
	return ((acc0 + acc1) + (acc2 + acc3)); 
}
```
以不同的(elems, stride)组合调用 `test()`函数.首先调用一次给缓存热身,再调用一次测试读取速度性能(MB/s).得到了这副封面上美丽的图:
![](attachments/Pasted%20image%2020250129100926.png)
随着stride轴增大,减小了空间局部性;随着size轴增大,减小了时间局部性.

## 在矩阵乘法中提高局部性
### 重新排列循环，提高空间局部性
假设矩阵维度很大，缓存中的一个块存放4个元素
1. ijk访问
```c
/* ijk */ 
for (i=0; i<n; i++){
	for(j=0;j<n;j++){
		sum =0.0;
		for(k=0;k<n;k++)
			sum += a[i][k]*b[k][j];
		c[i][j] = sum;
	}
}
```
![](attachments/Pasted%20image%2020250130205312.png)
缓存不命中的概率是:

A|B|C
:---:|:---:|:---:
0.25|1.0|0.0
2. jik访问
与ijk访问无异.
3. kij访问
```c
/* kij */
for(k=0;k<n;k++){
	for(i=0;i<n;i++){
		r = a[i][k];
		for(j=0;j<n;j++)
			c[i][j] += r*b[k][j];
	}
}
```
![](attachments/Pasted%20image%2020250130205806.png)
缓存不命中的概率是:

A|B|C
:---:|:---:|:---:
0|0.25|0.25

4. ikj访问
与kij访问无异
5. jki访问
```c
/* jki */
for(j=0;j<n;j++){
	for(k=0;k<n;k++){
		r = b[k][j];
		for(i=0;i<n;i++)
			c[i][j] += a[i][k]*r;
	}
}
```
![](attachments/Pasted%20image%2020250130210233.png)
缓存不命中的概率是:

A|B|C
:---:|:---:|:---:
1.0|0.0|1.0
6. kji访问
与jki访问无异

### 矩阵分块,提高时间局部性
假设高速缓存块中包含8个元素,矩阵维数n足够大.
1. 传统计算方法
```c
c = (double *) calloc(sizeof(double), n*n); 

/* Multiply n x n matrices a and b */ 
void mmm(double *a, double *b, double *c, int n) { 
	int i, j, k; 
	for (i = 0; i < n; i++) 
		for (j = 0; j < n; j++) 
			for (k = 0; k < n; k++) 
				c[i*n + j] += a[i*n + k] * b[k*n + j]; 
}
```
在没有分块的传统计算方式中,每一个结果元素的迭代,会发生9n/8次缓存不命中:
![](attachments/Pasted%20image%2020250130210842.png)
所以计算整个矩阵乘法,会发生
9n/8\*n^ 2 = (9/8) n^ 3次缓存不命中

2. 矩阵分块计算方法
```c
c = (double *) calloc(sizeof(double), n*n); 

/* Multiply n x n matrices a and b */ 
void mmm(double *a, double *b, double *c, int n) { 
	int i, j, k; 
	for (i = 0; i < n; i+=B) 
		for (j = 0; j < n; j+=B) 
			for (k = 0; k < n; k+=B) 
				/* B x B mini matrix multiplications */ 
				for (i1 = i; i1 < i+B; i++) 
					for (j1 = j; j1 < j+B; j++) 
						for (k1 = k; k1 < k+B; k++) 
							c[i1*n+j1] += a[i1*n + k1]*b[k1*n + j1]; 
}
```
假设矩阵分成B\*B的小块,对于每一个小块,在遍历其元素时会发生B^ 22/8次缓存不命中.对计算结果的每一小块,会发生2n/B\*B^ 2/8=nB/4次缓存不命中,所以整个结果矩阵会发生nB/4\*(n/B)^ 2=n^ 3/(4B)次缓存不命中.
![](attachments/Pasted%20image%2020250130211852.png)

从结果来看,分块与不分块造成了相当大的差异!如果按照数据结构中理论上的时间复杂度来看,他们的时间复杂度是一样的,但在计算机的缓存机制下,差异凸显!

