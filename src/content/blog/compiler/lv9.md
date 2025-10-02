---
title: "Lv9：数组 | 编译原理"
description: PKU编译原理实践课程
pubDate: 2025 08 26 
categories: 
  - tech
tags:
  - compiler
  - rust
---

按照我自己的写法的sysy.lalrpop总是出各种问题,匪夷所思.最后是在没招了,我只好参考了示例编译器的lalrpop写法,这才解决问题.顺便一提,示例编译器的rust写法非常抽象,我都看不太懂.我对自己的代码风格还是很满意的,既有一定的抽象,又清晰可读.别的学生的代码已经变成屎山了,中后期对我找bug的参考意义就不大了.

> 由于经常要测试,不管是手敲命令还是上下翻找都不方便.所以我向`bashrc`添加命令别名(alias),很好用:

```shell
echo 'alias test-koopa="cargo run -- -koopa /root/compiler/tests/hello.c -o /root/compiler/tests/hello.koopa"'>> ~/.bash_aliases
echo 'alias test-riscv="cargo run -- -riscv /root/compiler/tests/hello.c -o /root/compiler/tests/hello.S"'  >> ~/.bash_aliases

echo 'chapter_test(){ autotest -$1 -s lv$2 /root/compiler; }' >> ~/.bash_aliases
```

这章各种指针乱飞,是最让我头大的.经常出现指针越界的问题(返回值显示-11),Debug了很久,而且懒得自己链接调试,用的是`putint`库函数打印调试....最后硬是靠着二分法看着汇编找到了一些寄存器分配/函数参数的冲突问题.后续,我搞了一个Makefile来编译链接,推荐大家使用,减少编译等待的时间,我的电脑比较差劲,每次autotest都得等二十多秒.


```
running test "00_local_arr_1d" ... PASSED
running test "01_local_arr_nd" ... PASSED
running test "02_global_arr" ... PASSED
running test "03_arr_init_1d" ... PASSED
running test "04_arr_init_nd" ... PASSED
running test "05_global_arr_init" ... PASSED
running test "06_long_array" ... PASSED
running test "07_const_array" ... PASSED
running test "08_arr_access" ... PASSED
running test "09_const_arr_read" ... PASSED
running test "10_arr_in_loop" ... PASSED
running test "11_arr_params" ... PASSED
running test "12_more_arr_params" ... PASSED
running test "13_complex_arr_params" ... PASSED
running test "14_arr_lib_funcs" ... PASSED
running test "15_sort1" ... PASSED
running test "16_sort2" ... PASSED
running test "17_sort3" ... PASSED
running test "18_sort4" ... PASSED
running test "19_sort5" ... PASSED
running test "20_sort6" ... PASSED
running test "21_sort7" ... PASSED
PASSED (22/22)
```
终于通过了,真是不容易.虽然这里通过了,但在此基础上,我还修了几个bug.