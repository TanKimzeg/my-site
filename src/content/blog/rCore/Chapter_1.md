---
title: "第一章：应用程序与基本执行环境"
description: "本章主要是讲解如何设计和实现建立在裸机上的执行环境，并让应用程序能够在这样的执行环境中运行。"
pubDate: 2026 03 01 
categories: 
  - tech
tags:
  - os
  - rust
---

## 应用程序执行环境

操作系统虽然是软件，但它不是运行在通用操作系统（如Linux）上的一般应用软件，而是运行在裸机执行环境中的系统软件。如果采用通常的应用编程方法和编译手段，无法开发出这样的操作系统。其中一个重要的原因是：编译器（Rust 编译器和 C 编译器等）编译出的应用软件在缺省情况下是要链接标准库，而标准库是依赖于操作系统的，但操作系统不依赖其他操作系统。

如下图所示，现在通用操作系统（如 Linux 等）上的应用程序运行需要下面多层次的执行环境栈的支持，图中的白色块自上而下（越往下则越靠近底层，下层作为上层的执行环境支持上层代码的运行）表示各级执行环境，黑色块则表示相邻两层执行环境之间的接口。

![](https://rcore-os.cn/rCore-Tutorial-Book-v3/_images/app-software-stack.png)

## 目标三元组

现代编译器工具集（以C或Rust编译器为例）的主要工作流程如下：

1. 源代码（source code） –> 预处理器（preprocessor） –> 宏展开的源代码

2. 宏展开的源代码 –> 编译器（compiler） –> 汇编程序

3. 汇编程序 –> 汇编器（assembler）–> 目标代码（object code）

4. 目标代码 –> 链接器（linker） –> 可执行文件（executables）

从上图我们又知道，编译器在将其通过编译、链接得到可执行文件的时候需要知道程序要在哪个 **平台** (Platform) 上运行。这里平台主要是指 CPU 类型、操作系统类型和标准运行时库的组合。

大部分源代码是跨平台的，因此CPU、操作系统和运行时库等信息就决定了如何编译生成二进制文件。Rust编译器通过 **目标三元组** (Target Triplet) 来描述一个软件运行的目标平台。

比如我这里

```shell
rustc --version --verbose
rustc 1.93.0 (254b59607 2026-01-19)
binary: rustc
commit-hash: 254b59607d4417e9dffbc307138ae5c86280fe4c
commit-date: 2026-01-19
host: x86_64-pc-windows-gnu
release: 1.93.0
LLVM version: 21.1.8
```

本课程我们选择 `riscv64gc-unknown-none-elf` 目标平台。这其中的 CPU 架构是 riscv64gc ，CPU厂商是 unknown ，操作系统是 none ， elf 表示没有标准的运行时库（表明没有任何系统调用的封装支持），但可以生成 ELF 格式的执行程序。

## QEMU启动流程

我一直不太了解计算机的启动流程。在MAKEFILE中可以看到QEMU的启动脚本：

```shell
qemu-system-riscv64 \
    -machine virt \
    -nographic \
    -bios ../bootloader/rustsbi-qemu.bin \
    -device loader,file=target/riscv64gc-unknown-none-elf/release/os.bin,addr=0x80200000
```

其中各个执行参数选项的含义如下：

- `-machine virt` 表示将模拟的 64 位 RISC-V 计算机设置为名为 `virt` 的虚拟计算机。
- `-nographic` 表示模拟器不需要提供图形界面，而只需要对外输出字符流。
- 通过 `-bios` 可以设置 Qemu 模拟器开机时用来初始化的引导加载程序（bootloader），这里我们使用预编译好的 `rustsbi-qemu.bin` ，它需要被放在与 `os` 同级的 `bootloader` 目录下，该目录可以从每一章的代码分支中获得。
- 通过虚拟设备 `-device` 中的 `loader` 属性可以在 Qemu 模拟器开机之前将一个宿主机上的文件载入到 Qemu 的物理内存的指定位置中， `file` 和 `addr` 属性分别可以设置待载入文件的路径以及将文件载入到的 Qemu 物理内存上的物理地址。

在Qemu模拟的 `virt` 硬件平台上，物理内存的起始物理地址为 `0x80000000` ，物理内存的默认大小为 128MiB 。如果使用默认配置的 128MiB 物理内存则对应的物理地址区间为 `[0x80000000,0x88000000)` 。

启动三个阶段：

- 第一阶段：将必要的文件载入到 Qemu 物理内存之后，Qemu CPU 的程序计数器（PC, Program Counter）会被初始化为 `0x1000` ，因此 Qemu 实际执行的第一条指令位于物理地址 `0x1000` ，接下来它将执行寥寥数条指令并跳转到物理地址 `0x80000000` 对应的指令处并进入第二阶段。从后面的调试过程可以看出，该地址 `0x80000000` 被固化在 Qemu 中，作为 Qemu 的使用者，我们在不触及 Qemu 源代码的情况下无法进行更改。

- 第二阶段：由于 Qemu 的第一阶段固定跳转到 `0x80000000` ，我们需要将负责第二阶段的 bootloader `rustsbi-qemu.bin` 放在以物理地址 `0x80000000` 开头的物理内存中，这样就能保证 `0x80000000` 处正好保存 bootloader 的第一条指令。在这一阶段，bootloader 负责对计算机进行一些初始化工作，并跳转到下一阶段软件的入口，在 Qemu 上即可实现将计算机控制权移交给我们的内核镜像 `os.bin` 。这里需要注意的是，对于不同的 bootloader 而言，下一阶段软件的入口不一定相同，而且获取这一信息的方式和时间点也不同：入口地址可能是一个预先约定好的固定的值，也有可能是在 bootloader 运行期间才动态获取到的值。我们选用的 RustSBI 则是将下一阶段的入口地址预先约定为固定的 `0x80200000` ，在 RustSBI 的初始化工作完成之后，它会跳转到该地址并将计算机控制权移交给下一阶段的软件——也即我们的内核镜像。

- 第三阶段：为了正确地和上一阶段的 RustSBI 对接，我们需要保证内核的第一条指令位于物理地址 `0x80200000` 处。为此，我们需要将内核镜像预先加载到 Qemu 物理内存以地址 `0x80200000` 开头的区域上。一旦 CPU 开始执行内核的第一条指令，证明计算机的控制权已经被移交给我们的内核，也就达到了本节的目标。

> 我原来不清楚这几个地址的设计意图，看了好几遍，返回来看教材才发现是QEMU和RustSBI写死的。我发现实验指导书主要讲解代码，有些细节没有解释。教材的内容又非常多，初看找不到重点。因此还是得反复啃……先看实验指导书，再阅读代码，最后返回来看教材，很多疑惑和没注意的细节就水落石出。

**真实计算机的加电启动流程**类似，我不需要详细了解。

## 程序内存布局

![](https://rcore-os.cn/rCore-Tutorial-Book-v3/_images/MemoryLayout.png)

这个布局可以说是大家非常熟悉的了，但这里我想提醒注意这两个section：

- 已初始化数据段保存程序中那些已初始化的全局数据，分为 `.rodata` 和 `.data` 两部分。前者存放只读的全局数据，通常是一些常数或者是 常量字符串等；而后者存放可修改的全局数据。

- 未初始化数据段 `.bss` 保存程序中那些未初始化的全局数据，通常由程序的加载者代为进行零初始化，即将这块区域逐字节清零；

在代码里面，我确实看到了程序启动前对 `.bss` 段逐位设置为0的操作。这种细节在以前是不了解的。

![](https://rcore-os.cn/rCore-Tutorial-Book-v3/_images/link-sections.png)

链接这块跟我在CS:APP中学到的一致。想要拓展就回去复习就行。

## 手动加载内核可执行文件

![](https://rcore-os.cn/rCore-Tutorial-Book-v3/_images/load-into-qemu.png)

我们对目标平台的设置导致生成的二进制文件是ELF格式，包含一些元数据。这些多余的数据需要剥除，然后通过链接到固定地址形成操作系统的镜像文件，整个加载到固定位置的内存中。

## 基于SBI服务完成输出和关机

和U模式下的系统调用中 `ecall` 的使用类似, S模式下也是通过 `ecall` 来进入M模式, 从而使用sbi提供的服务。

输出到控制台和断点关机是需要硬件层面支持的操作，也就是需要调用SBI。

## 练习

1. 实现一个应用程序A，显示当前目录下的文件名。

```rust
use std::env::current_dir;
use std::fs;
use std::path::Path;

fn main() -> std::io::Result<()> {
    let current_dir = current_dir().expect("Failed to get current directory");
    println!("Current directory: {}", current_dir.display());
    let path = Path::new(current_dir.as_os_str());
    println!("Contents of the directory:");
    for entry in fs::read_dir(path).expect("Failed to read directory") {
        let entry = entry.expect("Failed to get directory entry");
        let file_name = entry.file_name();
        println!("{}", file_name.to_string_lossy());
    }

    Ok(())
}
```

1. 实现一个应用程序B，能打印出调用栈链信息。

询问DeepSeek后得知，可以使用 `backtrace` crate来完成这一功能。

```rust
use backtrace::Backtrace;

fn main() {
    println!("程序开始，即将进入函数调用链...");
    a();
}

fn a() {
    b();
}

fn b() {
    c();
}

fn c() {
    print_backtrace();
}

fn print_backtrace() {
    println!("\n=== 调用栈链信息 ===");
    // 获取当前调用栈
    let bt = Backtrace::new();
    // 以调试格式打印，会包含符号信息（需要调试符号）
    println!("{:#?}", bt);
}

```

能得到一大串：

```
程序开始，即将进入函数调用链...

=== 调用栈链信息 ===
   0:     0x7ff694fab35a - backtrace::backtrace::win64::trace::h3bca1746e4120269
                               at E:\cargo-cache\registry\src\rsproxy.cn-e3de039b2554c837\backtrace-0.3.76\src\backtrace\win64.rs:85:14
                           backtrace::backtrace::trace_unsynchronized::h4be988f8aac5d749
                               at E:\cargo-cache\registry\src\rsproxy.cn-e3de039b2554c837\backtrace-0.3.76\src\backtrace\mod.rs:66:14
   1:     0x7ff694fab6b1 - backtrace::backtrace::trace::h6f1926d6116557ec
                               at E:\cargo-cache\registry\src\rsproxy.cn-e3de039b2554c837\backtrace-0.3.76\src\backtrace\mod.rs:53:14
   2:     0x7ff694f836da - backtrace::capture::Backtrace::create::h54b69d0daf40c6bc
                               at E:\cargo-cache\registry\src\rsproxy.cn-e3de039b2554c837\backtrace-0.3.76\src\capture.rs:294:9
   3:     0x7ff694f83640 - backtrace::capture::Backtrace::new::h875ccf625453caba
                               at E:\cargo-cache\registry\src\rsproxy.cn-e3de039b2554c837\backtrace-0.3.76\src\capture.rs:259:22
   4:     0x7ff694f71582 - backtrace_demo::print_backtrace::hb2c414abd952b993
                               at E:\Documents\learnRust\backtrace_demo\src\main.rs:23:14
   5:     0x7ff694f71649 - backtrace_demo::c::h86e369defa061388
                               at E:\Documents\learnRust\backtrace_demo\src\main.rs:17:5
   6:     0x7ff694f71639 - backtrace_demo::b::h1a8959c6123956f5
                               at E:\Documents\learnRust\backtrace_demo\src\main.rs:13:5
   7:     0x7ff694f71629 - backtrace_demo::a::hb660dee3ec66682e
                               at E:\Documents\learnRust\backtrace_demo\src\main.rs:9:5
   8:     0x7ff694f71672 - backtrace_demo::main::hbef9756fc813855a
                               at E:\Documents\learnRust\backtrace_demo\src\main.rs:5:5
   9:     0x7ff694f714fb - core::ops::function::FnOnce::call_once::h8d26aaad1d692375
                               at E:\rust-toolchain\toolchains\stable-x86_64-pc-windows-gnu\lib/rustlib/src/rust\library\core\src\ops\function.rs:250:5
  10:     0x7ff694f7145e - std::sys::backtrace::__rust_begin_short_backtrace::h6a45ef28d71b4fea
                               at E:\rust-toolchain\toolchains\stable-x86_64-pc-windows-gnu\lib/rustlib/src/rust\library\std\src\sys\backtrace.rs:160:18
  11:     0x7ff694f71711 - std::rt::lang_start::{{closure}}::h04fa871a1135797f
                               at E:\rust-toolchain\toolchains\stable-x86_64-pc-windows-gnu\lib/rustlib/src/rust\library\std\src\rt.rs:206:18
  12:     0x7ff695089272 - std::rt::lang_start_internal::h5a50cb1527320f99
                               at /rustc/254b59607d4417e9dffbc307138ae5c86280fe4c/library\core\src\ops/function.rs:287:21
  13:     0x7ff694f716fa - std::rt::lang_start::hb7b10131d327e8f8
                               at E:\rust-toolchain\toolchains\stable-x86_64-pc-windows-gnu\lib/rustlib/src/rust\library\std\src\rt.rs:205:5
  14:     0x7ff694f716af - main
  15:     0x7ff694f712ef - __tmainCRTStartup
  16:     0x7ff694f71406 - mainCRTStartup
  17:     0x7ff92b7c53e0 - <unknown>
  18:     0x7ff92c44485b - <unknown>
```

## 参考资料

- <https://zhuanlan.zhihu.com/c_1738250998752292864>

- <https://sazikk.top/posts/%E7%AC%94%E8%AE%B0-rCoreLab%E5%AE%9E%E9%AA%8C%E7%AC%94%E8%AE%B0/>
