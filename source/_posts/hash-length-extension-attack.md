---
title: Hash Length Extension Attack（哈希长度扩展攻击）
date: 2017-11-12 09:22:34
tags: [实验吧,CTF,Writeup,Vulnerability,Crypto,MD5,Web,PHP,Python,Audit]
categories: [InfoSec,Crypto]
copyright: true
mathjax: true
---

# 0x00 前言

**[Hash Length Extension Attack](https://en.wikipedia.org/wiki/Length_extension_attack)（[哈希长度扩展攻击](https://zh.wikipedia.org/w/index.php?title=%E9%95%BF%E5%BA%A6%E6%89%A9%E5%B1%95%E6%94%BB%E5%87%BB)）**是针对采用了 [Merkle–Damgård 结构](https://en.wikipedia.org/wiki/Merkle%E2%80%93Damg%C3%A5rd_construction)的哈希函数的攻击手段，如 MD5、SHA-1 和 SHA-2 等。该攻击可以伪造消息散列值，产生新的合法数字签名，对数据的完整性和不可否认性造成严重威胁。

本文以 MD5 为例，0x01 介绍 MD5 的基本原理；0x02 介绍 Hash Length Extension Attack 的漏洞原理与漏洞修复方法，并在假设场景下展示了漏洞利用过程；0x03 介绍攻击工具 HashPump 的使用；0x04 借助相关的 CTF 题目来展示此漏洞的利用方法。

阅读本文需要**理解 MD5 哈希函数的原理**，以及**在 Linux 下熟练使用命令行工具**。

<!-- more -->

# 0x01 MD5 Hash Function

为了后续更好地理解 Hash Length Extension Attack，首先简单介绍一下 MD5 的算法流程。

[MD5](https://en.wikipedia.org/wiki/MD5) 算法由美国麻省理工密码学家 [Ronald Rivest](https://en.wikipedia.org/wiki/Ron_Rivest) 在 MD2、MD3 与 MD4 的基础上设计而成，并在 1992 年公开发表，在规范 [RFC 1321](https://tools.ietf.org/html/rfc1321) 中作了详尽阐述。

MD5 算法的输入为长度小于 $2^{64} \ bit$ 的消息比特串，输出为固定 $128 \ bit$ 的消息散列值，输入数据需要以 $512 \ bit$ 为单位进行分组。

MD5 算法的流程图如下：

![md5-process](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/md5-process.jpg)

-  $L$ 是消息比特串的原始长度；

-  $N$ 是消息扩充后的分组个数；

-  $M_i$ 是消息扩充后的第 $i$ 个分组，$0 \le i \le N-1$；

-  $IV$ 是 $128 \ bit$ 的初始链接变量，由 4 个 $32 \ bit$ 的寄存器构成；

-  $CV_i$ 是链接变量，代表 $M_i$ 分组单元的输入，也是 $M_{i-1}$ 分组单元的输出，$1 \le i \le N-1$。**注意，最后一个分组单元 $M_{N-1}$ 的输出 $CV_N$ 即为消息的散列值。**

MD5 算法的具体流程描述如下：

## Step 1 附加填充

先填充一个「1」比特和若干个「0」比特使消息长度在模 512 下与 448 同余，再将消息的原始长度用一个 $64 \ bit$ 的整型表示，以[小端字节序（Little-Endian）](https://en.wikipedia.org/wiki/Endianness#Little)的方式继续填充，使得扩充后的消息长度为 $512 \ bit$ 的整数倍，可表示为：

$$
\begin{cases}
L + padding\_seq + padding\_len = N \times 512  \\\\
L + padding\_seq \equiv 448 \ mod \ 512  \\\\
\end{cases}
$$

- $L$ 是消息比特串的原始长度；
- $padding\_seq$ 是比特串「$100 \cdots 00$」的长度；
- $padding\_len$ 恒为 $64 \ bit$，代表原始消息长度。

各自的取值范围如下：

$$
\begin{cases}
0 \le L \lt 2^{64}  \\\\
1 \le padding\_seq \le 512  \\\\
padding\_len = 64
\end{cases}
$$

下面举例说明，假设要对字符串「hello world」进行附加填充：

![example1](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/example1.jpg)

可见消息比特串长度为 $11 \ Byte$，即 $88 \ bit$，因此在第 $89 \ bit$ 处填充「1」比特，然后填充「0」比特直至长度为 $448 \ bit$，而原始长度 $88 \ bit$ 的十六进制为 $0x58 \ bit$，根据小端原则应放在低地址 $0x00000038$ 处，而高地址全部为 $0x00$。

**注意，附加填充对任何消息比特串来说都是必须的，即使消息原始长度恰为 $448 \ bit$：**

![example2](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/example2.jpg)

即使消息比特串长度为 $56 \ Byte$，即 $448 \ bit$，也要在第 $449 \ bit$ 处填充「1」比特，然后填充「0」比特直至下一分组单元长度为 $448 \ bit$，而原始长度 $448 \ bit$ 的十六进制为 $0x01C0 \ bit$，根据小端原则低地址 $0x00000078$ 处为 $0xC0$，$0x00000079$ 处为 $0x01$，而高地址全部为 $0x00$。

## Step 2 初始链接变量

初始链接变量 $IV$ 在最开始存于 4 个 $32 \ bit$ 的寄存器 $A、B、C、D$ 中，将参与第一个分组单元的哈希运算，它们分别为：

$$
\begin{cases}
A = 0x01234567  \\\\
B = 0x89ABCDEF  \\\\
C = 0xFEDCBA98  \\\\
D = 0x76543210
\end{cases}
$$

**注意，这些值都是以小端字节序存放在各个寄存器中，而实际上它们的值为以下 32 位整型数（对于链接变量 $CV_i$ 也同理，注意实际值与内存中存储值的区别）：**

$$
\begin{cases}
A = 0x67452301  \\\\
B = 0xEFCDAB89  \\\\
C = 0x98BADCFE  \\\\
D = 0x10325476
\end{cases}
$$

## Step 3 分组单元迭代压缩

每个分组单元 $M_i$ 的迭代压缩由 4 轮组成，将 $512 \ bit$ 的分组单元均分为 16 个子分组参与每轮 16 次的步函数运算，每次步函数的输入为 4 个 $32 \ bit$ 的整型变量和 1 个 $32 \ bit$ 的子分组，输出也为 4 个 $32 \ bit$ 的整型变量，作为下一次步函数的输入。经过 4 轮共 64 次的步函数运算后，将 4 个 $32 \ bit$ 寄存器中的结果分别与相应输入链接变量在模 $2^{32}$ 下相加，即得到该分组单元的输出链接变量。若为最后一个分组，则输出为消息的散列值。

![iteration](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/iteration.jpg)

**注意，在第 1 轮开始前，要将输入链接变量 $A、B、C、D$ 的值复制到暂存变量  $AA、BB、CC、DD$ 中，便于 4 轮运算结束后与结果进行模加。**

## Step 4 步函数

MD5 迭代压缩算法每一轮都包含 16 次的步函数运算，同一轮中的步函数使用相同的非线性函数，不同轮之间非线性函数是不同的。设输入 $B、C、D$ 是 3 个 $32 \ bit$ 的整型变量，输出是 1 个 $32 \ bit$ 的整型变量，则每一轮的非线性函数 $F、G、H、I$ 分别定义如下：

$$
\begin{cases}
F(B,C,D) = (B \land C) \lor (\lnot B \land D)  \\\\
G(B,C,D) = (B \land D) \lor (C \land \lnot D)  \\\\
H(B,C,D) = B \oplus C \oplus D  \\\\
I(B,C,D) = C \oplus (B \lor \lnot D)
\end{cases}
$$

其中 $\land、\lor、\lnot、\oplus$ 分别为与、或、非、异或逻辑运算。

![step-function](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/step-function.jpg)

- $M[j]$ 表示当前分组单元 $M$ 的第 $j$ 个 $32 \ bit$ 子分组，$0 \le j \le 15$；
- $<<< s$ 表示循环左移 $s$ 位；
- $T[i]$ 是一个伪随机常数，用于消除输入数据的规律性，$1 \le i \le 64$，$i$ 对应着 4 轮共 64 次步函数的执行顺序，其构造方法与具体取值请见规范 [RFC 1321](https://tools.ietf.org/html/rfc1321)。

上图为步函数的具体流程：先取输入整型变量 $B、C、D$ 作为参数执行一次非线性函数，将结果依次加上 $A、M[j]、T[i]$，再将结果循环左移 $s$ 位后加上 $B$，把最终结果赋值给 $B$，而 $B、C、D$ 的输入值依次赋值给 $C、D、A$，得到本次步函数的输出，同时也作为下一次步函数的输入。上述加法运算均在模 $2^{32}$ 下。

# 0x02 Hash Length Extension Attack

## 漏洞原理

**Hash Length Extension Attack** 适用于采用了 Merkle–Damgård 结构的哈希函数，攻击者在不知道 $secret$ 具体的值，但知道其长度的情况下，若已知 $message1$ 与 $MD5(secret \ || \ message1)$，可以推算出 $MD5(secret \ || \ message1 \ || \ padding1 \ || \ message2)$ 的值。

- $||$ 是字符串连接符；
- $message1$ 是用户需要计算散列值的明文消息；
- $secret$ 是哈希运算中与明文消息一起计算的私密字符串，相当于消息认证码中的 $key$，或者加「盐」哈希中的 $salt$；
- $padding1$ 是计算 $MD5(secret \ || \ message1)$ 时的附加填充；
- $message2$ 是攻击者构造的任意字符串。

**注意，若要根据 $MD5(secret \ || \ message1)$ 推算 $MD5(secret \ || \ message1 \ || \ padding1 \ || \ message2)$，则必须要知道 $secret$ 和 $message1$ 的长度，因为要先计算 $padding1$ 中 $(secret \ || \ message1)$ 的长度，才能得出 $padding2$ 中 $(secret \ || \ message1 || \ padding1 \ || \ message2)$ 的总长度，其中 $padding2$ 是计算 $MD5(secret \ || \ message1 \ || \ padding1 \ || \ message2)$ 时的附加填充。**

道哥在《白帽子讲Web安全》的 **[Understanding MD5 Length Extension Attack](http://blog.chinaunix.net/uid-27070210-id-3255947.html)** 一文中对此攻击作了详细叙述，本文就其中的 PoC 举例作出讲解。

![poc](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/poc.jpg)

为了方便说明，上图 PoC 中只有 $secret$，省略了 $message1$。可见，此处的 $secret$ 为随机产生的一个小数字符串，长度为 $18 \ Byte$，即 $144 \ bit$， $MD5(secret)$ 与 $padding1$ 如上图所示，任意值 $message2$ 此处取为「Welcome to Secrypt Agency!」。攻击后得到的散列值与 $MD5(secret \ || \ padding1 \ || \ message2)$ 相等，表示攻击成功。

**注意，这里的 $h0、h1、h2、h3$ 分别为上述的 $A、B、C、D$，并且用 $32 \ bit$ 有符号整型数表示。**如 run time = 0 时的 $h0$：

$$
h0 = 841628852 = 0x322a3cb4
$$

其小端字节序正好对应散列值的第 $1$ ~ $4 \ Byte$，即 $0xb43c2a32$。对于负数，其补码表示的正数与其在模 $2^{32}$ 下同余的正数相等，如 run time = 0 时的 $h2$：

$$
h2 = -474181071 \equiv 3820786225 \ mod \ 2^{32} = 0xe3bc9231
$$

其小端字节序对应散列值的第 $9$ ~ $12 \ Byte$，即 $0x3192bce3$。

此处纠正 Understanding MD5 Length Extension Attack 文中 PoC 源代码中的一处错误，在 md5_le.js 文件的 159 行：

``` javascript
for (i = parseInt(m_len/64)+1; i < databytes.length / 64; i++)
```

其中 `i = parseInt(m_len / 64) + 1` 并非恒成立，当 $56 \le m\_len \ \% \ 64 \lt 64$ 时，附加填充将会多占用一个字节，此时应为 `i = parseInt(m_len / 64) + 2`。

**解决方案：在循环前先判断变量 `m_len` 的范围，再决定变量 `i` 的取值。**

## 漏洞利用 

假设已登录用户要在某个网站下载 `test.pdf` 文件，点击下载链接后 URL 如下所示：

`http://example.com/download?login=1&file=test.pdf&hash=f26e1f5aa1094662caf3a6f8b774e824 `

已知网站服务器是 Linux 操作系统，后端使用 Python 脚本语言，并在用户下载文件前，需要验证用户的下载权限，所以会先用以下算法生成一个关于文件名的哈希值附在链接末尾：

```python
def create_hash(salt, login, file_name):
	return md5(salt + login + file_name).hexdigest()
```

再用以下算法验证下载请求的合法性：

```python
def verify_hash(salt, login, file_name, user_hash):
	if login:
		valid_hash = create_hash(salt, login, file_name)
		if valid_hash == user_hash:
			permit_download(file_name)
		else:
			print "Your hash is invalid."
	else:
		print "Please login."
```

在不知道 `salt` 具体的值，但知道其长度的情况下，能否下载根目录下的 `/etc/passwd` 文件呢？

假设 `salt` 的长度为 6，先列出原问题的已知参数：

```
login = "1"
file = "test.pdf"
length(login || file) = 9 Byte = 72 bit
length(salt) = 6 Byte = 48 bit
hash = MD5(salt || "1test.pdf") = f26e1f5aa1094662caf3a6f8b774e824
```

再列出待解问题的未知参数：

```
login = ？
file = "../../../../../../etc/passwd"
length(login) = ？
length(salt || "1test.pdf") = 15 Byte = 120 bit
hash = MD5(salt || login || "../../../../../../etc/passwd") = ？
```

由上述参数的变化可知，若改变 `login` 的值后，还能计算出对应的签名，即可达到**任意文件下载**的目的。根据漏洞原理，利用 0x03 中的 HashPump 工具可解出上述未知参数：

```
Input Signature: f26e1f5aa1094662caf3a6f8b774e824
Input Data: 1test.pdf
Input Key Length: 6
Input Data to Add: ../../../../../../etc/passwd
ee3dc297d57bd7bf82ccf0ae20e35c6b
1test.pdf\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x78\x00\x00\x00\x00\x00\x00\x00../../../../../../etc/passwd
```

可见，在成功构造 `login` 后，并重新计算出新的签名，结果如下所示：

```
login = "1test.pdf\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x78\x00\x00\x00\x00\x00\x00\x00"
file = "../../../../../../etc/passwd"
length(login) = 58 Byte = 464 bit
length(salt || "1test.pdf") = 15 Byte = 120 bit
hash = MD5(salt || login || "../../../../../../etc/passwd") = ee3dc297d57bd7bf82ccf0ae20e35c6b
```

注意，需要将上述 `login` 的值进行 URL 编码，以适应浏览器的请求格式，最终构造下载链接的 URL 即可下载 `/etc/passwd` 文件：

`http://example.com/download?login=1test.pdf%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%78%00%00%00%00%00%00%00&file=../../../../../../etc/passwd&hash=ee3dc297d57bd7bf82ccf0ae20e35c6b`

**哈希长度扩展攻击的限制条件较多，现实中并不常见，下面关于上述漏洞利用场景作几点说明：**

1. 对于不同文件的校验哈希值，必须由同一个 `salt` 值产生的；
2. Web 服务器必须有访问其他目录的权限，否则无法访问根目录下的 `/etc/passwd` 文件；
3. `../` 是在命令行下返回上级目录的操作符。由于文件下载目录不在根目录下，所以要通过多个 `../` 操作返回根目录。注意，在根目录下返回上级目录，仍然是根目录。

## 漏洞修复

Hash Length Extension Attack 是 Merkle–Damgård 结构的固有缺陷，只要采用了此结构的哈希函数都会存在此漏洞。因此没有药到病除的方法，只有以下几条权宜之计供参考：

1.  **采用 HAMC 或 SHA-3 等**非 Merkle–Damgård 结构的哈希算法；
2.  **采用连续两次加「盐」哈希运算**，即 $hash(salt \ + hash(salt \ + \ message))$；
3.  **将 $secret$ 值放在输入参数末尾。**若已知 $MD5(message1 \ || \ secret)$，我们希望能求出 $MD5(message1 \ || \ secret \ || \ padding1 \ || \ message2)$，但实际上 $secret$ 的附加策略是在输入参数末尾，因此只能得到 $MD5(message1 \ || \ padding1^{'} \ || \ message2 \ || \ secret)$。显然，在 $secret$ 未知的情况下是求不出该值的。

# 0x03 HashPump

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

# 0x04 writeups

介绍完 Hash Length Extension Attack 的原理与 HashPump 工具的使用方法后，下面借助相关的 CTF 题目来展示该漏洞的实际利用过程。

## 【实验吧 CTF】 Web —— 让我进去

此题结合了 PHP 的代码审计与 Hash Length Extension Attack，难度中等，需要的基础知识有：**PHP、Linux、HTTP协议、MD5加密原理。**相关链接如下：

- 题目链接：[http://www.shiyanbar.com/ctf/1848](http://www.shiyanbar.com/ctf/1848)
- 解题链接：[http://ctf5.shiyanbar.com/web/kzhan.php](http://ctf5.shiyanbar.com/web/kzhan.php)

![lmi-question](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/lmi-question.jpg)

进入解题链接，发现如下输入框，任意输入一些值，或尝试注入，均无报错信息，且源码也无干货。

![lmi-input](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/lmi-input.jpg)

![lmi-source1](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/lmi-source1.jpg)

接下来查看它的 HTTP 请求头，发现有两个属于题目本域的异常 Cookie，分别为：`sample-hash = 571580b26c65f306376d4f64e53cb5c7` 和 `source = 0`。

![lmi-cookie](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/lmi-cookie.jpg)

尝试用 BurpSuite 把 `source` 的值改为 1，再次发出请求，果然得到了真正的源代码：

![lmi-source2](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/lmi-source2.jpg)

由以下语句可知 Cookie `sample-hash` 原来是 `$secret` 与「adminadmin」连接而成的字符串的 MD5 散列值，即上述的 $MD5(secret || message1)$， $secret$ 为 $15 \ Byte$ 长的字符串变量 `$secret`，$message1$ 为字符串「adminadmin」 。

``` php
setcookie("sample-hash", md5($secret . urldecode("admin" . "admin")), time() + (60 * 60 * 24 * 7));
```

又由以下核心语句，得知爆 flag 的条件是设置一个新 Cookie `getmein`，它的值要与 `$secret + $username + $password` 组成的字符串的 MD5 散列值相等，但前面还有一个限制条件：**`$username` 的值要等于「admin」，且 `$password` 不能等于「admin」。**想到这里，就可知此题是要用 Hash Length Extension Attack 来伪造新的散列值绕过验证。

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

![lmi-hashpump](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/lmi-hashpump.jpg)

- **Input Signature** 是 $MD5(secret \ || \ message1)$，此处为 `sample-hash` 的取值`571580b26c65f306376d4f64e53cb5c7`；

- **Input Data** 是 $message1$，此处为字符串「adminadmin」；

- **Input Key Length** 是 $secret$ 的长度，此处为 15；

- **Input Data to Add** 是 $message2$，此处设为字符串「ciphersaw」。

可见，得到了 $MD5(secret \ || \ message1 \ || \ padding1 \ || \ message2)$ 的结果为 `ca78a24c34c2e13331e7b0425b567b09` 。

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

![lmi-flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/hash-length-extension-attack/lmi-flag.jpg)