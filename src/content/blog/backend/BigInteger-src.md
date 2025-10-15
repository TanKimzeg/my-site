---
title: BigInteger类源码阅读 | Java
description: "java.math.BigInteger类的源码分析"
pubDate: 2025 10 15
categories:
  - tech
tags:
  - java
---

## BigInteger简介

BigInteger是Java中用于表示任意精度整数的类,位于`java.math`包中.它可以处理超出基本数据类型(如int和long)范围的整数运算.BigInteger类提供了丰富的方法来进行算术运算、位操作、比较等操作.

这是一个大数运算的类.之前学算法竞赛的时候,看过高精度计算的算法.这里也涉及一些大数运算的算法.

网上关于BigInteger的研究不是很多. [Java大数源码剖析(一) - BigInteger的底层数据结构](https://zhuanlan.zhihu.com/p/390067069)

## BigInteger的内部表示

BigInteger主要由符号位和int数组构成.

```java
final int signum;

final int[] mag;
```

其中, `signum`表示整数的符号,取值为-1(负数),0(零),1(正数). `mag`是一个int数组,用于存储整数的绝对值,每个int元素表示整数的一部分,按大端序存储.

## 构造方法

BigInteger类提供了多种构造方法(重载).有的是公开接口,有的是私有的辅助方法.

这里我着重解析

```java
public BigInteger(String val, int radix); // line at 415
```

用法如

```java
BigInteger bigInt = new BigInteger("12345", 10);
```

首先会判断输入合法性: 进制合理(2到36),字符串非空,整数部分合法.

`cursor` 是处理字符串的索引,跳过前导0.

然后来到数组大小的预分配.向上取整以免存放不下.

```java
long numBits = ((numDigits * bitsPerDigit[radix]) >>> 32) + 1;
```

这里计算 `radix` 进制下 `numDigits` 位数字所需的二进制位数 `numBits` . `bitsPerDigit` 是一个预定义的数组,存储了不同进制下每位数字对应的二进制位数.

从数学的角度来看, 当大整数趋于无穷大时,需要的
$$ numBits = numDigits \cdot \log_2 (radix) $$

这里又是乘 `bigsPerDigit[radix]` , 又是 `>>>10` .其实是做精度上的估算. 放大了1024倍,再除以1024.你也可以乘2048, 再除以2048.以 `radix = 3` 为例, $\log_2(3) \times 1024 \approx 1623.\dots$, 所以 `bitsPerDigit[3] = 1624`.

下一步将 `numBits` 向上对齐到字(int 类型的大小),从而分配足够的 `int[]` 空间.

再往下,取出不足一字的最高几位.这里出现了 `digitsPerInt[radix]` ,它是一个预定义数组,指几位 `radix` 进制数字可以放入一个int中.以十进制为例, `digitsPerInt[10] = 9` ,表示一个int可以存放9位十进制数字.我们知道, $10^9 < 2^{32} < 10^{10}$.但是这里, `digitsPerInt[2] = 30`, 好像还是有符号整数的范围?

后面就是从右向左依次填入 `int[]` 数组了.每次向左移动一位,需要乘这个进制下32位能容纳的最大数.也就是说,

$$ intRadix[radix] = radix^{digitsPerInt[radix]} $$

使用了 `destruciveMulAdd` 辅助函数实现.

```java
    private static void destructiveMulAdd(int[] x, int y, int z) {
        // Perform the multiplication word by word
        long ylong = y & LONG_MASK;
        long zlong = z & LONG_MASK;
        int len = x.length;

        long product = 0;
        long carry = 0;
        for (int i = len-1; i >= 0; i--) {
            product = ylong * (x[i] & LONG_MASK) + carry;
            x[i] = (int)product;
            carry = product >>> 32;
        }

        // Perform the addition
        long sum = (x[len-1] & LONG_MASK) + zlong;
        x[len-1] = (int)sum;
        carry = sum >>> 32;
        for (int i = len-2; i >= 0; i--) {
            sum = (x[i] & LONG_MASK) + carry;
            x[i] = (int)sum;
            carry = sum >>> 32;
        }
    }
```

类似的运算,我们在后面的大数运算方法中也会用到.

至此,我们已经完成了字符串到BigInteger的转换.构造方法基本解析完毕.

接下来是一些随机大数生成方法、大质数生成方法等,涉及专业的密码学知识,这里不做赘述.

## 加法

根据两个大数符号的不同,转换为 `mag` 数组的加法或减法.

这里讲的是 `mag` 的加法(私有)

跟竖式加法类似,我们需要从低位起逐位相加,并处理进位.

```java
    private static int[] add(int[] x, int[] y) {
        // If x is shorter, swap the two arrays
        if (x.length < y.length) {
            int[] tmp = x;
            x = y;
            y = tmp;
        }

        int xIndex = x.length;
        int yIndex = y.length;
        int result[] = new int[xIndex];
        long sum = 0;
        if (yIndex == 1) {
            sum = (x[--xIndex] & LONG_MASK) + (y[0] & LONG_MASK) ;
            result[xIndex] = (int)sum;
        } else {
            // Add common parts of both numbers
            while (yIndex > 0) {
                sum = (x[--xIndex] & LONG_MASK) +
                      (y[--yIndex] & LONG_MASK) + (sum >>> 32);
                result[xIndex] = (int)sum;
            }
        }
        // Copy remainder of longer number while carry propagation is required
        boolean carry = (sum >>> 32 != 0);
        while (xIndex > 0 && carry)
            carry = ((result[--xIndex] = x[xIndex] + 1) == 0);

        // Copy remainder of longer number
        while (xIndex > 0)
            result[--xIndex] = x[xIndex];

        // Grow result if necessary
        if (carry) {
            int bigger[] = new int[result.length + 1];
            System.arraycopy(result, 0, bigger, 1, result.length);
            bigger[0] = 0x01;
            return bigger;
        }
        return result;
    }
```

精彩绝伦!

## 减法

减法原理相似,但需注意借位.这里体现了计算机反码的巧妙之处!

比如, 在十进制世界中, 6-7=-1.在计算机世界中, -1以全1存储,恰好从无符号来看是最大数字,即9.

<div align="center">

$$ 32 bits| 32 bits $$

$$ 11111 | 11111 $$

$$ \downarrow | \downarrow $$

$$ -1 | +9 $$
</div>

所以借位也不必太复杂,实际上跟进位***对偶***.

```java
private static int[] subtract(int[] big, int[] little) {
        int bigIndex = big.length;
        int result[] = new int[bigIndex];
        int littleIndex = little.length;
        long difference = 0;

        // Subtract common parts of both numbers
        while (littleIndex > 0) {
            difference = (big[--bigIndex] & LONG_MASK) -
                         (little[--littleIndex] & LONG_MASK) +
                         (difference >> 32);
            result[bigIndex] = (int)difference;
        }

        // Subtract remainder of longer number while borrow propagates
        boolean borrow = (difference >> 32 != 0);
        while (bigIndex > 0 && borrow)
            borrow = ((result[--bigIndex] = big[bigIndex] - 1) == -1);

        // Copy remainder of longer number
        while (bigIndex > 0)
            result[--bigIndex] = big[bigIndex];

        return result;
    }
```

## 乘法

根据数的范围,采用了三种不同的乘法算法.

- `multiplyToLen`: 传统的逐位乘法,时间复杂度$O(n^2)$

- `karatsubaMultiply`: Karatsuba算法,时间复杂度$O(n^{\log_2(3)}) \approx O(n^{1.585})$

- `multiplyToomCook3`: Toom-Cook算法,时间复杂度$O(n^{1.465})$

## 除法

除法太复杂了, 我就不展开了.

## 乘方

主要是快速幂,但为了优化分了很多情况,也要判断是否溢出.

$(1101000)_2 $ 对于右侧的0,先右移,最后再左移,可以减小参与运算的数.这是我在那些圈地自萌的算法竞赛题解里面没有看到的!

如果结果小,在 `long` 范围内,直接乘法.如果是大数,调用已经实现的 `multipy` 和 `squre` 方法(`squre`有优化,我已略过).

```java
   /**
     * Returns a BigInteger whose value is <code>(this<sup>exponent</sup>)</code>.
     * Note that {@code exponent} is an integer rather than a BigInteger.
     *
     * @param  exponent exponent to which this BigInteger is to be raised.
     * @return <code>this<sup>exponent</sup></code>
     * @throws ArithmeticException {@code exponent} is negative.  (This would
     *         cause the operation to yield a non-integer value.)
     */
    public BigInteger pow(int exponent) {
        if (exponent < 0) {
            throw new ArithmeticException("Negative exponent");
        }
        if (exponent == 0 || this.equals(ONE))
            return ONE;

        if (signum == 0 || exponent == 1)
            return this;

        BigInteger base = this.abs();
        final boolean negative = signum < 0 && (exponent & 1) == 1;

        // Factor out powers of two from the base, as the exponentiation of
        // these can be done by left shifts only.
        // The remaining part can then be exponentiated faster.  The
        // powers of two will be multiplied back at the end.
        final int powersOfTwo = base.getLowestSetBit();
        final long bitsToShiftLong = (long) powersOfTwo * exponent;
        final int bitsToShift = (int) bitsToShiftLong;
        if (bitsToShift != bitsToShiftLong) {
            reportOverflow();
        }

        // Factor the powers of two out quickly by shifting right.
        base = base.shiftRight(powersOfTwo);
        final int remainingBits = base.bitLength();
        if (remainingBits == 1) // Nothing left but +/- 1?
            return (negative ? NEGATIVE_ONE : ONE).shiftLeft(bitsToShift);

        // This is a quick way to approximate the size of the result,
        // similar to doing log2[n] * exponent.  This will give an upper bound
        // of how big the result can be, and which algorithm to use.
        final long scaleFactor = (long) remainingBits * exponent;

        // Use slightly different algorithms for small and large operands.
        // See if the result will safely fit into an unsigned long. (Largest 2^64-1)
        if (scaleFactor <= Long.SIZE) {
            // Small number algorithm.  Everything fits into an unsigned long.
            final int newSign = negative ? -1 : 1;
            final long result = unsignedLongPow(base.mag[0] & LONG_MASK, exponent);

            // Multiply back the powers of two (quickly, by shifting left)
            return bitsToShift + scaleFactor <= Long.SIZE  // Fits in long?
                    ? new BigInteger(result << bitsToShift, newSign)
                    : new BigInteger(result, newSign).shiftLeft(bitsToShift);
        }
        // (magBitLength() - 1L) * exponent + 1L > Integer.MAX_VALUE
        if (scaleFactor + bitsToShift - exponent >= Integer.MAX_VALUE) {
            reportOverflow();
        }

        // Large number algorithm.  This is basically identical to
        // the algorithm above, but calls multiply()
        // which may use more efficient algorithms for large numbers.
        BigInteger answer = ONE;

        final int expZeros = Integer.numberOfLeadingZeros(exponent);
        int workingExp = exponent << expZeros;
        // Perform exponentiation using repeated squaring trick
        // The loop relies on this invariant:
        // base^exponent == answer^(2^expLen) * base^(workingExp >>> (32-expLen))
        for (int expLen = Integer.SIZE - expZeros; expLen > 0; expLen--) {
            answer = answer.multiply(answer);
            if (workingExp < 0) // leading bit is set
                answer = answer.multiply(base);

            workingExp <<= 1;
        }

        // Multiply back the (exponentiated) powers of two (quickly,
        // by shifting left)
        answer = answer.shiftLeft(bitsToShift);
        return negative ? answer.negate() : answer;
    }
```

## 其余

`mod`, `gcd`, `shift` 和质数等方法,剩下的就不一一解析了,有兴趣可以看源码.

> 一个类四千多行,是谁的一辈子...
