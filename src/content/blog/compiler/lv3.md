---
title: Lv3：表达式 | 编译原理
description: "PKU编译原理实践课程"
pubDate: 2025 08 15
categories: 
  - tech
tags:
  - compiler
  - rust
---

这章将处理这样的像C语言里面一样行为的表达式:

```c
int main() { return 1 + 2 * -3; }
```

## 一元表达式
```ebnf
Stmt        ::= "return" Exp ";";

Exp         ::= UnaryExp;
PrimaryExp  ::= "(" Exp ")" | Number;
Number      ::= INT_CONST;
UnaryExp    ::= PrimaryExp | UnaryOp UnaryExp;
UnaryOp     ::= "+" | "-" | "!";
```

我目前的实践方式是直接捕捉表达式执行求值, 这其实算是一种编译优化了.如果忠于源码,则要逐句翻译,略显繁琐.在以后的课程中绕不开的.我需要重新组织代码,为每个Exp语句实现`compile`方法,进而最后为`ir::Program`实现`compile`方法,例如这位的代码🤣:

https://github.com/AsdOkuu/Compiler-25-Spring/commit/7c50d8f5ee37380018313b3ae43fbdbcefc5dfa6

这天(8.17),我在保留执行表达式的函数的同时, 另外重构了代码, 逐句翻译了源代码.

## 算术表达式
来到算术表达式, 我依旧按照 ~~enfp~~ ebnf 的框架和命名去拓展ast. 有了 一元表达式 的经历, 简单的拓展不是问题.

## 比较和逻辑表达式

```ebnf
Exp         ::= LOrExp;
PrimaryExp  ::= ...;
Number      ::= ...;
UnaryExp    ::= ...;
UnaryOp     ::= ...;
MulExp      ::= ...;
AddExp      ::= ...;
RelExp      ::= AddExp | RelExp ("<" | ">" | "<=" | ">=") AddExp;
EqExp       ::= RelExp | EqExp ("==" | "!=") RelExp;
LAndExp     ::= EqExp | LAndExp "&&" EqExp;
LOrExp      ::= LAndExp | LOrExp "||" LAndExp;
```

可以看到, 小类的`Exp`还是表现出这样的两种结构.于是我忽然灵机一动, 重构为相同的框架: `Single` 和 `Binary`.

`Binary` 接收泛型, 泛型需绑定 `Compile` trait. 至此豁然开朗!简化了大量`match` 逻辑的代码!这就是在Rust中实现其他编程语言中继承的技巧.

运行测试:
```shell
autotest -koopa -s lv3 /root/compiler/
```

发现
```
...
running test "23_lor" ... WRONG ANSWER
your answer:
11
running test "24_land" ... WRONG ANSWER
your answer:
0
running test "25_int_min" ... PASSED
running test "26_parentheses" ... PASSED
running test "27_complex_binary" ... PASSED
WRONG ANSWER (26/28)
```

23 和 24 测试样例是什么情况?
```c
// /opt/bin/testcases/lv3/23_lor.c
int main() {
  return 11 || 0;
}
```

```c
// /opt/bin/testcases/lv3/24_land.c
int main() {
  return 2 && 4;
}
```
原来`Binary::Or`是按位或; `Binary::And`是按位与.

如果要复现短路特性的话, 必须要在编译时执行表达式,根据结果判断. 目前, 虽然我之前有写了一点点表达式的执行函数, 但已经失修,应放到后面编译优化环节专门实现.

所以我逐句执行判断逻辑.

```
    Finished release [optimized] target(s) in 19.54s
running test "00_pos" ... PASSED
running test "01_neg_0" ... PASSED
running test "02_neg_2" ... PASSED
running test "03_neg_max" ... PASSED
running test "04_not_0" ... PASSED
running test "05_not_10" ... PASSED
running test "06_complex_unary" ... PASSED
running test "07_add" ... PASSED
running test "08_add_neg" ... PASSED
running test "09_sub" ... PASSED
running test "10_sub_neg" ... PASSED
running test "11_mul" ... PASSED
running test "12_mul_neg" ... PASSED
running test "13_div" ... PASSED
running test "14_div_neg" ... PASSED
running test "15_mod" ... PASSED
running test "16_mod_neg" ... PASSED
running test "17_lt" ... PASSED
running test "18_gt" ... PASSED
running test "19_le" ... PASSED
running test "20_ge" ... PASSED
running test "21_eq" ... PASSED
running test "22_ne" ... PASSED
running test "23_lor" ... PASSED
running test "24_land" ... PASSED
running test "25_int_min" ... PASSED
running test "26_parentheses" ... PASSED
running test "27_complex_binary" ... PASSED
PASSED (28/28)
```

至此, Lv3 全部通过!