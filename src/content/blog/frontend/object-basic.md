---
title: 对象(Object)基础知识 | 现代JavaScript
description: Object这一章的简单笔记
pubDate: 2025 10 05
categories:
  - tech
tags:
  - javascript
---

# 对象

## 创建对象

```js
let user = new Object();
let user = {};
```

对象的属性可以在创建时定义,也可以稍后定义.

```js
user.name = "John";
user.age = 20;
```

属性可以删除:

```js
delete user.age;
```

多字词语作为属性名必须加引号
,同时,访问多次属性用方括号:

```js
user["is admin"] = true;
```

### 计算属性

```js
let fruit = prompt("Which fruit?", "apple")
let bag = {
 [fruit] = 5,
};
```

相当于

```js
let fruit = prompt("Which fruit?", "apple");
let bag = {};

bag[fruit] = 5;
```

方括号中使用更复杂的表达式,这就是叫做"计算"的原因

```js
let bag = {
 [fruit + "Computers]: 5,
};
```

跟Rust 一样,如果变量跟属性名一样,可以简写.

## 属性存在 `in` 操作符

检查属性是否存在

```js
"key" in object;
```

## 通过 `for..in`遍历对象的所有键

属性的排序: 整数属性升序排序, 其他按照创建的顺序排序.

经过

```js
String(Math.trunc(Number("49")));
```

后与原字符串相同的就是整数属性.
而

```js
String(Math.trunc(Number("+49")));
String(Math.trunc(Number("1.2")));
```

就不是整数属性

## 对象引用和复制

跟很多编程语言一样,原始类型的复制是完全的复制,而对象的复制时复制了引用的指针.这一点对于已经接触过不少现代编程语言的我们来说不难理解.

引用同一个对象,则它们"相等"(`a === b`),不同对象,则不相等.这跟Python中的 `is` 一样.在Rust中,我们需要自己实现判等的trait,才能使用 `==` 运算符.

通过 `Object.assign` 方法来实现克隆:

```js
Object.assign(dist, [src1, scr2, ...]);
```

将所有源对象的属性拷贝到目标对象 `dist` 中.可以用来合并多个对象.

为了进行深拷贝,必须递归复制.采用现有的实现,比如 `lodash` 库的 `.cloneDeep(obj)`.

# 垃圾回收

垃圾回收机制是不少现代编程语言具备的内存管理机制,它的根本原理是什么呢?这一章做了解释.

## 可达性(Reachability)

"可达"的值

1. 根(Root)

- 当前执行的函数,其局部变量和参数.
- 嵌套调用链上的其他函数,它们的局部变量和参数
- 全局变量
- 其他内部实现??

1. 如果一个值可以从根通过引用或者引用链进行访问, 则该值也是可达的

执行引擎中有一个 **垃圾回收器**, 监督所有对象的状态,删除已经不可达的.

## 内部算法

垃圾回收的基本算法被称为 "mark-and-sweep". 其实就是从"根"出发进行遍历搜索.搜索到就标记一下,没有标记的就是不可达,直接清除.

垃圾回收器定期执行.

垃圾回收器运行速度要快,也不能让人对代码执行感到延迟.为此有一些优化: 分代收集,增量收集, 闲时收集.

当我熟悉了这门语言之后, 把熟悉引擎作为下一步计划吧!就从垃圾回收算法开始.

# 对象方法

作为对象属性的函数就是该对象的方法.

为了定义方法,可以使用预先定义的函数,也可以直接在对象里面定义:

```js
let user = {
  name: "John",
  age: 30,

  say() {
    alert(this.name);
  },
};
```

`this`, 就相当于其他语言的 `self`

# 构造器

为了创建很多类似的对象,使用构造函数和 `new` 来实现

## 构造函数

1. 以大写字母开头
2. 用new操作符来执行

当一个函数使用new 操作符执行时,它按照以下步骤执行:

1. 一个新的空对象创建并分配给 `this`
2. 函数体执行,添加新的属性
3. 返回 `this` 的值

## 构造器的 `return`

如果构造器的return 语句返回一个对象就会返回这个对象覆盖this.

# 可选链

在前端的业务逻辑处理过程中,我们经常遇到这样的问题,需要访问对象链条的元素.如果到某一个对象是null 或 undefine, 继续访问就会出错.

```js
alert(user.address && user.address.street && user.address.street.name);
```

这样可以解决,但是重复度太高了.可选链 `?.` 就是为了解决这个问题的.

```js
alert(user?.address?.street);
```

如果 `value` 是 `null` 或 `undefined`, `value.prop` 返回 `undefined`.

跟 && 运算符一样, 有短路效应.

## 其他变体

`?.()` 用于调用一个可能不存在的函数

`?.[]` 也可以访问属性.

# symbol类型

只有两种原始类型可作为对象属性的键: 字符串类型和symbol类型

"symbol"表示唯一的标识符.可以使用Symbol来创建这种类型的值:

```js
let id = Symbol("Here is id");
```

即使创建了许多具有相同描述的symbol.它们也是不同的.

symbol不会自动转换为字符串.可以通过 `toString()` 方法转换.获取 `.description` 属性获取描述.

## 隐藏属性

可以用来创建私有属性,代码的其他部分不能随意访问或重写这些属性.

```js
let user = {
  name: "John",
};

let id = Symbol("id");
user[id] = 1;
alert(user[id]);
```

第三方代码不能知道这里定义的id,所以无法访问.它们也可以定义自己的id,但是不冲突

### symbol在 `for..in` 中会被跳过

而 `Object.assign` 会同时复制字符串和symbol属性

## 全局 symbol

在 **全局symbol注册表**中创建的symbol,每次访问相同名字的symbol时,返回都是相同的symbol

```js
let id = Symbol.for("id"); // 不存在则创建

let idAgain = Symbol.for("id"); // 读取

alert(id === idAgain); // true
```

### `Symbol.keyfor`

对于全局 symbol, `Symbol.for(key)` 按名字返回一个 symbol. 相反,使用 `Symbol.keyfor(sym)` 返回一个名字.

如果找不到返回 `undefined`.

# 对象原始值转换

## hint

类型转换被称为遵循"hint"

### string

期望对字符串执行操作时,hint就是 string.

如 `alert`

### number

数学运算,对象到数字的转换

### default

不确定的类型期望值

为了进行类型转换, 执行引擎查找并调用三个对象方法:

1. 调用 `obj[Symbol.toPrimitive](hint)`,如果存在
2. 否则,如果hint是string,尝试调用 `obj.toString()`或 `obj.valueOf()`,
3. 否则,如果hint是 `number` 或 `default` ,尝试调用 `obj.valueOf()` 或 `obj.toString()`.

## `Symbol.toPrimitive`

这是一个内建 symbol, 用来自定义转换方法.

```js
let user = {
  name: "John",
  money: 1000,
  [Symbol.toPrimitive](hint) {
    alert(`hint: ${hint}`);
    return hint == "string" ? `{name: "${this.name}"` : this.money;
    // 自定义的实现
  }
};
```

## `toString` / `valueOf`

如果没有以上, 将尝试寻找这两个方法

默认情况下,普通对象具有这两个方法:

- `toString` 方法返回一个字符串 "[object Object]".
- `valueOf` 方法返回对象自身.

我们自己实现这些方法来自定义转换

```js
let user = {
name: "John",
money: 1000,

toString() {
 return `{name: "${this.name}"`;
 // 自定义实现
},

valueOf() }
 return this.money;
}
```

转换可以返回任何原始类型(返回对象这个方法会被忽略), 不受 hint 的原始值限制了. `[Symbol.toPrimitive]`返回对象会触发错误
