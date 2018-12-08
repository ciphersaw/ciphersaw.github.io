---
title: 【CNSS 2017】 Crypto —— RSA Combo
date: 2017-10-27 22:11:08
tags: [CNSS,CTF,writeup,crypto]
categories: [InfoSec,Crypto]
copyright: true
mathjax: true
---

# 0x00 前言

本次 [UESTC CNSS Recruit 2017](https://ctf.cnssuestc.org/) 中，Crypto 方面的题推出了 RSA 套餐，涉及 **RSA 加密算法原理**与**特定情况下对 RSA 的密码攻击**，对密码学初学者是个很好的练习机会，在此感谢出题人 [JHSN](http://blog.chrstm.com/) 和 [xris](http://xr1s.me/) 。

<!-- more -->

此 RSA 套餐一共四题，前两题涉及 RSA 加密算法原理，后两题涉及 RSA 密码攻击。

RSA 公钥密码体制于 1977 年由 Ron Rivest、Adi Shamir、Leonard Adleman 一起提出，并以三人的姓氏首字母拼接命名，现已成为公钥密码的国际标准，是目前应用最广泛的公钥密码体制之一。RSA 是基于大整数因子分解问题的公钥密码，因此阅读本文需要有**数论**基础，并且所有代码选用 **Python**，便于大整数运算。

下面先介绍 RSA 加解密算法的过程，需要用到的几个数论知识，请读者自行学习理解。

## RSA 密钥对的生成

RSA 公私密钥对的生成，由以下四个步骤完成：

1. 选取两个**大素数** $p$ 和 $q$ （目前安全标准要求 $p$、$q$ 长度相差不能太大，且至少有 $512 bits$；
2. 计算乘积 $n = p \times q$ 和 $\varphi\left(n\right) = \left(p-1\right)\left(q-1\right)$，其中 $\varphi\left(n\right)$ 是**欧拉函数**；
3. 随机选取整数 $e$ 作为公钥，$1 < e < \varphi\left(n\right)$，并且要求 $gcd\left(e,\varphi\left(n\right)\right) = 1$，即 $e$ 与 $\varphi\left(n\right)$ 互素，**最大公约数**为 $1$；
4. 用**扩展欧几里得算法**计算私钥 $d$，满足 $d \times e \equiv 1 \ mod \ \varphi\left(n\right)$，即 $d \equiv e^{-1} \ mod \ \varphi\left(n\right)$，称 $d$ 是 $e$ 在模 $\varphi\left(n\right)$ 下的**乘法逆元**。

此时得到公钥 $\left(e,n\right)$ 与 私钥 $d$。应注意，用户需要公开公钥 $\left(e,n\right)$，而只需保留私钥 $d$，两个大素数 $p$ 和 $q$ 已不再需要，最好销毁，但千万不能泄露。

## RSA 加密算法

加密时首先将明文消息字符串转换为二进制编码，用十六进制表示，然后将明文比特串分组，每个分组的十进制数必须小于 $n$，即每个分组的比特数不大于 $\log_2 n $，最后对每个明文分组进行加密运算，过程如下：

1. 获得接收方的公钥 $\left(e,n\right)$；
2. 将明文 $M$ 划分为 $N$ 个明文分组 $M = m_1m_2 \cdots m_N$，其中每个分组长度为 $L$（$L < \log_2 n$）；
3. 对明文分组进行加密运算，每个分组对应的密文为 $c_i = {m_i}^{e} \ mod \ n$，其中 $1 \le i \le N$，加密后得密文分组 $C = c_1c_2 \cdots c_N$；
4. 将密文 $C$ 发送给接收方。

## RSA 解密算法

解密时首先将密文比特串恢复成明文比特串，再对其进行相应的字符编码，即可得到明文消息，过程如下：

1. 接收方收到密文 $C$ 后，先按照分组长度 $L$ 进行划分，得密文分组 $C = c_1c_2 \cdots c_N$；
2. 使用私钥 $d$，对密文分组进行解密运算，每个分组对应的明文为 $m_i = {c_i}^{d} \ mod \ n$，其中 $1 \le i \le N$，解密后得明文分组 $M = m_1m_2 \cdots m_N$。

以上就是 RSA 加密算法的基本原理，涉及到的数论知识已加粗标识，基本部分没掌握好的请自行查阅资料学习。

下面进入正题，借助 **Python 2.7** 来对 RSA 加解密过程的大整数进行运算，要用到模块 [gmpy2](https://pypi.python.org/pypi/gmpy2) 进行大整数运算，使用文档请见 [http://gmpy2.readthedocs.io/en/latest/](http://gmpy2.readthedocs.io/en/latest/)，以及模块 [binascii](https://docs.python.org/2/library/binascii.html)，将 ASCII 码十六进制字符串还原成明文。

**注意：由于以下四题的明文量较小，均有 $m < p \times q = n$，因此明密文不涉及分组过程。**

# 0x01 Easy RSA

![easy_rsa](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/CNSS_2017_Crypto_RSA_Combo/easy_rsa.png)

```
p: 0xddb9fe428c938abdce551751b299feed367c97b52b17062d
q: 0x265ad78c77eab2c5ab9b69fb44a11624818bed56c003d2c5e6d29f7
e: 0x1fffffffffffffff
d: 0x9737352a92d198aaeddb8db9cc5cb81a788aa7d0ec0ec9bac7f6ffece7ff928c8db6a47656dffb0421ef9ca595665b6b55d35f
c: 0x1c0aa41505131e967d3db09227ef9572337a5e79f07484428efd6262eddee2fb67b6e6e6b5506871891ece1949eabf7a03cafdb
```

根据题意，已知 $p、q、e、d、c$，求 $m$。此题属于 RSA 加密算法基础题，思路也容易想到，直接求 $m = c^d \ mod \ n$ 即可得到明文，且 $n = p \times q$。下面给出 Python 解题代码，代码中的函数使用方法请自行查阅相应模块的使用手册。

```python
import gmpy2
import binascii

p = gmpy2.mpz(0xddb9fe428c938abdce551751b299feed367c97b52b17062d)
q = gmpy2.mpz(0x265ad78c77eab2c5ab9b69fb44a11624818bed56c003d2c5e6d29f7)
d = gmpy2.mpz(0x9737352a92d198aaeddb8db9cc5cb81a788aa7d0ec0ec9bac7f6ffece7ff928c8db6a47656dffb0421ef9ca595665b6b55d35f)
c = gmpy2.mpz(0x1c0aa41505131e967d3db09227ef9572337a5e79f07484428efd6262eddee2fb67b6e6e6b5506871891ece1949eabf7a03cafdb)

m = hex(pow(c, d, p*q))  # Figure out c^d modulo n, then change to hex. Note that n = p * q.
print "plaintext:", m
print "flag:", binascii.a2b_hex(str(m)[2:])
```

代码执行后，打印明文的十六进制数值，以及对应的 ASCII 字符串：

```
plaintext: 0x636e73737b555f6d7573745f6b6e30775f41534331315f616e645f5235617d
flag: cnss{U_must_kn0w_ASC11_and_R5a}
```

# 0x02 RSA Cool

![easy_rsa](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/CNSS_2017_Crypto_RSA_Combo/rsa_cool.png)

```
p: 0xf5621a5fd44994f720c1b971fea84f63
q: 0xdfb85e3d22c0b59271884df021a57123
e: 0xf36698ed9d9fedd7
c: 0x448040a0a4757a630c4d8401fb3c0518ab0bce9a02085329536244c91727775c
```
根据所给数据，本题是已知 $p、q、e、c$，求 $m$，与第一题相比少给了私钥 $d$。此题也属于 RSA 加密算法基础题，在第一题的基础上先求出私钥 $d$，再求 $m = c^d \ mod \ n$ 即可得到明文。下面给出 Python 解题代码。

```python
import gmpy2
import binascii

p = gmpy2.mpz(0xf5621a5fd44994f720c1b971fea84f63)
q = gmpy2.mpz(0xdfb85e3d22c0b59271884df021a57123)
e = gmpy2.mpz(0xf36698ed9d9fedd7)
c = gmpy2.mpz(0x448040a0a4757a630c4d8401fb3c0518ab0bce9a02085329536244c91727775c)

phi_n = (p - 1) * (q - 1)
d = gmpy2.invert(e, phi_n)  # Figure out the multiplicative inverse of e modulo phi_n (i.e. the private key). 
m = hex(pow(c, d, p*q))  # Figure out c^d modulo n, then change to hex. Note that n = p * q.

print "private key:", hex(d)
print "plaintext:", m
print "flag:", binascii.a2b_hex(str(m)[2:])
```

代码执行后，打印私钥、明文的十六进制数值，以及对应的 ASCII 字符串：

```
private key: 0x93f984ff1d6333df9c43c135c3098a83d27516f5cf32f9475171fe31da5c7edb
plaintext: 0x636e73737b5269763373745f5368616d31725f34646c656d616e7d
flag: cnss{Riv3st_Sham1r_4dleman}
```
# 0x03 RSA Cooler

![easy_rsa](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/CNSS_2017_Crypto_RSA_Combo/rsa_cooler.png)

```
    public key 1:
    n = 0x9ff2e873e1fcafbed22341b4eafdae01afec540e4e84e6041b0a0e83253f1c5da5dabc73004faa82cfaff8e83e5a99255f9790a7744dd18a694d09a89a5caf638d0cf4fe1150a9e894d47a17f386c107a083ae227efab851196de992a2441b7af3442f31a757234ef8997d8af1a3c3aecf2b6100d393a7b632913c2b1c921409
    e = 0xe9a44960483b5ca224cfd18818944eaae47de3a158debbc7886b74d7e11165e2e4158c86add4ccc5317256e5323596c9947513766645aefdac4f0375a0296743

    encrypted message 1:
    c = 0x636f86fb2b1991d4788092563adf87d14b975e9c7ab7279b10f4741f515788bba2e6e788d6f6c165f4daf65eabee93cebfc55a1d651b1dfb1190174ab338d959775658cf1c6d42b0fe6b7b1abaf5a9aa4ca239367bfcbe88b304c99d5e5f8aac019ec74b11662a5deba523c2f93b7c68a731c019578e3ac64db64cfd3533e91b

    public key 2:
    n = 0x9ff2e873e1fcafbed22341b4eafdae01afec540e4e84e6041b0a0e83253f1c5da5dabc73004faa82cfaff8e83e5a99255f9790a7744dd18a694d09a89a5caf638d0cf4fe1150a9e894d47a17f386c107a083ae227efab851196de992a2441b7af3442f31a757234ef8997d8af1a3c3aecf2b6100d393a7b632913c2b1c921409
    e = 0xd9b47cdd777deb3e94cfa3d416aa91b04f9391af0504a83de03e9e0c49faae8b79cf7c99f575af99ed2e9e5a7edb09219c4f79cf961092f9919ab33bc3c9a74f

    encrypted message 2:
    c = 0x53b601daa8f93166495a69fa747f8553bb8317cfe6dc3f7fec8c8511e209f9288038405fdee399f3ed68ab25dcd91be8bb2ef2ecac1173318b5d2bba932afdcab2d4e5b46987a0f774a29204ce481f79ea422943118f2eaf6c6820b501d9da8d3fbbcea464a2d158a39de6bae6ab845555e4646ae556d7b1e00567b00d41b06c
```

根据所给数据，可看出本题是已知两组 $n、e、c$，求 $m$，且两组中的模数 $n$ 相等。

换言之，就是已知两个都在模 $n$ 下的公钥，记为 $e_1、e_2$，以及相应的密文 $c_1、c_2$，看你能不能恢复出明文？即使学过 RSA，如果数学基础不够扎实，也很难想出解法的。翻阅了几本密码学教材，发现这种在特定场景下的 RSA 密码攻击，大名为**共模攻击**。

## 共模攻击

**共模攻击**，是指在 RSA 加密算法的实际使用中，有时为了方便起见，给每个用户设置相同的模数 $n$，仅用不同的公钥 $e$ 来区分不同用户。在这种场景下，若攻击者截获了分别用不同公钥 $e_1、e_2$ 加密相同明文 $m$ 后的密文 $c_1、c_2$，则能够在不知道用户私钥 $d_1、d_2$ 的情况下，恢复出明文 $m$。

假设两个用户的公钥分别为 $e_1、e_2$，且 $e_1$ 与 $e_2$ 互素，模数为 $n$，明文为 $m$，密文分别为 $c_1 \equiv m^{e_1} \ mod \ n 、 c_2 \equiv m^{e_2} \ mod \ n$。攻击者截获 $c_1、c_2$ 后，可通过**扩展欧几里得算法**，求出满足等式 $xe_1 + ye_2 = 1$ 的两个整数 $x$ 和 $y$，其中 $x$ 是 $e_1$ 在模 $e_2$ 下的**乘法逆元**，$y$ 是 $e_2$ 在模 $e_1$ 下的**乘法逆元**，由此计算 ${c_1}^x{c_2}^y \equiv m^{xe_1}m^{ye_2} \equiv m^{\left(xe_1+ye_2\right)} \equiv m \ mod \ n$ 即可得到明文 $m$。下面给出 Python 解题代码。

```python
import gmpy2
import binascii

# Extended Euclid Algorithm
def extendedGCD(a, b):  
    # a*xi + b*yi = ri
    if b == 0:
        return (1, 0, a)
    # a*x1 + b*y1 = a
    x1 = 1
    y1 = 0
    # a*x2 + b*y2 = b
    x2 = 0
    y2 = 1
    while b != 0:
        q = a / b
        # ri = r(i-2) % r(i-1)
        r = a % b
        a = b
        b = r
        # xi = x(i-2) - q*x(i-1)
        x = x1 - q*x2
        x1 = x2
        x2 = x
        # yi = y(i-2) - q*y(i-1)
        y = y1 - q*y2
        y1 = y2
        y2 = y
    return (x1, y1, a)

n = gmpy2.mpz(0x9ff2e873e1fcafbed22341b4eafdae01afec540e4e84e6041b0a0e83253f1c5da5dabc73004faa82cfaff8e83e5a99255f9790a7744dd18a694d09a89a5caf638d0cf4fe1150a9e894d47a17f386c107a083ae227efab851196de992a2441b7af3442f31a757234ef8997d8af1a3c3aecf2b6100d393a7b632913c2b1c921409)
e1 = gmpy2.mpz(0xe9a44960483b5ca224cfd18818944eaae47de3a158debbc7886b74d7e11165e2e4158c86add4ccc5317256e5323596c9947513766645aefdac4f0375a0296743)
e2 = gmpy2.mpz(0xd9b47cdd777deb3e94cfa3d416aa91b04f9391af0504a83de03e9e0c49faae8b79cf7c99f575af99ed2e9e5a7edb09219c4f79cf961092f9919ab33bc3c9a74f)
c1 = gmpy2.mpz(0x636f86fb2b1991d4788092563adf87d14b975e9c7ab7279b10f4741f515788bba2e6e788d6f6c165f4daf65eabee93cebfc55a1d651b1dfb1190174ab338d959775658cf1c6d42b0fe6b7b1abaf5a9aa4ca239367bfcbe88b304c99d5e5f8aac019ec74b11662a5deba523c2f93b7c68a731c019578e3ac64db64cfd3533e91b)
c2 = gmpy2.mpz(0x53b601daa8f93166495a69fa747f8553bb8317cfe6dc3f7fec8c8511e209f9288038405fdee399f3ed68ab25dcd91be8bb2ef2ecac1173318b5d2bba932afdcab2d4e5b46987a0f774a29204ce481f79ea422943118f2eaf6c6820b501d9da8d3fbbcea464a2d158a39de6bae6ab845555e4646ae556d7b1e00567b00d41b06c)

x, y, r = extendedGCD(e1, e2)
m = hex(pow(c1, x, n) * pow(c2, y, n) % n)

print "plaintext:", m
print "flag:", binascii.a2b_hex(str(m)[2:])
```

代码执行后，打印明文的十六进制数值，以及对应的 ASCII 字符串：

```
plaintext: 0x636e73737b5253415f63306d6d4f6e5f6d6f64754975355f34746b7d
flag: cnss{RSA_c0mmOn_moduIu5_4tk}
```

# 0x04 RSA Coolest

![easy_rsa](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/CNSS_2017_Crypto_RSA_Combo/rsa_coolest.png)

```
    public key 1:
    n = 0xba298d721fadbadb15dabd393db296c13610b33bfeb3aea844815439df3b025bcc6a7085a21eeb3b904a17071c01f05229873518828a8eb8a9129cff611f3481
    e = 0x3

    encrypted message 1:
    c = 0x7d4f6c0953ec517212b6c778da72245820a749254d21b62d09e36b44e073f858114f174b71cee25104b4d3b0abbf7eb31f031201bf40846290344c865c4b9cf8

    public key 2:
    n = 0xe37a3cab324cc0a5ea1030b498f3838f674e6ee9b4e441900c604e4d095b04c70cd32a7c4a5be0b463e3fd94594b3bd25ada9bc9ca17a80d72b7928e233f726d
    e = 0x3

    encrypted message 2:
    c = 0xc09aea0a9b6e10d7db7a5c2071b46f5801896c536152badb81db37848ef373cf6c6842737a87c12f6aba1d39bdf5d2aaf40e919628a64e4cd78a42c2cdde651a

    public key 3:
    n = 0xd8b6924687baaffe1c205ac0474fd5b5f894cb97abb3d427df0e47f30c7f035c07586430679ab65c5bbdccbc53cea9c95c466f3171d24efb85433bd05bc36c5d
    e = 0x3

    encrypted message 3:
    c = 0x6e3591536b9aadcdb412d6b05a755d603d0272434cc27447a8877707861363c8408b47da377474924db89a3e104717855613cbea16ad439c98b6e7bfdb7ae14f
```

根据所给数据，可看出本题是已知三组 $n、e、c$，求 $m$，且三组中的公钥 $e$ 都等于较小的数 $3$。

换言之，就是已知在三个不同模数 $n_1、n_2、n_3$ 下的相同公钥 $e$，以及相应的密文 $c_1、c_2、c_3$，问能不能恢复出明文？刚才的密码学教材继续往下看，得知在此特定场景下的 RSA 密码攻击，名为**低指数攻击**，顾名思义，即要求此相同公钥 $e$ 是个较小的数。

## 低指数攻击

**低指数攻击**，是指为了增强 RSA 加密算法在实际使用中高效性，给每个用户设置相同且较小的公钥 $e$，仅用不同的模数 $n$ 来区分不同用户。在这种场景下，若攻击者截获了在不同模数 $n_1、n_2、n_3$ 下用相同公钥 $e$ 加密相同明文 $m$ 后的密文 $c_1、c_2、c_3$，则能够在不知道用户私钥 $d_1、d_2、d_3$ 的情况下，恢复出明文 $m$。

假设三个用户的模数分别为 $n_1、n_2、n_3$，且不同的模数间两两互素，否则通过计算最大公约数可分解模数，公钥为 $e = 0x3$，明文为 $m$，密文分别为
$$
\begin{cases}
c_1 \equiv m^3 \ mod \ n_1  \\
c_2 \equiv m^3 \ mod \ n_2  \\
c_3 \equiv m^3 \ mod \ n_3
\end{cases}
$$
即可得
$$
\begin{cases}
m^3 \equiv c_1 \ mod \ n_1  \\
m^3 \equiv c_2 \ mod \ n_2  \\
m^3 \equiv c_3 \ mod \ n_3 
\end{cases}
$$
令 $N = n_1n_2n_3$，则通过**中国剩余定理**可求得 $m^3 \ mod \ N$。又因为 $m^3 < N$，则可直接对 $m^3$ 开立方根得到明文 $m$。至此，可知为何要求公钥 $e$ 是个较小的数，因为 $e$ 太大的话会增加开方运算的难度。下面给出 Python 解题代码。

```python
import gmpy2
import binascii

n1 = gmpy2.mpz(0xba298d721fadbadb15dabd393db296c13610b33bfeb3aea844815439df3b025bcc6a7085a21eeb3b904a17071c01f05229873518828a8eb8a9129cff611f3481)
n2 = gmpy2.mpz(0xe37a3cab324cc0a5ea1030b498f3838f674e6ee9b4e441900c604e4d095b04c70cd32a7c4a5be0b463e3fd94594b3bd25ada9bc9ca17a80d72b7928e233f726d)
n3 = gmpy2.mpz(0xd8b6924687baaffe1c205ac0474fd5b5f894cb97abb3d427df0e47f30c7f035c07586430679ab65c5bbdccbc53cea9c95c466f3171d24efb85433bd05bc36c5d)
e  = gmpy2.mpz(0x3)
c1 = gmpy2.mpz(0x7d4f6c0953ec517212b6c778da72245820a749254d21b62d09e36b44e073f858114f174b71cee25104b4d3b0abbf7eb31f031201bf40846290344c865c4b9cf8)
c2 = gmpy2.mpz(0xc09aea0a9b6e10d7db7a5c2071b46f5801896c536152badb81db37848ef373cf6c6842737a87c12f6aba1d39bdf5d2aaf40e919628a64e4cd78a42c2cdde651a)
c3 = gmpy2.mpz(0x6e3591536b9aadcdb412d6b05a755d603d0272434cc27447a8877707861363c8408b47da377474924db89a3e104717855613cbea16ad439c98b6e7bfdb7ae14f)

# Chinese Remainder Theorem with three equations
N  = n1 * n2 * n3
N1 = N / n1
N2 = N / n2
N3 = N / n3
b1 = gmpy2.invert(N1, n1)
b2 = gmpy2.invert(N2, n2)
b3 = gmpy2.invert(N3, n3)
m_pow_e = (c1*b1*N1 + c2*b2*N2 + c3*b3*N3) % N

m, boolean = gmpy2.iroot(m_pow_e, e)  # Figure out the cubic root of m_pow_e
m = hex(m)

print "plaintext:", m
print "flag:", binascii.a2b_hex(str(m)[2:])
```

代码执行后，打印明文的十六进制数值，以及对应的 ASCII 字符串：

```
plaintext: 0x636e73737b436f304f6f4f30306f4f304f6f4f6f304f306f6c6573747d
flag: cnss{Co0OoO00oO0OoOo0O0olest}
```

----------
以上四道关于 RSA 公钥密码体题目的 writeup 到此全部结束，作者水平和经验有限，文中若有错误或不妥之处在所难免，希望发现问题的读者可在文末留言，同时也希望本文能够对读者的密码学探索之旅给予帮助与启发，谢谢。