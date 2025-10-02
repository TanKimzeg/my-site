---
title: Lv2：目标代码生成 | 编译原理
description: "PKU编译原理实践课程"
pubDate: 2025 08 14
categories: 
  - tech
tags:
  - compiler
  - rust
---

MaxXing非常贴心,不只是Rust使用者有接口, C系也有.作者为此课程真是呕心沥血了,十分敬重.

 [Compiler Explorer](https://godbolt.org/)你可以在网站右侧的汇编输出窗口选择使用 “RISC-V rv32gc clang (trunk)” 编译器, 然后将编译选项设置为 `-O3 -g0`, 并查看窗口内的汇编输出.

  [RISC-V 指令速查](https://pku-minic.github.io/online-doc/#/misc-app-ref/riscv-insts)

对于只有`return <ret_val>;`的函数,我们只需要解析`program`的返回值,生成这样的汇编:
```nasm
	.text
	.globl main
main:
	li a0, 0
	ret
```

测试文件在 `/opt/testcase` 里面.

> 一开始我把a0寄存器写成s0了,找了很久的bug😭

```
    Finished release [optimized] target(s) in 25.17s
running test "0_main" ... PASSED
running test "1_comments" ... PASSED
running test "2_int_dec" ... PASSED
running test "3_int_oct" ... PASSED
running test "4_int_hex" ... PASSED
running test "5_compact" ... PASSED
running test "6_whitespaces" ... PASSED
PASSED (7/7)
```

我顺便重构了一下代码,轻松通过了!