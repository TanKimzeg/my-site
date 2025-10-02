---
title: Lv6：if语句 | 编译原理
description: "PKU编译原理实践课程"
pubDate: 2025 08 21 
categories: 
  - tech
tags:
  - compiler
  - rust
---

按照
```ebnf
Stmt ::= ...
       | ...
       | ...
       | "if" "(" Exp ")" Stmt ["else" Stmt]
       | ...;
```
遇到一些语法二义性导致的问题：

```

    The following symbols can be reduced in two ways:
      "if" "(" Exp ")" "if" "(" Exp ")" Stmt "else" Stmt

    They could be reduced like so:
      "if" "(" Exp ")" "if" "(" Exp ")" Stmt "else" Stmt
      │                └─Stmt──────────────┘           │
      └─Stmt───────────────────────────────────────────┘

    Alternatively, they could be reduced like so:
      "if" "(" Exp ")" "if" "(" Exp ")" Stmt "else" Stmt
      │                └─Stmt──────────────────────────┤
      └─Stmt───────────────────────────────────────────┘

    LALRPOP does not yet support ambiguous grammars. See the LALRPOP manual for
    advice on making your grammar unambiguous.
```

我想不出怎么解决,只好求助AI:
原因与设计思路

- 定义不变式
    
    - MatchedStmt：内部不再存在“悬空的 if”（即没有任何分支末尾还缺 else）。
    - UnmatchedStmt：以一个“悬空的 if”收尾，右端还可能被后续 else 吸收。
- 为什么在“把 else 绑定到最近未匹配 if”的产生式里写 UnmatchedStmt -> if (E) MatchedStmt else UnmatchedStmt
    
    - then_m 必须是 MatchedStmt：这样保证 then 分支内部不再携带悬空 if，避免 else 去抢绑定 then 分支里更早的 if，确保“else 只能往右绑定最近的未匹配 if”。
    - else_u 是 UnmatchedStmt：把“悬空”状态继续向右传播。如果 else 分支自身以悬空 if 结尾，那么整个 if 仍然是 Unmatched，留给更靠右的 else 去匹配；如果 else 分支是 Matched，则下一步可整体归约为 Matched 的 if-else。

```
// ...existing code...
Stmt: Stmt = {
  MatchedStmt => <>,
  UnmatchedStmt => <>,
};

MatchedStmt: Stmt = {
  // if-else，then/else 两边都“已匹配”
  "if" "(" <exp: Exp> ")" <then_m: MatchedStmt> "else" <else_m: MatchedStmt> =>
    Stmt::Cond(Cond{ exp, then_branch: Box::new(then_m), else_branch: Some(Box::new(else_m)) }),

  // 其它“非 if 缺 else”的语句都属于已匹配
  "return" <exp: Exp?> ";" => Stmt::Ret(<>),
  <id: Ident> "=" <exp: Exp> ";" => Stmt::LVal(<>),
  Block => Stmt::Block(<>),
  <exp: Exp?> ";" => Stmt::Exp(<>),
};

UnmatchedStmt: Stmt = {
  // 缺少 else 的 if
  "if" "(" <exp: Exp> ")" <then_s: Stmt> =>
    Stmt::Cond(Cond{ exp, then_branch: Box::new(then_s), else_branch: None }),

  // 把 else 绑定到最近的未匹配 if
  "if" "(" <exp: Exp> ")" <then_m: MatchedStmt> "else" <else_u: UnmatchedStmt> =>
    Stmt::Cond(Cond{ exp, then_branch: Box::new(then_m), else_branch: Some(Box::new(else_u)) }),
};
// ...existing code...
```

那么可以进入下一步了
### IR生成
Koopa IR 中, 控制转移指令有两种:

1. **`br 条件, 目标1, 目标2` 指令:** 进行条件分支, 其中 `条件` 为整数, 两个目标为基本块. 如果 `条件` 非 0, 则跳转到 `目标1` 基本块的开头执行, 否则跳转到 `目标2`.
2. **`jump 目标` 指令:** 进行无条件跳转, 其中 `目标` 为基本块. 直接跳转到 `目标` 基本块的开头执行.

在之前的 Koopa IR 程序中, 只有一个入口基本块 `%entry`. 现在, 你可以通过划分新的基本块, 来标记控制流转移的目标.

需要注意的是, 基本块的结尾必须是 `br`, `jump` 或 `ret` 指令其中之一 (并且, 这些指令只能出现在基本块的结尾).这也是上次空块编译失败的原因.这点和汇编语言中 label 的概念有所不同.

所以,这里就需要想清楚了,如果if的stmt里面嵌套if分支,对应的koopa  ir  需要展开,jump语句就不能放在第一层分支里面,而要放在最后一层分支下面.遍历时,要求函数返回遍历完成时所在的`BasicBlock`,才能解决这个问题.

另一个细节是为了避免在`ret`后面加上跳转语句,遇到`Stmt::Ret`时新增一个不可达的`Basickblock`,跳转语句放在这个不可达的bb下面就能保持这一主体逻辑不被破坏.

```
    Finished release [optimized] target(s) in 19.21s
running test "0_if" ... PASSED
running test "1_if_else" ... PASSED
running test "2_multiple_if_else" ... PASSED
running test "3_nested_if" ... PASSED
running test "4_logical" ... PASSED
running test "5_more_logical" ... PASSED
running test "6_multiple_returns" ... PASSED
running test "7_complex" ... PASSED
PASSED (8/8)
```

### 目标代码生成

1. **`bnez 寄存器, 目标`:** 判断 `寄存器` 的值, 如果不为 0, 则跳转到目标, 否则继续执行下一条指令.
2. **`j 目标`:** 无条件跳转到 `目标`.


又被折磨了很久...已经懒得写了...


```
    Finished release [optimized] target(s) in 23.68s
running test "0_if" ... PASSED
running test "1_if_else" ... PASSED
running test "2_multiple_if_else" ... PASSED
running test "3_nested_if" ... PASSED
running test "4_logical" ... PASSED
running test "5_more_logical" ... PASSED
running test "6_multiple_returns" ... PASSED
running test "7_complex" ... PASSED
PASSED (8/8)
```