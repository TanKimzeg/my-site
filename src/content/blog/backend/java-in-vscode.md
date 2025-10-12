---
title: VSCode搭建Java开发环境 | Java
description: "VSCode搭建Java开发环境"
pubDate: 2025 10 12
categories:
  - tech
tags:
  - java
---

![java-brain](/backend/java-brain.jpg)

近期在实习单位写Java后端,就想着在我的本地也搭建Java开发环境.之前下载Xbox的Minecraft需要Java执行环境,所以安装过几次JRE和JDK.JRE是Java程序的运行环境,JDK则是开发套件,包含了JRE.我清理了原来的环境,安装了最新的JDK25.

对于IDE的选择,如果Java是你的主力开发语言,还是建议用JB家的IDEA,功能方便,分析能力强大.但是我只是用来轻度体验,IDEA太笨重了,就不合适.所以我决定基于VSCode搭建开发环境.简中网上的大部分教程都是IDEA的设置,关于VSCode的很少.鉴于此,为了学习Java的项目管理,顺便简单介绍一下在VSCode中搭建Java开发环境.

## 工具链安装

首先,如果以前装过Minecraft等游戏,最好使用[卸载工具](https://www.java.com/zh-CN/download/uninstalltool.jsp)卸载掉多余的JRE或者过时的JDK,然后[安装新版的JDK](https://www.oracle.com/java/technologies/downloads/).完成安装后,在命令行中执行

```shell
java -version
javac -version
```

检查是否成功安装.

JDK安装完后,再[安装Maven](https://maven.apache.org/download.cgi).

Maven是Java生态的项目和包管理工具. [Maven简介](https://blog.csdn.net/qq_44757034/article/details/120238561)简单修改一下全局配置(repo位置,镜像地址),添加到PATH环境变量.

## Java项目结构

说实话,Java的语法非常简单,我不用专门学习,直接上手就能写了.但是项目结构需要认真了解,不然看不懂为什么这么写,导入包也会出错.

这是普通的Java项目结构:
[IDEA 创建的 Java 项目结构：从零到一](https://blog.csdn.net/xycxycooo/article/details/142061331)

这是Spring网络应用的项目结构:
https://zhuanlan.zhihu.com/p/115403195

其实都是相似的,我注意到`java`下总是有一个 `com.`,[这有什么必要](https://dev59.com/mGs05IYBdhLWcg3wJ-uQ)?

导入包有的也以 `org.` 开头,其实是为了避免包重名.这确实是一个解决办法.像Pypi, crate.io上面的包都不允许重名,先到先得的特点饱受诟病.我有自己的域名,所以,我写的Java程序,就会命名为 `top.tankimzeg.*`.

同时,这个包下的类上添加一行:

```java
package top.tankimzeg.xxx;
```

https://www.cnblogs.com/geekbruce/articles/18463444

## VSCode配置

打开VSCode,安装微软发布的 Extension Pack for Java, 一共有7个捆绑包.

然后在 settings.json里面添加配置,参考如下:

```json
{
  /* Settings for Java Development */
  "java.configuration.runtimes": [
    {
      "name": "JavaSE-25",
      "path": "D:/Java/jdk-25",
      "default": true
    }
  ],
  "java.jdt.ls.java.home": "D:/Java/jdk-25",
  "java.configuration.maven.globalSettings": "D:/Maven/apache-maven-3.9.11-bin/apache-maven-3.9.11/conf/settings.xml",
  "java.configuration.updateBuildConfiguration": "automatic",
  "java.autobuild.enabled": true
}
```

在项目文件夹下的 `.vscode/settings.json` 也可以设置,但可能会导致一个问题.待会说.

### 工作区设置

我喜欢将我的项目保存为工作区,集中放到一个桌面的文件夹里.相当于一个快捷方式,每次都能很方便地打开一个项目.

工作区设置使您能够在已打开的工作区上下文中配置设置，并始终覆盖全局用户设置。单根工作区的设置存储在 *.vscode/settings.json* 中，而多根工作区的设置存储在 *.code-workspace* 文件中。

我都用的是单根工作区,设置保存在项目的 `.vscode/settings.json`, 以前都没出问题. 但这次当我保存一个Java工作区再打开时,加载设置却出问题了.

> 此设置无法应用于此工作区。它将在您直接打开包含的工作区文件夹时应用。

只有去原来项目的文件夹下,用

```shell
cd JavaProject
code .
```

打开才能生效.

编辑`.code-workspace`文件,在里面的settings复制`.vscode/settings.json` 才解决了这个问题.看来,这个工作区被当成了多根工作区,真奇怪.

[VSCode工作区配置](https://zhuanlan.zhihu.com/p/54770077)提到了配置文件生效顺序.

## 一个简单的Java项目

> 展示Maven的使用

在这里不使用mvn自动创建命令,而是手动创建,一步步理解每个文件的作用.

在项目的根目录下创建一个 `pom.xml` ,这包含了项目的信息和依赖:

```xml
<project
    xmlns="http://maven.apache.org/POM/4.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>top.tankimzeg</groupId>
    <artifactId>Calculator</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>jar</packaging>
    <properties>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
    </properties>
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.12</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

执行

```shell
mvn install
```

这是一个简单的四则运算计算器.已符合标准 Maven 布局，源码与测试分离且能够成功编译并通过测试。

- 主代码类：`top.tankimzeg.calc.Calculator`
- 测试类：`top.tankimzeg.calc.CalculatorTest`
- 构建配置：pom.xml

```java
package top.tankimzeg.calc;

import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class CalculatorTest {

    @Test
    public void testAdd() {
        assertEquals(2, Calculator.add(2, 0));
    }

    @Test
    public void testSubtract() {
        assertEquals(2, Calculator.subtract(5, 3));
    }
}
```

可运行测试:

```shell
mvn test
```

项目结构:

```
JavaProject
├─ pom.xml
├─ .vscode/
│  └─ settings.json
├─ src/
│  ├─ main/
│  │  ├─ java/
│  │  │  └─ top/tankimzeg/calc/
│  │  │     └─ Calculator.java
│  │  └─ resources/
│  └─ test/
│     ├─ java/
│     │  └─ top/tankimzeg/calc/
│     │     └─ CalculatorTest.java
│     └─ resources/
└─ target/
   ├─ classes/...
   ├─ test-classes/...
   ├─ surefire-reports/
   │  ├─ TEST-top.tankimzeg.calc.CalculatorTest.xml
   │  └─ *.dumpstream
   └─ Calculator-1.0-SNAPSHOT.jar
```

至此,我对Java的了解程度大大提升,中间件的掌握程度成为了开发能力的唯一制约.而在实习单位,我每天都与SpringBoot, Mybatis这些打交道.Java生态虽然发达,中间件虽然神奇,但依然改变不了给我一种繁琐笨重的感觉.
