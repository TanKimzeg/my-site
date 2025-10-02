---
title: "Lv7: while语句 | 编译原理"
description: "PKU编译原理实践课程"
pubDate: 2025 08 23
categories: 
  - tech
tags:
  - compiler
  - rust
---

## 处理while
```ebnf
Stmt ::= ...
       | ...
       | ...
       | ...
       | "while" "(" Exp ")" Stmt
       | ...;
```
设置三个新的`BasicBlock`: `while_entry`/`while_body`/`while_end`


## break和continue
```ebnf
Stmt ::= ...
       | ...
       | ...
       | ...
       | ...
       | "break" ";"
       | "continue" ";"
       | ...;
```

在`break`和`continue`之后,生成一些不可达的块来编译后续代码,防止崩溃,这么做是最省事的.

```
    Finished release [optimized] target(s) in 44.02s
running test "00_while" ... PASSED
running test "01_while_pow" ... PASSED
running test "02_while_false" ... PASSED
running test "03_while_true" ... PASSED
running test "04_while_if" ... PASSED
running test "05_if_while" ... PASSED
running test "06_nested_while" ... PASSED
running test "07_break" ... PASSED
running test "08_if_break" ... PASSED
running test "09_continue" ... PASSED
running test "10_if_continue" ... PASSED
running test "11_complex" ... PASSED
PASSED (12/12)
```

