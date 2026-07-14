---
title: "线性代数及矩阵分析习题（回忆版）"
description: ""
pubDate: 2026 07 13 10:46
categories: 
  - tech
---

## 1. 判断下列集合是否构成线性空间

### a. $W_{1}=\{(x,y,z)|x^{2}+y^{2}+z^{2}\le 1\}$

举一反例,
取$$\alpha=(1,0,0)\in W_{1},\beta=(0,1,0)\in W_{1}$$

但
$$
\alpha+\beta=(1,1,,0),\left \| \alpha+\beta \right \| =2 > 1
$$
所以$\alpha+\beta=(1,1,0)\not\in W_{1}$,加法不满足封闭性,因此$W_{1}$不构成线性空间.

### b. $\mathbb{R} ^3$中, $W_{3}=\{(x_{1},x_{2},x_{3})|\int_{0}^1(x_{1}t^{2}+x_{2}t+x_{3})\mathrm{d}t =0\}$

设$\alpha=(x_{1},x_{2},x_{3}),\beta=(y_{1},y_{2},y_{3})$，$\alpha+\beta=(x_{1}+y_{1},x_{2}+y_{2},x_{3}+y_{3})$
且
$$\int_{0}^1[(x_{1}+y_{1})t^{2}+(x_{2}+y_{2})t+(x_{3}+y_{3})]\mathrm{d}t=0$$
因此$\alpha+\beta \in W_{3}$.

$k\alpha=(kx_{1},kx_{2},kx_{3})$,且
$$
\int_{0}^1(kx_{1}t^{2}+kx_{2}t+kx_{3})\mathrm{d}t=k\int_{0}^1(x_{1}t^{2}+x_{2}t+x_{3})=0
$$

因此$k\alpha\in Ww_{3}$.
综上,$W_{3}$对加法和数乘封闭,构成线性空间.

## 2. 设$\alpha_{1}=(1,1,0,1)^T$,$\alpha_{2}=(2,1,3,1)^T$,$\alpha_{3}=(1,1,0,0)^T$,$\alpha_{4}=(0,1,-1,-1)^T$.证明它们是$\mathbb{R}^4$的基,并求$\beta=(2,2,4,1)^T$在此基下的坐标

令
$$
A=\begin{bmatrix}
\alpha_{1},\alpha_{2},\alpha_{3},\alpha_{4}
\end{bmatrix}=\begin{bmatrix}
1&2&1&0\\1&1&1&1\\0&3&0&-1\\1&1&0&-1
\end{bmatrix}
$$

计算得
$$
\det A=-2\not=0
$$
所以$A$的秩是4,$\alpha_{1},\alpha_{2},\alpha_{3},\alpha_{4}$线性无关,构成$\mathbb{R}^4$的一组基.
设
$$
Ax=\beta
$$

解得
$$
x=\begin{bmatrix}
1\\2\\-3\\2
\end{bmatrix}
$$

因此$\beta$在基$\alpha_{1},\alpha_{2},\alpha_{3},\alpha_{4}$下的坐标为$(1,2,-3,2)^T$

## 3. $\mathbb{R}^{2 \times 2}$中线性变换$T$做标准基$E_{11},E_{12},E_{21},E_{22}$下的矩阵为$A=\begin{bmatrix}1&2&0&0\\ 0&1&0&0 \\ 0&0&3&1 \\ 0&0&0&2 \end{bmatrix}$,求$T$在基$G_{11}=\begin{bmatrix}1&1\\1&1\end{bmatrix},G_{12}=\begin{bmatrix}0&1\\1&1\end{bmatrix},G_{21}=\begin{bmatrix}0&0\\1&1\end{bmatrix},G_{22}=\begin{bmatrix}0&0\\0&1\end{bmatrix}$下的矩阵

$$
[G_{11},G_{12},G_{21},G_{22}]=[E_{11},E_{12},E_{21},E_{22}]\begin{bmatrix}
1&0&0&0\\1&1&0&0\\1&1&1&0\\1&1&1&1 \\
\end{bmatrix}
=[E_{11},E_{12},E_{21},E_{22}]P
$$

且
$$
P^{-1}=\begin{bmatrix}
1&0&0&0\\
-1 & 1 & 0 & 0 \\
0 & -1 & 1 & 0 \\
0 & 0 & -1 & 1
\end{bmatrix}
$$

设
$$
T(G_{11},G_{12},G_{21},G_{22})=[G_{11},G_{12},G_{21},G_{22}]B
$$

那么
$$
T(G_{11},G_{12},G_{21},G_{22})=[G_{11},G_{12},G_{21},G_{22}]B
=[E_{11},E_{12},E_{21},E_{22}]PB

$$

又
$$
T(G_{11},G_{12},G_{21},G_{22})=T(E_{11},E_{12},E_{21},E_{22})P
=[E_{11},E_{12},E_{21},E_{22}]AP
$$

故
$$
PB=AP \Rightarrow B=P^{-1}AP
$$

计算得

$$
B=\begin{bmatrix}
3 & 2 & 0 & 0 \\
-2 & -1 & 0 & 0 \\
3 & 3 & 4 & 1 \\
-2 & -2 & -2 & 1
\end{bmatrix}
$$

## 4. 设$T:\mathbb{R}^{4} \to \mathbb{R}^{3}$.$T(x_{1},x_{2},x_{3},x_{4})=(x_{1}-x_{2}+x_{3}+x_{4},x_{1}+2x_{2}-x_{4},x_{1}+x_{2}+3x_{3}-x_{4})^T$,求$T$的值域与核

$$
T(x_{1},x_{2},x_{3},x_{4})=\begin{bmatrix}
1 & -1 & 1 & 1 \\
1 & 2 & 0 & -1 \\
1 & 1 & 3 & -1
\end{bmatrix}
\begin{bmatrix}
x_{1} \\
x_{2} \\
x_{3} \\
x_{4}
\end{bmatrix}
$$
设
$$
A=\begin{bmatrix}
1 & -1 & 1 & 1 \\
1 & 2 & 0 & -1 \\
1 & 1 & 3 & -1
\end{bmatrix}
\sim
\begin{bmatrix}
1 & -1 & 1 & 1 \\
0 & 3 & -1 & -2 \\
0 & 0 & 4 & -1
\end{bmatrix}
$$

所以$A$的秩是3,值域是$\mathbb{R}^{3}$.

核空间满足$Ax=0$,解得
$$
x=(2,-3,-1,4)^T
$$

所以$A$的核是$(2,-3,-1,4)^T$张成的空间.

## 5. 已知$A=\begin{bmatrix}-1&1&0\\-4&3&0 \\ 1&0&2\end{bmatrix}$,求$g(A)=A^{7}-A^{5}-19A^{4}+28A^{3}+6A-4I$

三阶子式
$$
\det(A-\lambda I)=(2-\lambda)[(\lambda-3)(\lambda+1)+4]
=(\lambda-1)^{2}(2-\lambda)
$$
所以
$$
D_{3}=(\lambda-1)^{2}(\lambda-2)
$$
二阶子式中有

$$
\begin{vmatrix}
-4 & 3-\lambda \\
1 & 0
\end{vmatrix}=\lambda-3
$$

$$
\begin{vmatrix}
-1-\lambda & 1 \\
-4 & 3-\lambda
\end{vmatrix}=(\lambda-1)^{2}
$$

因此
$$
D_{2}=D_{1}=1
$$
不变因子
$$
d_{3}=\frac{D_{3}}{D_{2}}=(\lambda-1)^{2}(\lambda-2)
$$

$$
d_{2}=d_{1}=1
$$

$A$的最小多项式是
$$
\varphi(\lambda)=(\lambda-1)^{2}(\lambda-2)
$$

$$
\varphi(A)=(A-I)^{2}(A-2I)=0
$$

所以$g(A)$可由$A^{2},A,I$线性表示.设为$f(A)=a_{0}I+a_{1}A+a_{2}A^{2}$

$$
\begin{cases}
g(1)=f(11)=a_{0}+a_{1}+a_{2} \\
g'(1)=f'(16)=a_{1}+2a_{2} \\
g(2)=f(2)=24=a_{0}+2a_{1}+4a_{2}
\end{cases}
$$

解得
$$
\begin{cases}
a_{0}=-8 \\
a_{1}=22 \\
a_{2}=-3
\end{cases}
$$
即
$$
g(A)=-8I+22A-3A^{2}
$$
计算
$$
A^{2}=\begin{bmatrix}
-3 & 2 & 0 \\
-8 & 5 & 0 \\
1 & 1 & 4
\end{bmatrix}
$$

故
$$
g(A)=\begin{bmatrix}
-21 & 16 & 0 \\
-64 & 43 & 0 \\
19 & -3 & 24
\end{bmatrix}
$$

## 6. 已知$A=\begin{bmatrix}1&2&-6 \\ 1&0&-3 \\ 1&1&-4\end{bmatrix}$,求$e^{A}$,$\sin A$

$$
\det(A-\lambda I)=
\begin{vmatrix}
1-\lambda & 2 & -6 \\
1 & -\lambda & -3 \\
1 & 1 & -4-\lambda
\end{vmatrix}=
-(\lambda+1)^{3}
$$

因此
$$
D_{3}=(\lambda+1)^{3}
$$

二阶子式
$$
D_{2}=\lambda+1
$$
因此不变因子
$$
d_{3}=\frac{D_{3}}{D_{2}}=(\lambda+1)^{2}
$$
$$
d_{2}=d_{1}=1
$$

$A$的最小多项式是
$$
\varphi(\lambda)=(\lambda+1)^{2}
$$
故$A$的矩阵函数可由$I,A$线性表示.

### a. 求$e^{A}$

设$f(A)=e^{A}=p(A)=a_{0}I+a_{1}A$,则

$$
\begin{cases}
f(-1)=g(-1)=\frac{1}{e}=a_{0}-a_{1} \\
f'(-1)=g'(-1)=\frac{1}{e}=a_{1}
\end{cases}
$$
解得

$$
\begin{cases}
a_{0}=\frac{2}{e} \\
a_{1}=\frac{1}{e}
\end{cases}
$$
所以
$$
e^{A}=\frac{2}{e}I+\frac{1}{e}A=\frac{1}{e}(2I+A)
$$

故
$$
\boxed{
e^A=e^{-1}
\begin{bmatrix}
3&2&-6\\
1&2&-3\\
1&1&-2
\end{bmatrix}
}
$$

### b. 求$\sin A$

设$g(A)=\sin A=q(A)=b_{0}I+b_{1}A$,则

$$
\begin{cases}
g(-1)=f(-1)=-\sin 1=b_{0}-b_{1} \\
g'(-1)=f'(-1)=\cos 1=b_{1}
\end{cases}
$$

所以
$$
\sin A=\cos1\cdot A+(\cos1-\sin1)I
$$
逐项相加得
$$
\boxed{
\sin A=
\begin{bmatrix}
2\cos1-\sin1&2\cos1&-6\cos1\\
\cos1&\cos1-\sin1&-3\cos1\\
\cos1&\cos1&-3\cos1-\sin1
\end{bmatrix}
}
$$

## 7. 设$\alpha_{1},\alpha_{2},\alpha_{3},\alpha_{4}$是$\mathbb{R}^{4}$的一组基,$V_{1}=L(2\alpha_{1}+\alpha_{2},\alpha_{1})$,$V_{2}=L(\alpha_{3}-\alpha_{4},\alpha_{1}-\alpha_{4})$.证明$\mathbb{R}^{4}=V_{1}\oplus V_{2}$

先证$V_{1}+V_{2}=\mathbb{R}^{4}$:

设$x=k_{1}(2\alpha_{1}+\alpha_{2})+k_{2}\alpha_{1}\in V_{1}$,$y=k_{3}(\alpha_{3}-\alpha_{4})+k_{4}(\alpha_{1}-\alpha_{4})$,
那么
$$
x+y=(2k_{1}+k_{2}+k_{4})\alpha_{1}+k_{1}\alpha_{2}+k_{3}\alpha_{3}+(k_{4}-k_{3})\alpha_{4}
$$
系数不同时为0,所以$V_{1}+V_{2}=\mathbb{R}^{4}$

再证$V_{1}+V_{2}$成为直和$V_{1}\oplus V_{2}$:

即证:

$2\alpha_{1}+\alpha_{2},\alpha_{1}$是$V_{1}$的基,$\alpha_{3}+\alpha_{4},\alpha_{1}-\alpha_{4}$是$V_{2}$的基,
$2\alpha_{1}-\alpha_{2},\alpha_{1},\alpha_{3}-\alpha_{4},\alpha_{1}-\alpha_{4}$是$V_{1}+V_{2}$(即$\mathbb{R}^{4}$)的基.

$$
[2\alpha_{1}-\alpha_{2},\alpha_{1},\alpha_{3}-\alpha_{4},\alpha_{1}-\alpha_{4}]=[\alpha_{1},\alpha_{2},\alpha_{3},\alpha_{4}]
\begin{bmatrix}
2 & 1 & 0 & 1 \\
-1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & -1 & -1
\end{bmatrix}
$$

又
$$
\det ([2\alpha_{1}-\alpha_{2},\alpha_{1},\alpha_{3}-\alpha_{4},\alpha_{1}-\alpha_{4}])=\det([\alpha_{1},\alpha_{2},\alpha_{3},\alpha_{4}])
\begin{vmatrix}
2 & 1 & 0 & 1 \\
-1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & -1 & -1
\end{vmatrix}=-\det([\alpha_{1},\alpha_{2},\alpha_{3},\alpha_{4}])\not=0
$$

因此$2\alpha_{1}-\alpha_{2},\alpha_{1},\alpha_{3}-\alpha_{4},\alpha_{1}-\alpha_{4}$线性无关,构成$\mathbb{R}^{4}$的基.

这就证明了$V_{1}\oplus V_{2}=\mathbb{R}^{4}$.

## 8. 求常系数线性微分方程 $\begin{cases}y'''+7y''+14y'+8y=0\\y''(0)=y'(0)=0,y(0)=1\end{cases}$ 的初值问题

令$y_{1}=y,y_{2}=y',y_{3}=y''$,

$$
\begin{cases}
y'=y_{2} \\
y''=y_{3} \\
y'''=-7y_{3}-14y_{2}-8y_{1}
\end{cases}
$$

即
$$
Y'=\begin{bmatrix}
0 & 1 & 0 \\
0 & 0 & 1 \\
-7 & -14 & -8
\end{bmatrix}
\begin{bmatrix}
y_{1} \\
y_{2} \\
y_{3}
\end{bmatrix}
=AY
$$
这个微分方程的通解是
$$
Y=e^{At}Y(0)
$$
其中
$$
Y(0)=\begin{bmatrix}
1 \\
0 \\
0
\end{bmatrix}
$$

令$f(A)=e^{At}$.$A$的特征方程
$$
\det(A-\lambda I)=-(\lambda+1)(\lambda+2)(\lambda+4)
$$
特征值互异,最小多项式就是
$$
m(\lambda)=(\lambda+1)(\lambda+2)(\lambda+4)
$$
因此$e^{At}$可由$I,A,A^{2}$线性表示,设为$g(A)=a(t)I+b(t)A+c(t)A^{2}$.

$$
\begin{cases}
f(-1)=g(-1)=e^{-t}=a-b+c \\
f(-2)=g(-2)=e^{-2t}=a-2b+4c \\
f(-4)=g(-4)=e^{-4t}=a-4b+16c
\end{cases}
$$

解这个三元一次方程组，得：

$$
\boxed{
a(t)=\frac83 e^{-t}-2e^{-2t}+\frac13 e^{-4t}
}
$$

$$
\boxed{
b(t)=2e^{-t}-\frac52 e^{-2t}+\frac12 e^{-4t}
}
$$

$$
\boxed{
c(t)=\frac13 e^{-t}-\frac12 e^{-2t}+\frac16 e^{-4t}
}
$$

又
$$
A=\begin{bmatrix}0&1&0\\0&0&1\\-7&-14&-8\end{bmatrix},\quad
A^2=\begin{bmatrix}0&0&1\\-7&-14&-8\\56&112&57\end{bmatrix}.
$$

初值
$$
Y(0)=\begin{bmatrix}1\\0\\0\end{bmatrix}.
$$

于是
$$
Y(t)=e^{At}Y(0)=a(t)\begin{bmatrix}1\\0\\0\end{bmatrix}
+b(t)A\begin{bmatrix}1\\0\\0\end{bmatrix}
+c(t)A^2\begin{bmatrix}1\\0\\0\end{bmatrix}.
$$

因为
$$
A\begin{bmatrix}1\\0\\0\end{bmatrix}=\begin{bmatrix}0\\0\\-7\end{bmatrix},\quad
A^2\begin{bmatrix}1\\0\\0\end{bmatrix}=\begin{bmatrix}0\\-7\\56\end{bmatrix},
$$
所以
$$
Y(t)=
\begin{bmatrix}
a(t)\\
-7c(t)\\
-7b(t)+56c(t)
\end{bmatrix}.
$$

第一行即为 $y(t)$：
$$
y(t)=a(t)=\frac83 e^{-t}-2e^{-2t}+\frac13 e^{-4t}.
$$

因此初值问题的解为
$$
\boxed{y(t)=\frac83 e^{-t}-2e^{-2t}+\frac13 e^{-4t}}
$$

## 参考资料

1. [【矩阵论】Jordan 标准型及其求解方法](https://zhuanlan.zhihu.com/p/517900683)
2. [【矩阵论笔记】最小多项式与Jordan型的关系](https://blog.csdn.net/bless2015/article/details/105974793)
3. [矩阵论(二)——Jordan标准形](https://blog.csdn.net/u011609063/article/details/102505748)
