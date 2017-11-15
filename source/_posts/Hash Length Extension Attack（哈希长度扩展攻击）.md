---
title: Hash Length Extension Attack（哈希长度扩展攻击）
date: 2017-11-12 09:22:34
tags: [vulnerability,crypto,web,audit,CTF,writeup]
categories: [InfoSec,Crypto]
mathjax: true
---

# 0x00 前言

**[Hash Length Extension Attack](https://en.wikipedia.org/wiki/Length_extension_attack)（[哈希长度扩展攻击](https://zh.wikipedia.org/w/index.php?title=%E9%95%BF%E5%BA%A6%E6%89%A9%E5%B1%95%E6%94%BB%E5%87%BB)）**是针对采用了 [Merkle–Damgård 结构](https://en.wikipedia.org/wiki/Merkle%E2%80%93Damg%C3%A5rd_construction)的哈希函数的攻击手段，如 MD5、SHA-1 和 SHA-2 等。该攻击可以伪造消息散列值，产生新的合法数字签名，对数据的完整性和不可否认性造成严重威胁。

本文以 MD5 为例，在 0x01 节先介绍 MD5 与 Hash Length Extension Attack 的基本原理，在 0x02 节介绍攻击工具 HashPump 的使用，最后在 0x03 节借助相关的 CTF 题目来展示此漏洞的利用方法。阅读本文需要**理解 MD5 加密原理**，以及**掌握Linux下的工具使用**。

<!-- more -->

# 0x01 理论基础

为了便于后续理解，所以在介绍 Hash Length Extension Attack 之前，先简单介绍一下 MD5 的加密流程。

## MD5 Hash Function

[MD5](https://en.wikipedia.org/wiki/MD5) 算法由美国麻省理工密码学家 [Ronald Rivest](https://en.wikipedia.org/wiki/Ron_Rivest) 在 MD2、MD3 与 MD4 的基础上设计而成，并在 1992 年公开发表，在规范 [RFC 1321](https://tools.ietf.org/html/rfc1321) 中作了详尽阐述。

MD5 算法的输入为长度小于 $2^{64} \ bit$ 的消息比特串，输出为固定 $128 \ bit$ 的消息散列值。输入的数据以 $512 \ bit$ 为分组进行处理。MD5 算法流程如下图所示。

![md5_process](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/md5_process.jpg)

其中 $L$ 是消息比特串；$N$ 是消息扩充后的分组个数；$M_i$ 是第 $i$ 个分组，$0 \le i \le N-1$；$IV$ 是 $128 \ bit$ 的初始链接变量，由 4 个 $32 \ bit$ 的寄存器构成；$CV_i$ 是链接变量，代表第 $i$ 个分组单元的输入，而最后一个单元 $B_{N-1}$ 的输出 $CV_N$ 即为消息的散列值。算法具体流程如下：

### （1）附加填充

先填充一个“1”比特和若干个“0”比特使消息长度在模 512 下与 448 同余，再将消息的原始长度用一个 $64 \ bit$ 的整型表示，以[小端字节序（Little-Endian）](https://en.wikipedia.org/wiki/Endianness#Little)的方式继续填充，使得扩充后的消息长度为 $512 \ bit$ 的整数倍，可表示为：

$$
\begin{cases}
L + padding_1 + padding_2 = N \times 512  \\
L + padding_1 \equiv 448 \ mod \ 512  \\
\end{cases}
$$

其中 $L$ 是消息比特串；$padding_1$ 是比特串 "$100 \cdots 00$" 的长度；$padding_2$ 恒为 $64 \ bit$，代表原始消息长度。各自的取值范围如下：

$$
\begin{cases}
0 \le L \lt 2^{64}  \\
0 \lt padding_1 \le 512  \\
padding_2 = 64
\end{cases}
$$

下面举例说明，假设要对字符串“hello world”进行附加填充：

![example1](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/example1.jpg)

可见消息比特串长度为 $11 \ Byte$，即 $88 \ bit$，因此在第 $89 \ bit$ 处填充"1"比特，然后填充“0”比特直至长度为 $448 \ bit$，而原始长度 $88 \ bit$ 的十六进制为 $0x58 \ bit$，根据小端原则应放在低地址 $0x00000038$ 处，而高地址全部为 $0x00$。

**注意，附加填充对任何消息比特串来说都是必须的，即使消息原始长度恰为 $448 \ bit$：**

![example2](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/example2.jpg)

即使消息比特串长度为 $56 \ Byte$，即 $448 \ bit$，也要在第 $449 \ bit$ 处填充"1"比特，然后填充“0”比特直至下一分组单元长度为 $448 \ bit$，而原始长度 $448 \ bit$ 的十六进制为 $0x01B0 \ bit$，根据小端原则低地址 $0x00000078$ 处为 $0xB0$，$0x00000079$ 处为 $0x01$，而高地址全部为 $0x00$。

### （2）初始链接变量

初始链接变量 $IV$ 在最开始存于 4 个 $32 \ bit$ 的寄存器 $A、B、C、D$ 中，将参与第一个分组单元的哈希运算，它们分别为：

$$
\begin{cases}
A = 0x01234567  \\
B = 0x89ABCDEF  \\
C = 0xFEDCBA98  \\
D = 0x76543210
\end{cases}
$$

**注意，这些值都是以小端字节序存放在各个寄存器中，而实际上它们的值为以下 32 位整型数（对于链接变量 $CV_i$ 也同理，注意实际值与内存中存储值的区别）：**

$$
\begin{cases}
A = 0x67452301  \\
B = 0xEFCDAB89  \\
C = 0x98BADCFE  \\
D = 0x10325476
\end{cases}
$$

### （3）分组单元迭代压缩

每个分组单元 $M_i$ 的迭代压缩由 4 轮组成，将 $512 \ bit$ 的分组单元均分为 16 个子分组参与每轮的 16 步函数运算，每步函数的输入为 4 个 $32 \ bit$ 的整型变量和 1 个 $32 \ bit$ 的子分组，输出也为 4 个 $32 \ bit$ 的整型变量，作为下一步函数的输入。经过 4 轮共 64 步函数运算后，将 4 个 $32 \ bit$ 寄存器中的结果分别与相应输入链接变量在模 $2^{32}$ 下相加，即得到该分组单元的输出链接变量。若为最后一个分组，则输出为消息的散列值。

![iteration](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/iteration.jpg)

**注意，在第 1 轮开始前，要将输入链接变量 $A、B、C、D$ 的值复制到暂存变量  $AA、BB、CC、DD$ 中，便于 4 轮运算结束后与结果进行模加。**

### （4）步函数

MD5 迭代压缩算法每一轮都包含 16 步函数运算，同一轮中的步函数使用相同的非线性函数，不同轮之间非线性函数是不同的。设输入 $B、C、D$ 是 3 个 $32 \ bit$ 的整型变量，输出是 1 个 $32 \ bit$ 的整型变量，则每一轮的非线性函数 $F、G、H、I$ 分别定义如下：

$$
\begin{cases}
F(B,C,D) = (B \land C) \lor (\lnot B \land D)  \\
G(B,C,D) = (B \land D) \lor (C \land \lnot D)  \\
H(B,C,D) = B \oplus C \oplus D  \\
I(B,C,D) = C \oplus (B \lor \lnot D)
\end{cases}
$$

其中 $\land、\lor、\lnot、\oplus$ 分别为与、或、非、异或逻辑运算。

![step_function](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/step_function.jpg)

其中 $M[j]$ 表示分组单元 $M_i$ 的第 $j$ 个 $32 \ bit$ 子分组，$0 \le j \le 15$；$<<< s$ 表示循环左移 $s$ 位；$T[i]$ 是一个伪随机常数，$1 \le i \le 64$，用于消除输入数据的规律性，其构造方法与具体取值请见规范 RFC 1321。

上图为步函数的流程，先取输入整型变量 $B、C、D$ 作为参数执行一次非线性函数，将结果依次加上 $A、M[j]、T[i]$，再将结果循环左移 $s$ 位后加上 $B$，把最终结果赋值给 $B$，而 $B、C、D$ 的输入值依次赋值给 $C、D、A$，得到输出整型变量，作为下一次步函数的输入。上述加法均在模 $2^{32}$ 下。

## Hash Length Extension Attack

### 漏洞原理

**Hash Length Extension Attack** 适用于采用了 Merkle–Damgård 结构的哈希函数，在攻击者不知道 $secret$ 的情况下，已知 $message1$ 与 $MD5(secret \ || \ message1)$，可以推算出 $MD5(secret \ || \ message1 \ || \ padding1 \ || \ message2)$ 的值。

其中 $||$ 是字符串连接符；$message1$ 是用户需要计算散列值的明文消息；$secret$ 是哈希运算中与明文消息一起计算的私密字符串，相当于消息认证码中的 $key$，或者加“盐”哈希中的 $salt$；$padding1$ 是计算 $MD5(secret \ || \ message1)$ 时的填充字节；$message2$ 是攻击者构造的任意字符串。

**注意，由于要根据 $MD5(secret \ || \ message1)$ 推算 $MD5(secret \ || \ message1 \ || \ padding1 \ || \ message2)$，因此 $secret$ 和 $message1$ 的长度必须知道。换句话说，需要知道 $(secret \ || \ message1 \ || \ padding1)$ 有多少字节才能构造出 $padding2$，即计算 $MD5(secret \ || \ message1 \ || \ padding1 \ || \ message2)$ 时的填充字节，因为 $padding2$ 包含了 $(secret \ || \ message1 || \ padding1 \ || \ message2)$ 的总长度。**

道哥在《白帽子讲Web安全》的 **[Understanding MD5 Length Extension Attack](http://blog.chinaunix.net/uid-27070210-id-3255947.html)** 一文中对此攻击作了详细叙述，本文就其中的 PoC 举例作出讲解。

![poc](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/poc.jpg)

为了方便说明，上图 PoC 中只有 $secret$，省略了 $message1$。可见，此处的 $secret$ 为随机产生的一个小数字符串，长度为 $18 \ Byte$，即 $144 \ bit$， $MD5(secret)$ 与 $padding1$ 如上图所示，任意值 $message2$ 此处取为“Welcome to Secrypt Agency!”，攻击得到的散列值与 $MD5(secret \ || \ padding1 \ || \ message2)$ 相等，表示攻击成功。

**注意，这里的 $h0、h1、h2、h3$ 分别为上述的 $A、B、C、D$，并且用有符号 $32 \ bit$ 整型数表示。**如 run time = 0 时的 $h0$：

$$h0 = 841628852 = 0x322a3cb4$$

其小端字节序正好对应散列值的前 $4 \ Byte$，即 $b43c2a32$。对于负数，其补码表示的正数与其在模 $2^{32}$ 下同余的正数相等，如 run time = 0 时的 $h2$：

$$h2 = -474181071 \equiv 3820786225 \ mod \ 2^{32} = 0xe3bc9231$$

其小端字节序对应散列值的第 $9$ ~ $12 \ Byte$，即 $3192bce3$。

此处纠正 Understanding MD5 Length Extension Attack 文中 PoC 源代码中的一处错误，在 md5_le.js 文件的 159 行，`i = parseInt(m_len / 64) + 1` 并非恒成立，当 `m_len % 64 >= 56` 时，附加填充将会多占用一个字节，此时应为 `i = parseInt(m_len / 64) + 2`。**解决方案：在循环前先判断变量 i 的取值。**

``` javascript
for (i = parseInt(m_len/64)+1; i < databytes.length / 64; i++)
```

### 漏洞修复

Hash Length Extension Attack 是 Merkle–Damgård 结构的固有缺陷，只要采用了此结构的哈希函数都会存在此漏洞。因此没有药到病除的方法，只有以下几条权宜之计供参考：

1.  **采用 HAMC、SHA-3 等**非 Merkle–Damgård 结构或不受其影响的哈希算法；
2.  **将 $secret$ 值放在参数末尾。**若已知 $MD5(message1 \ || \ secret)$，要求出 $MD5(message1 \ || \ secret \ || \ padding1 \ || \ message2)$ 是很困难的，因为 $secret$ 的附加策略是在参数末尾，所以只会得到 $MD5(message1 \ || \ padding1^{'} \ || \ message2 \ || \ secret)$，在 $secret$ 未知的情况下是求不出该值的。

# 0x02 HashPump

[HashPump](https://github.com/bwall/HashPump) 是基于 OpenSSL 的哈希长度扩展攻击工具，支持对 MD5、SHA-1、SHA-256、SHA-512 等哈希函数的攻击利用。

以下只介绍在 Kali Linux 使用环境下的安装流程，以下命令需要用 `root` 权限完成：

``` shell
$ git clone https://github.com/bwall/HashPump.git
$ apt-get update
$ apt-get install g++ libssl-dev
$ cd HashPump
$ make
$ make install
```

安装完成后，输入以下命令，即可得到 HashPump 的用法帮助：

``` shell
$ hashpump -h
HashPump [-h help] [-t test] [-s signature] [-d data] [-a additional] [-k keylength]
    HashPump generates strings to exploit signatures vulnerable to the Hash Length Extension Attack.
    -h --help          Display this message.
    -t --test          Run tests to verify each algorithm is operating properly.
    -s --signature     The signature from known message.
    -d --data          The data from the known message.
    -a --additional    The information you would like to add to the known message.
    -k --keylength     The length in bytes of the key being used to sign the original message with.
    Version 1.2.0 with CRC32, MD5, SHA1, SHA256 and SHA512 support.
    <Developed by bwall(@botnet_hunter)>
```

# 0x03 writeups

介绍完 Hash Length Extension Attack 的原理与 HashPump 工具的使用方法后，下面借助相关的 CTF 题目来展示该漏洞的实际利用过程。

## 【实验吧CTF】 Web —— 让我进去

此题结合了 PHP 的代码审计与 Hash Length Extension Attack，难度中等，需要的基础知识有：**PHP、Linux、HTTP协议、MD5加密原理**。相关链接如下：

- 题目链接：[http://www.shiyanbar.com/ctf/1848](http://www.shiyanbar.com/ctf/1848)
- 解题链接：[http://ctf5.shiyanbar.com/web/kzhan.php](http://ctf5.shiyanbar.com/web/kzhan.php)

![lmi_question](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/lmi_question.jpg)

进入解题链接，发现如下输入框，任意输入一些值，或尝试注入，均无报错信息，且源码也无干货。

![lmi_input](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/lmi_input.jpg)

![lmi_source1](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/lmi_source1.jpg)

接下来查看它的 HTTP 请求头，发现有两个属于题目本域的异常 Cookie，分别为：`sample-hash = 571580b26c65f306376d4f64e53cb5c7` 和 `source = 0`。

![lmi_cookie](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/lmi_cookie.jpg)

尝试用 BurpSuite 把 `source` 的值改为 1，再次发出请求，果然得到了真正的源代码：

![lmi_source2](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/lmi_source2.jpg)

由以下语句可知 Cookie `sample-hash` 原来是 `$secret` 与 “adminadmin” 连接而成的字符串的 MD5 散列值，即上述的 $MD5(secret || message1)$， `$secret` 为 $15 \ Byte$ 长的字符串 $secret$，“adminadmin” 为 $message1$。

``` php
setcookie("sample-hash", md5($secret . urldecode("admin" . "admin")), time() + (60 * 60 * 24 * 7));
```

又由以下核心语句，得知爆 flag 的条件是设置一个新 Cookie `getmein`，它的值要与 `$secret + $username + $password` 组成的字符串的 MD5 散列值相等，但前面还有一个限制条件：`$username` 的值要等于 “admin”，且 `$password` 不能等于 “admin”。想到这里，就可知此题是要用 Hash Length Extension Attack 来伪造新的散列值绕过验证。

``` php
if (!empty($_COOKIE["getmein"])) {
    if (urldecode($username) === "admin" && urldecode($password) != "admin") {
        if ($COOKIE["getmein"] === md5($secret . urldecode($username . $password))) {
            echo "Congratulations! You are a registered user.\n";
            die ("The flag is ". $flag);
        }
        else {
            die ("Your cookies don't match up! STOP HACKING THIS SITE.");
        }
    }
    else {
        die ("You are not an admin! LEAVE.");
    }
}
```
首先要理清代码中的变量与 Hash Length Extension Attack 中变量的对应关系，下面用 HashPump 展示说明该漏洞的攻击过程：

![lmi_hashpump](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/lmi_hashpump.jpg)

其中 **Input Signature** 是 $MD5(secret \ || \ message1)$，**Input Data** 是 $message1$，**Input Key Length** 等于 15，**Input Data to Add** 是 $message2$。得到的结果 `ca78a24c34c2e13331e7b0425b567b09` 为 $MD5(secret \ || \ message1 \ || \ padding1 \ || \ message2)$。

最后，我们只要构造攻击 payload，在 Username 和 Password 框中输入，再创建一个新 Cookie `getmein = ca78a24c34c2e13331e7b0425b567b09`，Submit 后即能得到 flag 。构造的 payload 如下：

```
Username：admin
Password：admin\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc8\x00\x00\x00\x00\x00\x00\x00ciphersaw
```

但注意到源码在判断之前先用 `urldecode()` 函数对 `$username` 和 `$password` 进行 URL 解码，因此要把以上 payload 转换成 URL 编码形式：

```
Username：%61%64%6d%69%6e
Password：%61%64%6d%69%6e%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%c8%00%00%00%00%00%00%00%63%69%70%68%65%72%73%61%77
```

正确输入 payload 后，成功得到 flag：

![lmi_flag](http://oyhh4m1mt.bkt.clouddn.com/Hash_Length_Extension_Attack/lmi_flag.jpg)
