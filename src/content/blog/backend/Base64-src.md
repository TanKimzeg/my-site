---
title: Base64源码阅读 | Java
description: "java.util.Base64类的源码分析"
pubDate: 2025 10 17
categories:
  - tech
tags:
  - java
---

## Base64简介

Base64是一种常见的编码方式,用于将二进制数据转换为文本格式,以便在文本传输协议中传输. 许多通信协议和数据格式是为文本而不是二进制数据设计的.因此,当我们尝试通过这些系统发送二进制数据时,可能会遇到问题:

- 某些传输协议可能会将特定的二进制字节解释为控制字符,从而导致数据损坏.

- 基于文本的协议可能无法正确处理空字节或非打印字符.

而Base64的解决方案是,将二进制数据编码为仅包含可打印字符的ASCII字符串. 这样,编码后的数据可以安全地通过文本传输协议进行传输,而不会被误解或损坏.

### Base64编码和解码原理

Base64编码将每三个字节的二进制数据转换为四个可打印字符. 具体步骤如下:

1. 将输入的二进制数据按每24位(3字节)一组进行划分.(不足3字节的组,在末尾补0)

2. 将每组24位数据分成4个6位的块.

3. 使用Base64字符表将每个6位块映射到对应的可打印字符.(不足4个字符的组,在末尾补'=')

映射表如下:

```java
private static final char[] toBase64 = {
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '/'
};
```

反之,可以实现解码.

### 不同标准

MIME标准规定了Base64编码的行长度限制(每76个字符换行一次),以适应电子邮件等传输协议的要求.而URL和文件名安全的Base64变体则使用不同的字符集(用'-'和'_'代替'+'和'/'),以避免在URL中出现特殊字符.

### 使用示例

可以在markdown中直接使用Base64编码的图片,还是挺有意思的:

<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAABI1JREFUWEetl32IFHUYxz/PrKseiKaJWf2RGFhc7s1ep39JpqihBUl57M6cvWiQCZKBZpGGmJr5hxWBBCZkSne7t3EVJJQm9mYYpd7MehyZQlqHIkppL6De7TzdeLu43u3szB3Nf8vzPN/n+3veVxjipyAtJG5p4vilD5g0YimnrwwFSgZj1ExicozYcoWlAuOLto7CZeAO0B9A3rdxvo6KG4lAjtrhBeIbBVkNDAsD7yV4RtARII+mcY4IaJBNKIEsdfcrxl6B28tBFA4DvwInBa0B7laoF2Tyzc70K4PuxhSdf1QiUZVAK4m5ivEJyKg+Y1VFPhNkvUW7WwmwhcS9BrFXgKduyPVEHJ27iHxXf5tAAjnqaz3Ud1IK+ek4MmsR7WfCUuDLs5iPK5IViF+njh60cedEJtALkAdJFF++18B4OUV7ZxTnJZ0MdSsF453Sb0GfTON+WI4xIAJZktOFQo0S+6bIfLOFu75aIQWR8ls1i+mn7JEi1iELd2Y51gACzSTGGhhnBRmp6Cob9+3BvLq/bhZzCsgJ4FtBt6Rw9wcSyFE7TokvVWQb6D4Ld3415xnMemCZIF2gZwXOehQ6bTp+L7fLkPxJYJrCshjX2so74qYI5Kgd5RE/AnKPwGNpnE+DCLRiPqHwQA1XXlzIib9Lev6wilPoStF57UYtJN8TeFZgyQSc5tnQc6MuyjzkSCQ8YnnATePUB+W9r0O8lRbu8ijpyZBc0Ts5t/e+dkMa57XAIsxQN0cwDii8YeOsDQLPktxVgC2LcU4OhoCiX9i4CwIJtJKYWaz+FRbOu1UItFs4fv4Dvzbq7yrNjFbM1cW6Wm3hvlWNwFwl9qXgNabJt1UhcDKNMyVqa2ZJrgPWjeafsQ9z6mpoBAxkVor263Og0pfBPB+je0aKzlOV5C1MGd/ELxd9mb/IPOIHgX/TuPP7k76pC/whBPwYgcAeQX+zyL9aTqAU9l1MGlm6D7KYzwNbwEtdZviB5zjaHRiBFsz7DKRD8dbY5LdVet3H1E24CgkwskrPnCY6/K4hS91Ug9j5FO0XSnZZ6k1FPzdgR//qD2hD804P6VLYbeMsqUTAnxXK8Jmg4xS2GngLUxw/Wq6bI9HgYTyosLF3k267wqWtQRdThV1gngMuWrjFRTSQxg4a4mPobhCY7WH4R8r3Avvou4weAhaAFgRdlSafqdYtAwhkSH4k0Kj0TLfpOFLNuJXkDIUXQP9UxC+6bt9x7yV07C9i+/vnuxJWpW24GCiuTO9pi/yesGFTvJpGg1eYSP5w+agNsx1AoNg250DGVSvGMOCo8ooXUYbk6wJrFT1v406MCjYUvYoE/D6uYYzTtxUL89IcPzAU8Cg2gTdhhqnThGH+5XvoNpx5g8lrFMcV50B/wwzJJoFmhZ02zrLBAEfVDf1fkMHcJLBOkWcsnN1RF9D/RqBvzF7fZptB3/wZ96UN4EV1EKYXGoESQIa6RpDtIN8pPZtKOyDMQZg8MgEfKEfDGI/uNYrYIFttnJ1hDsLkgyJQDuZ3iUHsVkUvWOSPhTkKkv8HSH6fMJUtKgQAAAAASUVORK5CYII=" alt="gnu-debian-logo">

```html
<img src=
"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAABI1JREFUWEetl32IFHUYxz/PrKseiKaJWf2RGFhc7s1ep39JpqihBUl57M6cvWiQCZKBZpGGmJr5hxWBBCZkSne7t3EVJJQm9mYYpd7MehyZQlqHIkppL6De7TzdeLu43u3szB3Nf8vzPN/n+3veVxjipyAtJG5p4vilD5g0YimnrwwFSgZj1ExicozYcoWlAuOLto7CZeAO0B9A3rdxvo6KG4lAjtrhBeIbBVkNDAsD7yV4RtARII+mcY4IaJBNKIEsdfcrxl6B28tBFA4DvwInBa0B7laoF2Tyzc70K4PuxhSdf1QiUZVAK4m5ivEJyKg+Y1VFPhNkvUW7WwmwhcS9BrFXgKduyPVEHJ27iHxXf5tAAjnqaz3Ud1IK+ek4MmsR7WfCUuDLs5iPK5IViF+njh60cedEJtALkAdJFF++18B4OUV7ZxTnJZ0MdSsF453Sb0GfTON+WI4xIAJZktOFQo0S+6bIfLOFu75aIQWR8ls1i+mn7JEi1iELd2Y51gACzSTGGhhnBRmp6Cob9+3BvLq/bhZzCsgJ4FtBt6Rw9wcSyFE7TokvVWQb6D4Ld3415xnMemCZIF2gZwXOehQ6bTp+L7fLkPxJYJrCshjX2so74qYI5Kgd5RE/AnKPwGNpnE+DCLRiPqHwQA1XXlzIib9Lev6wilPoStF57UYtJN8TeFZgyQSc5tnQc6MuyjzkSCQ8YnnATePUB+W9r0O8lRbu8ijpyZBc0Ts5t/e+dkMa57XAIsxQN0cwDii8YeOsDQLPktxVgC2LcU4OhoCiX9i4CwIJtJKYWaz+FRbOu1UItFs4fv4Dvzbq7yrNjFbM1cW6Wm3hvlWNwFwl9qXgNabJt1UhcDKNMyVqa2ZJrgPWjeafsQ9z6mpoBAxkVor263Og0pfBPB+je0aKzlOV5C1MGd/ELxd9mb/IPOIHgX/TuPP7k76pC/whBPwYgcAeQX+zyL9aTqAU9l1MGlm6D7KYzwNbwEtdZviB5zjaHRiBFsz7DKRD8dbY5LdVet3H1E24CgkwskrPnCY6/K4hS91Ug9j5FO0XSnZZ6k1FPzdgR//qD2hD804P6VLYbeMsqUTAnxXK8Jmg4xS2GngLUxw/Wq6bI9HgYTyosLF3k267wqWtQRdThV1gngMuWrjFRTSQxg4a4mPobhCY7WH4R8r3Avvou4weAhaAFgRdlSafqdYtAwhkSH4k0Kj0TLfpOFLNuJXkDIUXQP9UxC+6bt9x7yV07C9i+/vnuxJWpW24GCiuTO9pi/yesGFTvJpGg1eYSP5w+agNsx1AoNg250DGVSvGMOCo8ooXUYbk6wJrFT1v406MCjYUvYoE/D6uYYzTtxUL89IcPzAU8Cg2gTdhhqnThGH+5XvoNpx5g8lrFMcV50B/wwzJJoFmhZ02zrLBAEfVDf1fkMHcJLBOkWcsnN1RF9D/RqBvzF7fZptB3/wZ96UN4EV1EKYXGoESQIa6RpDtIN8pPZtKOyDMQZg8MgEfKEfDGI/uNYrYIFttnJ1hDsLkgyJQDuZ3iUHsVkUvWOSPhTkKkv8HSH6fMJUtKgQAAAAASUVORK5CYII=" 
alt="gnu-debian-logo">
```

Java的`java.util.Base64`类提供了Base64编码和解码的功能,位于`java.util`包中.该类包含静态方法来获取编码器和解码器实例,并提供了多种编码和解码选项,如基本编码、URL文件名安全编码以及MIME编码.

## 内部实现

核心组件就是编码器和解码器接口,以及它们的具体实现类.

### 编码器

首先会根据不同的标准计算所需的输出长度,然后创建合适大小的输出字节数组.编码器按3字节一组处理输入数据,并将其映射为4个Base64字符. 对于剩余的1或2个字节,它会根据需要添加填充字符'='.

```java
public static class Encoder {
    // ...

    private final int encodedOutLength(int srclen, boolean throwOOME) {
        int len = 0;
        try {
            if (doPadding) {
                len = Math.multiplyExact(4, (Math.addExact(srclen, 2) / 3));
                // 每3个字节编码为4个字符,向上取整
                // 在jdk-1.8中都没使用Math,是这样写的:
                // len = 4 * ((srclen + 2) / 3);
            } else {
                int n = srclen % 3;
                len = Math.addExact(Math.multiplyExact(4, (srclen / 3)), (n == 0 ? 0 : n + 1));
                // 不使用填充时,剩余1个字节编码为2个字符,剩余2个字节编码为3个字符
            }
            if (linemax > 0) {                             // line separators
                len = Math.addExact(len, (len - 1) / linemax * newline.length);
            }
        } catch (ArithmeticException ex) {
            if (throwOOME) {
                throw new OutOfMemoryError("Encoded size is too large");
            } else {
                // let the caller know that encoded bytes length
                // is too large
                len = -1;
            }
        }
        return len;
    }

    private int encode0(byte[] src, int off, int end, byte[] dst) {
        char[] base64 = isURL ? toBase64URL : toBase64;
        int sp = off;
        int slen = (end - off) / 3 * 3;
        int sl = off + slen;
        if (linemax > 0 && slen  > linemax / 4 * 3)
            slen = linemax / 4 * 3;
        int dp = 0;
        while (sp < sl) {   // 好像只会进行1次循环啊
            int sl0 = Math.min(sp + slen, sl);  // 不是相等的吗?
            encodeBlock(src, sp, sl0, dst, dp, isURL);
            int dlen = (sl0 - sp) / 3 * 4;
            dp += dlen;
            sp = sl0;
            if (dlen == linemax && sp < end) {
                for (byte b : newline){
                    dst[dp++] = b;
                }
            }
        }
        if (sp < end) {               // 1 or 2 leftover bytes
            int b0 = src[sp++] & 0xff;
            dst[dp++] = (byte)base64[b0 >> 2];  // 第1个字节
            if (sp == end) {
                dst[dp++] = (byte)base64[(b0 << 4) & 0x3f]; // 第2个字节
                if (doPadding) {
                    dst[dp++] = '=';    // 第3个字节
                    dst[dp++] = '=';    // 第4个字节
                }
            } else {
                int b1 = src[sp++] & 0xff;
                dst[dp++] = (byte)base64[(b0 << 4) & 0x3f | (b1 >> 4)]; // 第2个字节
                dst[dp++] = (byte)base64[(b1 << 2) & 0x3f]; // 第3个字节
                if (doPadding) {
                    dst[dp++] = '=';    // 第4个字节
                }
            }
        }
        return dp;
    }
}
```

编码器的核心方法是`encode0`,它负责将输入的字节数组转换为Base64编码的字节数组. 该方法按3字节一组处理输入数据,并将其映射为4个Base64字符. 对于剩余的1或2个字节,它会根据需要添加填充字符'='.

### 解码器

首先会根据不同的标准创建一个查找表,用于将Base64字符映射回其对应的6位二进制值.计算所需的输出长度,然后创建合适大小的输出字节数组.解码器按4个Base64字符一组处理输入数据,将其转换回3个字节的二进制数据. 它会忽略填充字符'='并正确处理输入中的无效字符.

```java
public static class Decoder {
    // ...

    /**
     * Lookup table for decoding "URL and Filename safe Base64 Alphabet"
     * as specified in Table2 of the RFC 4648.
     */
    private static final int[] fromBase64URL = new int[256];

    static {
        Arrays.fill(fromBase64URL, -1);
        for (int i = 0; i < Encoder.toBase64URL.length; i++)
            fromBase64URL[Encoder.toBase64URL[i]] = i;
        fromBase64URL['='] = -2;
    }

    private int decode0(byte[] src, int sp, int sl, byte[] dst) {
        int[] base64 = isURL ? fromBase64URL : fromBase64;
        int dp = 0;
        int bits = 0;
        int shiftto = 18;       // pos of first byte of 4-byte atom

        while (sp < sl) {   // 难道不是只会进行1次循环吗?
            if (shiftto == 18 && sp < sl - 4) {       // fast path
                int dl = decodeBlock(src, sp, sl, dst, dp, isURL, isMIME);
                /*
                    * Calculate how many characters were processed by how many
                    * bytes of data were returned.
                    */
                int chars_decoded = ((dl + 2) / 3) * 4;

                sp += chars_decoded;
                dp += dl;
            }
            if (sp >= sl) {
                // we're done
                break;
            }
            int b = src[sp++] & 0xff;
            if ((b = base64[b]) < 0) {  // 这部分都属于有点异常情况的处理
                if (b == -2) {         // padding byte '='
                    // =     shiftto==18 unnecessary padding
                    // x=    shiftto==12 a dangling single x
                    // x     to be handled together with non-padding case
                    // xx=   shiftto==6&&sp==sl missing last =
                    // xx=y  shiftto==6 last is not =
                    if (shiftto == 6 && (sp == sl || src[sp++] != '=') ||
                        shiftto == 18) {
                        throw new IllegalArgumentException(
                            "Input byte array has wrong 4-byte ending unit");
                    }
                    break;
                }
                if (isMIME)    // skip if for rfc2045
                    continue;
                else
                    throw new IllegalArgumentException(
                        "Illegal base64 character " +
                        Integer.toString(src[sp - 1], 16));
            }
            bits |= (b << shiftto);
            shiftto -= 6;
            if (shiftto < 0) {
                dst[dp++] = (byte)(bits >> 16);
                dst[dp++] = (byte)(bits >>  8);
                dst[dp++] = (byte)(bits);
                shiftto = 18;
                bits = 0;
            }
        }
        // reached end of byte array or hit padding '=' characters.
        if (shiftto == 6) {
            dst[dp++] = (byte)(bits >> 16);
        } else if (shiftto == 0) {
            dst[dp++] = (byte)(bits >> 16);
            dst[dp++] = (byte)(bits >>  8);
        } else if (shiftto == 12) {
            // dangling single "x", incorrectly encoded.
            throw new IllegalArgumentException(
                "Last unit does not have enough valid bits");
        }
        // anything left is invalid, if is not MIME.
        // if MIME, ignore all non-base64 character
        while (sp < sl) {
            if (isMIME && base64[src[sp++] & 0xff] < 0)
                continue;
            throw new IllegalArgumentException(
                "Input byte array has incorrect ending byte at " + sp);
        }
        return dp;
    }
}
```

解码器的核心方法是`decode0`,它负责将Base64编码的字节数组转换回原始的二进制字节数组. 该方法按4个Base64字符一组处理输入数据,将其转换回3个字节的二进制数据. 它会忽略填充字符'='并正确处理输入中的无效字符.

## 总结

这次我们通过阅读`java.util.Base64`类的源码,深入了解了Base64编码和解码的实现原理. 该类通过高效的算法和灵活的选项,为Java开发者提供了方便的Base64处理功能. 理解其内部工作机制有助于我们更好地应用和优化Base64相关的操作.
