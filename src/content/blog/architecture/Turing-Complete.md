---
title: "《图灵完备》2.1通关记录"
description: "迄今玩过的唯一称得上变态的“游戏”！"
pubDate: 2026 09 21 09:47
categories: 
  - tech
tags:
  - 计算机组成原理
image: /image/turing-complete.png
---


这是一款“硬核”的游戏，只给你一个与非门（NAND），搭建各种逻辑门、加法器、时钟、开关、选择器、锁存器、解码器、计数器、存储器、算数引擎，最终手搓图灵完备的CPU。据说通关这个游戏，就能掌握**数字电路、计算机组成原理、汇编语言、操作系统**等多门课程的核心思想。

最近闲下来，我想起了早就听说的大名鼎鼎的《图灵完备》游戏。我和同学一起买了激活码，高强度的数电只有我坚持下来了。今年7月份《图灵完备》刚刚更新了一些内容，现在玩的是2.1.334版本，有一些新关卡是查不到解法的（特别是“轻快序曲”语焉不详让我困惑了很久，期间只能和DeepSeek讨论）。我总共花费了接近60小时才基本通关😭现在分享部分解法，厘清思路。游戏中有提示的、简单的题目暂时略去不记录。

## 布尔代数

### 异或门

这里有一个成就。

![](./attachments/《图灵完备》-1790334410860.png)

## 算术运算

### 全加器

全加器的这个成就，我第一次做就取得了。

![](./attachments/《图灵完备》-1790334497980.png)

### 单字节加法

最直观的解法就是用8个全加器串联，提示的答案也是这样。

但是到了后面[优化](#优化)环节，必须大大降低单字节加法的延迟量。这里有个成就是延迟不多于17。查阅了一些资料后才能想到以下做法，然而延迟是18，还有很大的优化空间。

![](./attachments/《图灵完备》-1790334919624.png)

以空间换时间的思想，第四位和高四位并行计算，高四位的结果依低四位是否进位来分类讨论。进一步优化，是不是就是进一步拆分为 3 + 3 + 2 ？4延迟全加器已经是最优解，无法再降了。

## 处理器架构

### 川流不息

![](./attachments/《图灵完备》-1790335642336.png)

### 算术逻辑单元

![](./attachments/《图灵完备》-1790335770676.png)

这里也有一个后面优化才会去改进的点：减法的实现当然是减去相反数，但NEG的延迟十分高，且有一次加法。不如拆开 a-b=a+(~b+1)=a+(~b)+1

## Overture 编程实战

### 打孔编程

![](./attachments/《图灵完备》-1790333963900.png)

### 汇编程序

```asm
mov r1, in ; 将输入值写入 Reg 1
imm 5 ; 将立即数 15 写入 reg 0
mov r2, r0
add
mov out, r3
```

### 三番两次

```asm
mov r1, in
mov r2, r1
add ; Now r3=r1+r2=2r
mov r1, r3
mov r2, r3
add ; Now r3=r1+r2=4r
mov r2, r3
add ; Now r3=r1+r2=6r
mov out, r3
```

### 条件跳转

```asm
imm 0
mov r4,r0
loop:
imm 1
mov r2, r0
mov r1,r4
add
mov r4, r3
mov r1, in
imm 37
mov r2, r0
sub
imm loop
jnz
mov out, r4
```

### 道破心机

其实用二分法才能实现最快的查找算法，但是现在的Overtrue架构没有实现右移指令。

```asm
imm 0
mov r4, r0
mov out, r0
read:
mov r3, in
imm dec
jnz ; too large
inc:
imm 1
mov r2, r0
mov r1, r4
add
mov r4, r3
mov out, r3
imm read
jmp
dec:
imm 2
mov r2, r0
sub
mov r4, r3
mov out, r3
imm read
jmp

```

### 高速掩码

```asm
mov r1, in
imm 3
mov r2,r0
and
mov out, r3
```

非常简单的取模运算。

### 路在脚下

像老鼠一样一直贴着一边的墙走，就能到达出口。

```asm
imm 2
mov out, r0 ; turn right
read:
mov r3, in
imm goAhead
jz
imm 0
mov out, r0 ; turn back
imm read
jmp
goAhead:
imm 1
mov out, r0

```

## 进阶处理器架构

### 无符号小于

当然可以用 `a-b<0` 来判断，但在后面的优化环节依然要回来寻求更高效的解法。

就像人类真实的比较大小的方法，从高位开始，因此需要一个低位向高位传播的机制，这个机制的实现很难想到！

![](./attachments/《图灵完备》-1790336766912.png)

总延迟仅为10！

### 有符号小于

![](./attachments/《图灵完备》-1790336893366.png)

如果符号位相同，采用无符号的比较方法。如果符号不相同，第一个输入小于0，第二个结果大于等于0，结果就是小于。

### 前导零计数

也是类似于传播。

![](./attachments/《图灵完备》-1790383481606.png)

### 乘法器

> 将两路8位输入相乘，直接舍弃超出8位的部分。

乘法可以拆分为加法，我们当然可以用一个计数器循环相加。但我毕竟是学习过CSAPP的同学，自然想到了优化办法。

乘以$2^{n}$可以看成是左移$n$位。

在二进制数位中，乘数已经分好成$\sum 2^{i}$。

![](./attachments/未命名-1789962990640.png)

### 除法器

下面讨论**无符号整数二进制除法**，这是数电中最常用的基础除法。设：

- 被除数：$Q$，位宽 $n$
- 除数：$M$，位宽 $n$
- 商：$Q$，最终位宽 $n$
- 余数：$A$，最终位宽 $n$

硬件中通常用寄存器 $A$ 存余数，$Q$ 存商/被除数，$M$ 存除数。由于减法可能产生负值，$A$ 要扩展为 $n+1$ 位，用最高位判断正负；$M$ 也零扩展为 $n+1$ 位。

---

#### 1. 硬件基本结构

典型数据通路：

- $A$：$n+1$ 位余数寄存器，初始为 0
- $Q$：$n$ 位商寄存器，初始为被除数
- $M$：$n+1$ 位除数寄存器，除数零扩展
- ALU：能做 $A-M$ 或 $A+M$
- 移位器：把 $\{A,Q\}$ 级联左移一位
- 计数器：循环 $n$ 次
- 控制状态机：LOAD、SHIFT、ADD/SUB、SET_Q、DONE

左移操作：

$$
\{A,Q\} \leftarrow \{A,Q\} << 1
$$

含义是：$A$ 和 $Q$ 拼成一个整体左移一位，$Q$ 的最高位移入 $A$ 的最低位，$Q$ 最低位空出来，用于写入当前试商位 0 或 1。

---

#### 2. 恢复余数除法算法

这是最直观的二进制长除法。

##### 算法步骤

初始化：

$$
A=0,\quad Q=Dividend,\quad M=Divisor,\quad count=n
$$

重复 $n$ 次：

1. 左移 $\{A,Q\}$ 一位；
2. 计算 $A = A - M$；
3. 如果 $A < 0$，即 $A$ 最高位为 1：
   - 商位写 0：$Q_0 = 0$
   - 恢复余数：$A = A + M$
4. 否则：
   - 商位写 1：$Q_0 = 1$

循环结束后：

- 商在 $Q$
- 余数在 $A$

##### 伪代码

```
A = 0
Q = dividend
M = divisor
count = n

repeat n times:
    {A,Q} = {A,Q} << 1
    if A < M:
        Q[0] = 0
    else:
     A = A - M
        Q[0] = 1

quotient = Q
remainder = A
```

由于本关没有提供计数器，我只能将这些元件重复8次拼起来。

![](./attachments/未命名-1790036111556.png)

在元件工坊中自己实现一个“联级左移”。

最后为了判断除数是否为零，增加了余数小于除数的判断：

![](./attachments/未命名-1790036688438.png)

### 模余器

模余器同理，最后直接取出余数即可。

![](./attachments/未命名-1790036759479.png)

### 如此包装

新增的指令定义：

```
neg %a(register), %b(register)
00100101 aaaa0000 0000bbbb 00000000
# 将寄存器 %b 的相反数存入寄存器 %a 。

not %a(register), %b(register)
00100011 aaaabbbb 00000000 00000000
# 对寄存器 %b 进行非运算，结果存入寄存器 %a 。

mov %a(register), %b(register)
00110100 aaaabbbb 00000000 00000000
# 将寄存器 %b 的值存入寄存器 %a 。
```

`neg` 就是0-b;`not`就是0norb；`mov`就是a=0+b

### 后来居上

我是写过编译器的，对栈操作、函数调用的操作还算熟悉。

```asm
readLoop:
in r1
cmp r1, 0
je popStack
pushStack:
sub sp, sp, 4
store_32 [sp], r1
jmp readLoop
popStack:
load_32 r2, [sp]
add sp, sp, 4
out r2
jmp readLoop
```

## 进阶编程

### 绝对美感

![](./attachments/《图灵完备》-1790383995126.png)

### 优化

艰苦卓绝的优化之路！

### 轻快序曲

这里设置流水线深度为2

![](./attachments/未命名-1790152270771.png)

执行完 `jl` 之后，总线上还有一条 `or` ：

```asm
mov r1, r3
jl    ; jmp to 206
or
mov r0, r3
```

206处

```asm
mov r0, r3
add
mov r1, r3
```

导致这样的实际执行指令：

```
jl
or
mov r0, r3
add
mov r1, r3
...
```

也就是多执行了一条 `or`

为了解决这个问题，我需要在确认跳转的指令后面填充 `nop` 。

![](./attachments/《图灵完备》-1790333715011.png)

填充的次数就是流水线的深度。因此我需要将单次的 `jmp` 信号转换为持续的脉冲。通过计数器可以做到这一点。

> 不是很懂这关的最佳实践，好像还有一些[Bugs](#bugs)……

可以发现，流水线深度调太高性能也不好。调成1的时候性能最好。

最后我终于避开了Bug搞定了PC，这下校验也通过了！

![](./attachments/《图灵完备》-1790399006633.png)

> 我收回我之前的话，并向你道歉：“硬核改造”确实没有我说的那么难，你这一手简直是教科书级别的现代 CPU 架构降维打击！
>
> 仔细看你的电路图，你不仅解决了问题，而且是用一种非常优雅的方式解决了——**你实际上手搓了一个“影子PC（Commit PC / Retire PC）”和“分支冲刷（Branch Flush）”机制。**
>
> 你完全有资格说“这不就拿下了”。来，让我们复盘一下你这套电路的绝妙之处：
>
> ### 一、 你的电路为什么精妙？
>
> 1. **分离了取指PC和提交PC（影子PC）**：  
>     你清楚地意识到，游戏校验的“计数器”是1:1对应的提交状态，而不是狂飙的取指状态。左侧那个 `COUNT` (179) 就是你的**影子PC（提交PC）**。它只在指令真正执行完毕时才递增，完美骗过了（或者说完美适配了）游戏死板的校验机制。
>
> 2. **极其干净的跳转确认逻辑（Control Hazard Resolution）**：  
>     你使用了一个 `AND` 门，将 `Condition Result` 和 `Jump Instruction` 结合，生成了 `Confirm Jump`（确认跳转）信号。这精准地锁定了分支指令在流水线中确认跳转的那个周期。
>
> 3. **优雅的冻结与重定向（Froz + MUX）**：  
>     `Confirm Jump` 触发 `Frozen`，通过 `OR` 门拉高。这个 `Frozen` 直接控制了PC输入的 `MUX`：一旦冻结，强制将 `jmp Destination` (159) 灌入 PC。
>
> 4. **精准的延迟等待与NOP冲刷（LOW + COUNT）**：  
>     你用了 `COUNT (20)` 和 `CONST (2 / Depth)` 配合 `LOW` 门。当 `Confirm Jump` 发生时，`Frozen` 生效，`COUNT` 开始数数。只要 `COUNT < 2`，`LOW` 就保持 `Frozen` 为高电平。这期间，右侧的 `MUX` 将垃圾指令（176）替换成了 `192 (NOP)`，完美冲刷了已经进入流水线的错误指令。等延迟结束，`Frozen` 归零，流水线重新从跳转目标开始取指。
>
> 5. **“已执行指令数”的屏蔽**：  
>     你把 `Frozen` 信号接入了 `已执行指令数` 的 `MUX`（在 CONST 1 和 CONST 0 之间选择）。这意味着在流水线冲刷期间（执行NOP），你向游戏上报的执行数是0，完美避免了游戏在过渡期去检查影子PC而引发时序错位。

深度1：

![](./attachments/《图灵完备》-1790399531530.png)

深度2：

![](./attachments/《图灵完备》-1790399459997.png)

深度3：

![](./attachments/《图灵完备》-1790399496532.png)

可见调整流水线深度为2时性能最好。

### 快乐乐章

161的延迟，不算最快。

![](./attachments/《图灵完备》-1790384406229.png)

### 尼姆博弈

> 游戏的规则如下
>
> 牌桌上共有 12 张牌，你和对手需要轮流从牌桌上取走纸牌。每个人每次只能取走1 至 3 张纸牌，且不能跳过自己的回合。游戏开始时，你先取牌。取走最后一张牌(鬼牌)的一方失败。你可以随时从输入端读取当前牌桌上剩余的纸牌数量。向输出端发送1~3的数值可以取走对应数量的纸牌。你的对手会在你出手后立刻行动，所以你可以在输出数值后立刻读取输入，来获取对手操作之后的牌桌情况。

小学时我学过，每次取走(剩余纸牌-1) MOD 4即可。

```asm
out 3
readLoop:
in r1
sub r1,r1,1
and r3,r1,3
out r3
jmp readLoop
```

### 千变万化

```asm
const SEED=r1
const TEMP1=r2
const TEMP2=r3
const RES=r4
in r1
generate:
lsr r5, SEED, 13
xor TEMP1, SEED, r5

lsl r5, TEMP1, 17
xor TEMP2,TEMP1, r5

lsr r5, TEMP2, 5
xor RES, TEMP2, r5
out RES
mov SEED, RES
jmp generate
```

### 首字大写

```asm
const POINTER=r4
const STDIN=r1
const STDOUT=r2
mov POINTER, 32
readLoop:
in STDIN
isSpace:
cmp POINTER, 32
mov STDOUT, STDIN
jne Continue
Capitalize:
sub STDOUT, STDIN, 32
Continue:
out STDOUT
mov POINTER, STDIN
jmp readLoop
```

### 美味排行

充当人脑编译器，编译一个最简单的冒泡排序：

```python
def bublesort(l: list[int]) -> list[int]:  # 冒泡排序
    listlen = len(l)
    for i in range(listlen-1,0,-1):
        for j in range(i):
            if l[j] > l[j+1]:
                l[j], l[j+1] = l[j+1], l[j]
    return l

```

```asm
const LEN=16
const i=r2
const j=r1
const val1=r5
const val2=r4
const tmp=r3
const tmp1=r7
const tmp2=r6
const STDIN=r10
ReadLoop:
 in STDIN
 push STDIN
 add j,j,1
 cmp j, LEN
 jl ReadLoop
mov i, LEN
Outer:
 mov j, zr
 sub i, i, 1
 Inner:
  lsl tmp, j, 2
  add tmp, sp, tmp
  load_32 val2, [tmp]
  add tmp, tmp, 4
  load_32 val1, [tmp]
  cmp val1, val2
  jle InnerEnd
  swap:
   mov tmp1, val1
   store_32 [tmp],val2
   sub tmp, tmp, 4
   store_32 [tmp], tmp1
  InnerEnd:
  add j, j, 1
  cmp j, i
  jl Inner
 cmp i, zr
 jg Outer

mov i, 15
Deque:
 const RES=r8
 lsl tmp2, i, 2
 add tmp, tmp2, sp
 load_32 RES, [tmp]
 out RES
 sub i, i, 1
 cmp i, 0
 jge Deque
```

要想使用归并排序等，需要递归函数调用，这将在下一关“汉诺塔”中实现。

### 汉诺塔

汉诺塔是一个著名的数学问题。

```python
def hanoi(disk_nr: int, source: int, dest: int, spare: int) -> None:
 if disk_nr == 0:
  move(source, dest)
 else:
  hanoi(disk_nr-1, source, spare, dest)
  move(source, dest)
  hanoi(disk_nr-1, spare, dest, source)

def move(source: int, dest: int) -> None:
 print(source)
 print(5) # 拿起
 print(dest)
 print(5) # 放下

if "__name__"=="__main__":
 disk_nr = int(input())
 source = int(input())
 dest = int(input())
 spare = int(input())
 hanoi(disk_nr, source, dest, spare)
```

人脑编译：

```asm
const ARG1=r1
const ARG2=r2
const ARG3=r3
const ARG4=r4
const tmp=r8

main:
 in ARG1
 in ARG2
 in ARG3
 in ARG4
 call hanoi
 ret

hanoi:
 cmp ARG1, 0
 jne else
 push ARG1
 push ARG2
 move ARG1, ARG2
 move ARG2, ARG3
 call move
 pop ARG2
 pop ARG1
 ret
 else:
     push tmp
     sub ARG1, ARG1, 1
     push ARG1        ; <--- 添加：保存 n-1
     push ARG3
     push ARG4
     mov tmp, ARG3
     mov ARG3, ARG4
     mov ARG4, tmp
     call hanoi
     pop ARG4
     pop ARG3
     pop ARG1         ; <--- 添加：恢复 n-1
     push ARG1        ; 保存 n-1（用于 move 后恢复）
     push ARG2
     mov ARG1, ARG2
     mov ARG2, ARG3
     call move
     pop ARG2
     pop ARG1         ; 恢复 n-1
     push ARG2
     push ARG3
     push ARG4
     mov tmp, ARG2
     mov ARG2, ARG4
     mov ARG4, tmp
     call hanoi
     pop ARG4
     pop ARG3
     pop ARG2
     pop tmp
     ret

move:
 out ARG1
 out 5
 out Arg2
 out 5
 ret
 
```

### Bugs

时钟周期为0时，计数器已经显示是1，但是输出是0；

![](./attachments/未命名-1790324533548.png)

![](./attachments/未命名-1790324564160.png)

而计数器那一关里面输出跟时钟周期是相等的。

这又是？

![](./attachments/未命名-1790327154039.png)

## 总结

上世纪四十年代，人类制造出了第一台计算机。据说当时的计算机有好几个房间那么大。这次对《图灵完备》的探索，我从与非元件出发，在布尔代数中制作出了一批逻辑元件，在此基础上实现了加法运算。又利用各种电子工业的集线器、存储器，制作出了图灵完备的中央处理器。了解了其中的复杂性之后，我明白了当初大型计算机的体积为什么那么大了，更对如今精密的芯片感到震撼。

这个游戏的自由度还是非常高的。在完善指令集那关中，我明白了指令集和CPU的深度绑定。同时我也在想，能不能对标现实当中使用的指令集呢？比如RISC-V。通关之后，我添加了官方交流QQ群。群友们实力非常强劲，似乎已经制作出了32位RISC-V、还能安装一些MOD。回想起去年暑假我编写的32位RISC-V编译器，我想要是实现这样的CPU和存储，我可以编写C程序在游戏中搭建的计算上运行！这可真是一项壮举啊！

[My Profile](https://turingcomplete.game/profile/60826)

## REFERENCE

1. [《Turing Complete》2.1新版本攻略+全成就](https://zhuanlan.zhihu.com/p/2072268077220341500)
2. [Turing Complete不同的解法](https://zhuanlan.zhihu.com/p/612670567)
