---
title: 数据类型 | 现代JavaScript
description: 数据类型这一章的简单笔记
pubDate: 2025 10 09
categories:
  - tech
tags:
  - javascript
---

## Number类型

数字可以用下划线作为分隔符，这跟其他语言一样。

十六进制(`0x`)，二进制(`0b`)和八进制(`0o`)数字的表示方法跟其他语言也一样。

### `toString(base)` 方法

返回在给定base进制数下数字的字符串表示形式:

```js
let num = 255;
alert(num.toString(16));
alert(123456.0.toString(36));
```

最高支持36进制

### 舍入

`Math.floor()`

`Math.ceil()`

`Math.round()`, 四舍五入

`Math.trunc()` 移除小数点后所有内容

与其他语言一样,浮点数的相等判断应使用舍入.

### `isFinite` 和 `isNaN`

`NaN`不等于任何东西,包括它自身.所以必须使用这个方法

```js
alert(Number.NaN === Number.NaN); // 离谱. 使用了eslint后会提示改用isNaN判断
```

`isFinite()`将其参数转换为数字,如果是常规数字而不是 `NaN/Inf/-Inf`, 则返回 `true`.

在所有数字函数中，包括 `isFinite`，空字符串或仅有空格的字符串均被视为 `0`。

`Object.is()`也可以进行比较: 适用于 `NaN`, 但0和-0不同.

### `parseInt` 和 `parseFloat`

使用加号 `+` 或 `Number()` 的数字转换是严格的。如果一个值不完全是一个数字，就会失败

而这两个函数从字符串中读取数字,直到无法读取为止,返回收集到的数字.

没有数字可读返回 `NaN`.

`parseInt()` 函数具有可选的第二个参数。它指定了数字系统的基数，因此 `parseInt` 还可以解析十六进制数字、二进制数字等的字符串.

### 其他数学函数

内建的 Math对象有一些数学函数和常量.

## BigInt类型

在 JavaScript 中，“number” 类型无法安全地表示大于 `(2^53-1)`（即 `9007199254740991`），或小于 `-(2^53-1)` 的整数。

BigInt类型是新加类型.可以通过将 `n` 附加到整数字段的末尾来创建 `BigInt` 值。

## String类型

在js中可以有三种包含字符串的方式:

- 双引号: `"Hello"`
- 单引号: `'Hello'`
- 反引号: `Hello`

反引号是 **功能扩展** 引号。它们允许我们通过将变量和表达式包装在 `${…}` 中，来将它们嵌入到字符串中。

`.length` 属性是字符串长度.

### 访问字符

通过方括号 `[]` 或 `.charAt()` 方法访问.它们的区别在于超过最大长度时\[\]返回 `undefined`, `.charAt()` 方法返回空字符串 `""`.

可以用 `for..of` 遍历字符.

### 改变大小写

`toLowerCase()` 和 `toUpperCase()` 方法

### 查找子字符串

`.indexOf()` 没有找到返回 -1

`.lastIndexOf()` 从后向前找.

```js
let str = "Widget";

if (~str.indexOf("Widget")) { // if found
  alert("We found it!");
}
```

### `includes`,`startsWith`,`endsWith`方法

### 获取子字符串

`.slice(start[, end])` 方法

`.subString(start[, end])` 方法

不同的Unicode编码导致字符串非常复杂...

## Boolean类型

## null值

独立的类型.

## undefined 值

未被赋值

## Object 类型和 Symbol 类型

`object` 类型是一个特殊的类型。

其他所有的数据类型都被称为“原始类型”，因为它们的值只包含一个单独的内容（字符串、数字或者其他）。相反，`object` 则用于储存数据集合和更复杂的实体。

`symbol` 类型用于创建对象的唯一标识符。

## typeof 运算符

返回参数的类型.对 `typeof x` 的调用会以字符串的形式返回数据类型.

`typeof null` 的结果为 `"object"`。这是官方承认的 `typeof` 的错误.

> 逆天

## 数组

数组是特殊的对象.可以用方括号访问,也可以用 `.at` 方法访问元素

### `pop/push`,`shift/unshift`方法

`push`和 `unshift` 方法可以一次添加多个元素

### 循环

`for..of`

### 关于`length`属性

可用于一次性截断.所以清空数组最简单的方法就是
`arr.length = 0;`

### 多维数组

数组里面的元素可以是任何类型,包括数组.

### 数组方法

数组有大量方法.我学Rust都没有这么细致的讲解,掌握几个常用的,其他的都是现学现用.

#### splice

用于删除元素并插入新元素

```js
arr.splice(start[, deleteCount, elem1, elem2,..., elemN]);
```

#### slice

切片.

#### 遍历 `forEach`

依次取出 item, index, array. 相当于 map?那map的作用是?

#### 搜索

`indexOf`, `lastIndexOf`, `includes` 使用严格相等搜索.

#### `find`, `findIndex`, `findLastIndex`

返回 true 停止迭代

`filter` 返回所有匹配的数组

#### 转换数组

`map` 方法对数组的每个元素调用函数,返回结果数组

`sort` 方法原位排序,可接受一个函数参数作为排序方法.

```js
function compare(a, b) {
  alert(`${a}<>${b}`);
  return a - b;
}

arr.sort(compare);
```

#### `reverse`, `split`, `join`

#### `reduce`, `reduceRight`

```js
let val = arr.reduce(function(accumulator, item, index, array){}[, initial]);
```

参数：

- `accumulator` —— 是上一个函数调用的结果，第一次等于 `initial`（如果提供了 `initial` 的话）。
- `item` —— 当前的数组元素。
- `index` —— 当前索引。
- `arr` —— 数组本身。

应用函数时，上一个函数调用的结果将作为第一个参数传递给下一个函数。

#### 数组判断

`typeof` 不能区分数组和普通对象.

使用 `Array.isArray()` 判断

#### 其他方法

`arr.some(fn)` 和 `arr.every(fn)` 类似于Python里面的 `all()`, 和 `any()`.

## 总结

JavaScript 中有八种基本的数据类型。

- 七种原始数据类型（基本数据类型）：
  - `number` 用于任何类型的数字：整数或浮点数，在 `±(253-1)` 范围内的整数。
  - `bigint` 用于任意长度的整数。
  - `string` 用于字符串：一个字符串可以包含 0 个或多个字符，所以没有单独的单字符类型。
  - `boolean` 用于 `true` 和 `false`。
  - `null` 用于未知的值 —— 只有一个 `null` 值的独立类型。
  - `undefined` 用于未定义的值 —— 只有一个 `undefined` 值的独立类型。
  - `symbol` 用于唯一的标识符。
- 以及一种非原始数据类型（复杂数据类型）：
  - `object` 用于更复杂的数据结构。

我们可以通过 `typeof` 运算符查看存储在变量中的数据类型。

- 通常用作 `typeof x`，但 `typeof(x)` 也可行。
- 以字符串的形式返回类型名称，例如 `"string"`。
- `typeof null` 会返回 `"object"` —— 这是 JavaScript 编程语言的一个错误，实际上它并不是一个 `object`。
