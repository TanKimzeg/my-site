---
title: ESLint和Prettier配置
description: "在VSCode中初步配置ESLint和Prettier"
pubDate: 2025 10 05 
categories: 
  - tech
tags:
  - javascript
---

最近在做前后端项目,前端采用VUE,后端用的是Springboot.在编辑前端页面的时候都是照猫画虎,不甚满意.所以不得不来学习一下前端的知识,先从Javascript开始.

我跟着[教程](https://zh.javascript.info/coding-style)来到了代码风格这一章,发现了ESlint这个工具.之前VSCode偶尔会推荐我安装,我不知道是什么功能,今天就来探索一下!网上的教程非常混乱,有的已经过时,有的语焉不详,初次接触,我研究了好久!

## ESlint

ESlint是一个代码检查工具,既可以检查语法错误,也可以检查自定义的代码风格.

### 使用ESlint包

首先我们需要安装eslint包,运行:

```shell
npm init
npm install --save-dev eslint
npx eslint --init
```

按照指引完成配置,就会自动生成一个 `eslint.config.mjx` 文件.有的教程可能会说创建一个 `.eslintrc` 的文件,但是在[官方的文档](https://eslint.org/docs/latest/use/configure/configuration-files)里面已经没有详细介绍它了,已经过时了.

```js
import js from "@eslint/js";
import globals from "globals";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["src/*.{js,mjs,cjs}"],
    plugins: { js },
    rules: { "prettier/prettier": "warn" },
    extends: ["js/recommended"],
    languageOptions: { globals: globals.node },
  },
  { files: ["**/*.js"], languageOptions: { sourceType: "commonjs" } },
]);

```

我的工作区目前只是在学习基础的js,所以做了很简单的配置,自动生成的配置文件就是这样.

然后,在`npm init`生成的 `package.json`中添加一行script:

```json
{
	"scripts": {
		"lint": "eslint src/**"
	}
}
```

由于我上面配置文件中的环境选的是 `node`, 不支持浏览器函数(如 `alert`,`prompt`,`confirm`).为了测试,我们在js中写一条alert语句,然后运行

```shell
npm run lint
# 或者指定文件
npx eslint ./src/hello.js
```

就会看到报错.

### 使用VSCode的ESLint插件

在没有安装插件之前,VSCode已经有javascript的高亮和补全.但它不知道执行环境,也没有自定义的代码风格.

为了在编写代码的过程中看到错误提示,需要安装并启用微软维护的ESLint插件,它能自动读取 `eslint.confing.mjx`文件,就可以看到 `alert();`语句的错误提示了.

## 代码格式化

在Rust的工具链中,我们可以使用 `cargo fmt` 和 `rustfmt` 来格式化代码(虽然我不爱用), 而前端项目也有代码格式化的工具.

在配置文件里面可以设置一些规则,比如:

```json
{
    "rules": {
        "no-console": "error",
        "indent": ["error", 2]
    }
}
```

这样,代码中出现 `console.log()`就会报错.

所有可用的rules在[Rules](https://zh-hans.eslint.org/docs/latest/rules/)

### 使用Prettier插件

Prettier专用于代码格式化.为了使用prettier,首先安装 `eslint-plugin-prettier`:

```shell
npm install eslint-plugin-prettier
```

然后在配置文件中启用插件,修改成这样:

```js
import js from "@eslint/js";
import prettier from "eslint-plugin-prettier";
import globals from "globals";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["src/*.{js,mjs,cjs}"],
    plugins: { js, prettier },
    rules: { "prettier/prettier": "warn" },
    extends: ["js/recommended"],
    languageOptions: { globals: globals.node },
  },
  { files: ["**/*.js"], languageOptions: { sourceType: "commonjs" } },
]);

```

重启VSCode 的 ESlint插件,就会看到不少警告,主要是换行符问题(CRLF -> LF).

运行

```shell
npm run lint
# 或者指定文件
npx eslint .\hello.js
```

就能看到提示信息

```
✖ 1 problem (0 errors, 1 warning)
  0 errors and 1 warning potentially fixable with the `--fix` option.

```

加上 `--fix` 可以直接修复.

或者,在VSCode 中打开设置(Ctrl + ,),搜索 eslint:format, 启用.这样在代码编辑区域右键,选择 "使用...格式化文档", 再选择 ESLint,也能对文件进行格式化.

插件有很多,包括 [typescript](https://typescript-eslint.io/rules/), [react](https://github.com/jsx-eslint/eslint-plugin-react), [vue](https://eslint.vuejs.org/rules/) 都有各自的插件和规则, 后面做项目就可以用到了~

## REFERRENCE

[Linter上手完全指南](https://github.yanhaixiang.com/linter-tutorial/practice/eslint_prettier.html)

[ESlint](https://zh-hans.eslint.org/docs/latest/use/getting-started)
官方网站页面最下方可以设置简体中文语言
