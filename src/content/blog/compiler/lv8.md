---
title: "Lv8: 函数和全局变量 | 编译原理"
description: "PKU编译原理实践课程"
pubDate: 2025 08 23
categories: 
  - tech
tags:
  - compiler
  - rust
---


本章中, 你将在上一章的基础上, 实现一个能够处理函数 (包括 SysY 库函数) 和全局变量的编译器.

那么,我的编译器将越来越有用!

## 函数定义和调用

```ebnf
CompUnit    ::= [CompUnit] FuncDef;

FuncDef     ::= FuncType IDENT "(" [FuncFParams] ")" Block;
FuncType    ::= "void" | "int";
FuncFParams ::= FuncFParam {"," FuncFParam};
FuncFParam  ::= BType IDENT;

UnaryExp    ::= ...
              | IDENT "(" [FuncRParams] ")"
              | ...;
FuncRParams ::= Exp {"," Exp};
```

重新设计了符号表,由于有多个函数,重构了处理函数的代码,使其能够复用.另外,函数需要将全局符号和参数加入其符号表中.对于参数,需要为其分配存储空间

## 目标代码生成
还记得在汇编语言中:
- 如何定义函数?
- 如何调用函数
- 如何传递/接受函数参数
- 如何传递/接受返回值,以及从函数中返回?

这应该是本章最复杂的部分了.

### 函数的调用和返回
与CS:APP相比,这里要求的掌握程度就更高了.

1. 在汇编层面, “函数调用和返回” 并不包括参数和返回值的传递.
2. 函数的返回地址保存在寄存器 `ra` 中.

把函数之间的调用关系想象成一个图 (即调用图), 那么一个永远不会调用其他函数的函数就位于图中的叶子结点, 我们把这种函数称为叶子函数.与之相对的, 还有非叶子函数.

在 RISC-V 中, 非叶子函数通常需要在 prologue 中将自己的 `ra` 寄存器保存到栈帧中. 在 epilogue 中, 非叶子函数需要先从栈帧中恢复 `ra` 寄存器, 之后才能执行 `ret` 指令.

### 传递/接受参数
RISC-V有8个寄存器: `a0` - `a7` 用来在函数调用时传递函数的非浮点参数.函数的前8个参数必须按照从前到后的顺序依次放入 `a0` 到 `a7` 寄存器.

如果函数参数超过8个,超过的部分放在内存(栈帧)中.而且是从栈帧的最底部开始(`sp+0`,`sp+4`)开始.

## SysY库函数
在 Koopa IR 中, 所有被 `call` 指令引用的函数必须提前声明, 否则会出现错误. 你可以使用 `decl` 语句来预先声明所有的库函数.

我们需要用`FuncData::new(..)`来声明函数.
此外,在全局符号表中加入这些函数的声明.

## 全局变量和常量
```ebnf
CompUnit ::= [CompUnit] (Decl | FuncDef);
```
修改lexer时遇到了莫名其妙的问题:
```
CompUnit: CompUnit = {
  Decl => CompUnit::Decl(<>),
  FuncDef => CompUnit::Func(<>),
};
```

```
the top 1 token(s) from the stack and produce a `BType`. This might then yield a parse  
tree like  
"int" ╷ Comma<VarDef> ";"  
├─BType─┘ │  
└─VarDecl─────────────────┘

Alternatively, the parser could execute the production at  
E:\Documents\learnRust\compiler\src\sysy.lalrpop:34:3: 34:26, which would consume the  
top 1 token(s) from the stack and produce a `FuncType`. This might then yield a parse  
tree like  
"int" ╷ Ident "(" Comma<FuncFParam> ")" Block  
├─FuncType─┘ │  
└─FuncDef────────────────────────────────────────┘

See the LALRPOP manual for advice on making your grammar LR(1).
```

这paser不太智能啊,`Decl`后面没有括号,这也区分不了吗?


### 目标代码生成
RISC-V如何存取全局变量?借助 https://godbolt.org/ RISC-V rv32gc clang(trunck)我发现
```nasm
main:
        lui     a1, %hi(x)
        lw      a0, %lo(x)(a1)
        addi    a0, a0, 1
        sw      a0, %lo(x)(a1)
        ret
  
a:
        .word   2

x:
        .word   0
```
这就是存取全局变量的方法的,先获取变量的地址,再向地址写.当然也可以这样:
```nasm
la t0, var 
lw t0, 0(t0) 
sw t0, 0(sp)
```


```
    Finished release [optimized] target(s) in 21.30s
running test "00_int_func" ... PASSED
running test "01_void_func" ... PASSED
running test "02_params" ... PASSED
running test "03_more_params" ... PASSED
running test "04_param_name" ... PASSED
running test "05_func_name" ... PASSED
running test "06_complex_call" ... PASSED
running test "07_recursion" ... PASSED
running test "08_lib_funcs" ... PASSED
running test "09_globals" ... PASSED
running test "10_complex" ... PASSED
running test "11_short_circuit" ... PASSED
PASSED (12/12)
```

Lv9之前的测试全部通过，已经看到胜利的曙光了!