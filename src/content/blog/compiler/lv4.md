---
title: Lv4：常量和变量 | 编译原理
description: "PKU编译原理实践课程"
pubDate: 2025 08 19 
categories: 
  - tech
tags:
  - compiler
  - rust
---


进入第4章节, 
编译器将可以处理如下的 SysY 程序:

```c
int main() {
  const int x = 233 * 4;
  int y = 10;
  y = y + x / 2;
  return y;
}
```

教程给出了ebnf: 

```ebnf
CompUnit      ::= FuncDef;

Decl          ::= ConstDecl | VarDecl;
ConstDecl     ::= "const" BType ConstDef {"," ConstDef} ";";
BType         ::= "int";
ConstDef      ::= IDENT "=" ConstInitVal;
ConstInitVal  ::= ConstExp;
VarDecl       ::= BType VarDef {"," VarDef} ";";
VarDef        ::= IDENT | IDENT "=" InitVal;
InitVal       ::= Exp;

FuncDef       ::= FuncType IDENT "(" ")" Block;
FuncType      ::= "int";

Block         ::= "{" {BlockItem} "}";
BlockItem     ::= Decl | Stmt;
Stmt          ::= LVal "=" Exp ";"
                | "return" Exp ";";

Exp           ::= LOrExp;
LVal          ::= IDENT;
PrimaryExp    ::= "(" Exp ")" | LVal | Number;
Number        ::= INT_CONST;
UnaryExp      ::= PrimaryExp | UnaryOp UnaryExp;
UnaryOp       ::= "+" | "-" | "!";
MulExp        ::= UnaryExp | MulExp ("*" | "/" | "%") UnaryExp;
AddExp        ::= MulExp | AddExp ("+" | "-") MulExp;
RelExp        ::= AddExp | RelExp ("<" | ">" | "<=" | ">=") AddExp;
EqExp         ::= RelExp | EqExp ("==" | "!=") RelExp;
LAndExp       ::= EqExp | LAndExp "&&" EqExp;
LOrExp        ::= LAndExp | LOrExp "||" LAndExp;
ConstExp      ::= Exp;
```

差点晕😴...又是一个大工程...

我梳理一下: 这回增加了常量和变量的声明(Decl)

## 常量
循序渐进,先来看常量

```ebnf
Decl          ::= ConstDecl;
ConstDecl     ::= "const" BType ConstDef {"," ConstDef} ";";
BType         ::= "int";
ConstDef      ::= IDENT "=" ConstInitVal;
ConstInitVal  ::= ConstExp;

Block         ::= "{" {BlockItem} "}";
BlockItem     ::= Decl | Stmt;

LVal          ::= IDENT;
PrimaryExp    ::= "(" Exp ")" | LVal | Number;

ConstExp      ::= Exp;
```

### 词法/语法分析
本节的 EBNF 中出现了一种新的表示: `{ ... }`, 这代表花括号内包含的项可被重复 0 次或多次.


为了解析`{ }` 表示的数组,我查阅了[lalrpop的手册](https://lalrpop.github.io/lalrpop/tutorial/index.html),以及一些[示例](https://github.com/lalrpop/lalrpop/blob/master/lalrpop/src/parser/lrgrammar.lalrpop), 得知可以使用 \* 或? 来匹配


但是
```ebnf
ConstDecl     ::= "const" BType ConstDef {"," ConstDef} ";";
```
怎么解析?我在示例中找到了:

```
Plus<T>: Vec<T> = {
    <mut v:(<T> "+")*> <e:T?> => match e {
        None => v,
        Some(e) => { v.push(e); v }
    }
};
```
以及
https://github.com/lalrpop/lalrpop/blob/master/doc/calculator/src/calculator6.lalrpop 出现了
```
pub Exprs = Comma<Expr>;

Comma<T>: Vec<T> = { // (0)
    <v:(<T> ",")*> <e:T?> => match e { // (1)
        None=> v,
        Some(e) => {
            let mut v = v;
            v.push(e);
            v
        }
    }
};
```
照猫画虎即可.

### 句法分析
我需要在抽象语法树中引入**符号表** .

> 具体来说, 符号表需要支持如下操作:
> - **插入符号定义:** 向符号表中添加一个常量符号, 同时记录这个符号的常量值, 也就是一个 32 位整数.
> - **确认符号定义是否存在:** 给定一个符号, 查询符号表中是否存在这个符号的定义.
> - **查询符号定义:** 给定一个符号表中已经存在的符号, 返回这个符号对应的常量值.
> 在遇到常量声明语句时, 你应该遍历 AST, 直接算出语句右侧的 `ConstExp` 的值, 得到一个 32 位整数, 然后把这个常量定义插入到符号表中.
> 在遇到 `LVal` 时, 你应该从符号表中查询这个符号的值, 然后用查到的结果作为常量求值/IR 生成的结果. 如果没查到, 说明 SysY 程序出现了语义错误, 也就是程序里使用了未定义的常量.

那么, 我上一章节写的表达式在编译期间执行求值的代码就可以派上用场了!

在执行表达式求值时,需要将符号表传进去,于是我重构了代码.

## 变量和赋值
```ebnf
Decl          ::= ConstDecl | VarDecl;
ConstDecl     ::= ...;
BType         ::= ...;
ConstDef      ::= ...;
ConstInitVal  ::= ...;
VarDecl       ::= BType VarDef {"," VarDef} ";";
VarDef        ::= IDENT | IDENT "=" InitVal;
InitVal       ::= Exp;

...

Block         ::= ...;
BlockItem     ::= ...;
Stmt          ::= LVal "=" Exp ";"
                | "return" Exp ";";
```

变量与常量要分开处理.在遇到 `LVal` 时, 你需要从符号表中查询这个符号的信息, 然后用查到的结果作为常量求值/IR 生成的结果. 注意, 如下情况属于语义错误:

- 在进行常量求值时, 从符号表里查询到了变量而不是常量.
- 在处理赋值语句时, 赋值语句左侧的 `LVal` 对应一个常量, 而不是变量.
- 其他情况, 如符号重复定义, 或者符号未定义.

对于常量的定义我们直接求值,而对于变量的定义,我们必须引入三种新的指令: `alloc`, `load` 和 `store`:

### IR生成
对于`alloc`,有相应的接口:
```rust
let new_var = func_data.dfg_mut().new_value() .alloc(Type::get_i32());
let store = func_data.dfg_mut().new_value().store(val, new_var);
let load = func_data.dfg_mut().new_value().load(var_info.dest);
```

这并没有出现的koopa ir文档的示例方法里面.不过可以猜到.

更新AST后,针对koopa的测试一下子就通过了:
```
    Finished release [optimized] target(s) in 39.88s
running test "00_const" ... PASSED
running test "01_const_expr" ... PASSED
running test "02_multiple_consts" ... PASSED
running test "03_complex_const" ... PASSED
running test "04_var" ... PASSED
running test "05_var_init" ... PASSED
running test "06_var_expr" ... PASSED
running test "07_var_main" ... PASSED
running test "08_multiple_vars" ... PASSED
running test "09_complex_vars" ... PASSED
running test "10_assign" ... PASSED
running test "11_assign_read" ... PASSED
running test "12_multiple_assigns" ... PASSED
running test "13_complex" ... PASSED
PASSED (14/14)
```

### 目标代码生成
这是本节的理论难点了,需要具备操作系统内核的基础知识:栈帧.不过这并不能难倒我,因为我学过CS:APP.

> 另外本节还介绍了`call` `ret`伪指令相应的RISC-V真实汇编代码的原理,我仅是粗略看了一眼.


在IR生成中,本节没有充分利用寄存器,而是将每个运算结果都存储在内存(具体来说是栈帧)中,因此对应着汇编语言的栈指针操作.

按照文档给出的步骤,首先我需要扫描一遍函数中的所有指令,计算出所需栈空间,将栈顶指针sp退栈. `i32`占据4字节,但RISC-V要求16字节(double word)对齐(在CS:APP的alloclab中,x86也有类似的要求).

还需要一个变量来统计使用的情况,产生一个i32值,这个变量就加上4,最后用完刚好栈满.

`lw`和`sw`对应load和store.

最后,随着`ret`栈顶指针sp加回去.

之前我的代码是以`ret`语句为导向DFS展开,但现在不行了,只能遍历所有实例.经过长达一天的重构折磨,也参考了一下别人的代码(https://github.com/AsdOkuu/Compiler-25-Spring/commit/2f2cb9b92aaf15be984fb41160c698965e2dd90c)别人的代码写得太屎山了,不过思路是对的.我只好将我之前的寄存器分配删去.

我注意到`koopa::ir`中的`Value`具有`Hash`特型,而每条语句都有自己的`Value`,所以用`HashMap<Value,u32>`来存取它们的位置,从而实现`load`和`store`.重构的过程是痛苦的.

另一个设计是用一个`Context`结构体存储函数的上下文信息:
```rust
struct Context<'a> {
  pub func_data: &'a FunctionData,
  pub offset: HashMap<Value, u32>,
  pub stack_size: u32,
  pub inst: Option<Value>,
}
```
使得对`values::*`的trait实现时传参比较方便.

```
    Finished release [optimized] target(s) in 19.75s
running test "00_const" ... PASSED
running test "01_const_expr" ... PASSED
running test "02_multiple_consts" ... PASSED
running test "03_complex_const" ... PASSED
running test "04_var" ... PASSED
running test "05_var_init" ... PASSED
running test "06_var_expr" ... PASSED
running test "07_var_main" ... PASSED
running test "08_multiple_vars" ... PASSED
running test "09_complex_vars" ... PASSED
running test "10_assign" ... PASSED
running test "11_assign_read" ... PASSED
running test "12_multiple_assigns" ... PASSED
running test "13_complex" ... PASSED
PASSED (14/14)
```

至此,作用域和语句块也呼之欲出了.
