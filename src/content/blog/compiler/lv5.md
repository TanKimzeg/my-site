---
title: Lv5：语句块和作用域 | 编译原理
description: "PKU编译原理实践课程"
pubDate: 2025 08 21 
categories: 
  - tech
tags:
  - compiler
  - rust
---

```ebnf
Stmt ::= LVal "=" Exp ";"
       | [Exp] ";"
       | Block
       | "return" [Exp] ";";
```

本节内容不多,而且在建立符号表的那章我就思考过符号表的建立位置以及语句块和作用域的问题.本以为能很快解决,但没想到在智能指针等细节还是纠缠了很久.

智能指针及其配套方法还是难,好在有Chat-GPT5的帮助,最终还是写出来了.

我重构了符号表的数据结构,用`Rc<RefCell<SymbolTable>>`来减小复制开销.这样,总体来说性能还是不错的.

欣赏一下结果:
```
    Finished release [optimized] target(s) in 29.28s
running test "0_block" ... PASSED
running test "1_ret_from_block" ... PASSED
running test "2_blocks" ... PASSED
running test "3_exp" ... PASSED
running test "4_empty_exp" ... PASSED
running test "5_scope" ... PASSED
running test "6_complex_scopes" ... PASSED
PASSED (7/7)
```

还有一个`koopa IR`的语法细节:如果block里面没有内容,应该是不能给该block命名的:
```
fun @main(): i32 {
%entry:
  ret 1

%0:

%1:

%2:
}
```

这样是不行的.