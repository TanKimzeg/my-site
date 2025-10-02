---
title: Lv0：环境配置 | 编译原理
description: "PKU编译原理实践课程"
pubDate: 2025 08 13
categories: 
  - tech
tags:
  - compiler
  - rust
---

## Docker配置
我的Windows系统里面没有安装docker, 这次还得先安装Docker Desktop. 我以前以为Docker只能在Linux世界中使用, 所以我的WSL里面装了docker, 后来发现Windows也有Docker Desktop, 提供GUI界面, 方便管理,但由于我主要在Linux中用docker,就没去搞. 这次不得不安装一个臃肿的GUI界面,有点烦.一打开安装包,就提示: Docker Desktop requires the Server service to be enabled.

解决方法是Win+R打开services.msc, 开启Server服务自启动.

接着,安装程序就失去响应了...真的逆天啊

更逆天的是默认安装位置在C盘,若要更改位置只能:

```shell
`"D:\Download\Docker Desktop Installer.exe"`  `install --installation-dir=``"D:\Docker"`
```

在设置中修改镜像的存储位置

Docker容器的启动方式：
```shell
docker run -it --rm -v /home/max/compiler:/root/compiler maxxing/compiler-dev bash
```
这会在退出后自动删除容器

如果虚拟机没有被搞坏,我自己觉得这样更好,毕竟不用清除Cargo的缓存:
```shell
docker run -itd -v /.compiler:/root/compiler maxxing/compiler-dev bash
docker restart <container id>
docker exec -it <container id> bash
docker stop <container id>
```



## Koopa IR简介

Koopa IR 是一种专为北京大学编译原理课程实践设计的教学用的中间表示 (IR),Koopa IR 是一种强类型的 IR, IR 中的所有值 (`Value`) 和函数 (`Function`) 都具备类型 (`Type`).

我暂时不能理解以上内容.

### 本地运行Koopa IR
假设你已经把一个 Koopa IR 程序保存在了文件 `hello.koopa` 中, 你可以在实验环境中运行这个 Koopa IR 程序:

```
koopac hello.koopa | llc --filetype=obj -o hello.o
clang hello.o -L$CDE_LIBRARY_PATH/native -lsysy -o hello
./hello
```

## RISC-V简介
在之前的THU rCore中,我接触了RISC-V. 
RISC-V是一种开源的指令系统体系结构 (ISA). RISC-V 没有任何历史包袱, 设计简洁, 高效低能耗, 且高度模块化.相对于我之前在CS:APP中学过的英特尔x86指令集来说, 这又是一个新指令集, 需要从头学习.

RISC-V 的指令系统由基础指令集 (base instruction set) 和指令集扩展 (extension) 构成. 每个 RISC-V 处理器必须实现基础指令系统, 同时可以支持若干扩展. 常用的基础指令系统有两种:
- `RV32I`: 32 位整数指令系统.
- `RV64I`: 64 位整数指令系统. 兼容 `RV32I`.

常用的标准指令系统扩展包括:

- `M` 扩展: 包括乘法和除法相关的指令.
- `A` 扩展: 包括原子内存操作相关的指令.
- `F` 扩展: 包括单精度浮点操作相关的指令.
- `D` 扩展: 包括双精度浮点操作相关的指令.
- `C` 扩展: 包括常用指令的 16 位宽度的压缩版本.

我们通常使用 `RV32/64I` + 扩展名称的方式来描述某个处理器/平台支持的 RISC-V 指令系统类型, 例如 `RV32IMA` 代表这个处理器是一个 32 位的, 支持 `M` 和 `A` 扩展的 RISC-V 处理器.

在课程实践中, 我的编译器将生成 `RV32IM` 范围内的 RISC-V 汇编.

[RISC-V 指令速查](https://pku-minic.github.io/online-doc/#/misc-app-ref/riscv-insts)

### 运行RISC-V汇编
假设你已经把一个 RISC-V 汇编程序保存在了文件 `hello.S` 中, 你可以在实验环境中将这个 RISC-V 程序汇编并链接成可执行文件, 然后运行这个可执行文件:

```
clang hello.S -c -o hello.o -target riscv32-unknown-linux-elf -march=rv32im -mabi=ilp32
ld.lld hello.o -L$CDE_LIBRARY_PATH/riscv32 -lsysy -o hello
qemu-riscv32-static hello
```
