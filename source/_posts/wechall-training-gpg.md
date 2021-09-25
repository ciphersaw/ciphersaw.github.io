---
title: 【WeChall】 Training：GPG
copyright: true
date: 2019-05-01 18:29:47
tags: [WeChall,CTF,Writeup,Crypto,Linux,GPG,RSA]
categories: [InfoSec,Crypto]
---

# 0x00 前言

本题要求使用 GPG 为邮件通讯内容设置加密功能，一是为了保证邮件内容的机密性，二是为了让用户熟悉 GPG 的基本使用方法。

本题的解决过程如下：先使用 GPG **生成公私钥对**，在 WeChall 的账户设置中将公钥上传，接着 WeChall 会向用户邮箱发送一封加密邮件，解密后得到一条用于**确认公钥有效性**的验证链接，点击并完成公钥设置。最后，回到题目链接，点击按钮后 WeChall 会再发送一封加密邮件，**解密后即可得到 flag**。

备注：本题主要操作在虚拟机的 Kali Linux 2018.2 系统中完成，其中自带的 GPG 版本为 2.2.5，辅助操作在本机的 Windows 7 系统中完成。

- 题目链接：[https://www.wechall.net/challenge/training/crypto/gpg/index.php](https://www.wechall.net/challenge/training/crypto/gpg/index.php)

<!-- more -->

![question](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/question.png)

# 0x01 生成公私钥对

[**GPG（GNU Privacy Guard）**](https://en.wikipedia.org/wiki/GNU_Privacy_Guard)自由软件基金会 GNU 计划中的一款加密软件，其中包含了多种对称加密算法、非对称加密算法、数字签名算法、杂凑算法等，目的是替代 1991 年 [Phil Zimmermann](https://en.wikipedia.org/wiki/Phil_Zimmermann) 开发的商业加密软件 [**PGP（Pretty Good Privacy）**](https://en.wikipedia.org/wiki/Pretty_Good_Privacy)，给普通用户的通讯信息提供安全保护。

在 GPG 2.2.5 版本中，生成公私钥对有两个参数：`--generate-key` 与 `--full-generate-key`。前者是快速生成密钥对，只需填入用户 ID 与邮箱以标识身份，默认使用 3072 位的 RSA 算法，有效期 2 年；后者是完全生成密钥对，还提供了密钥种类、密钥长度、密钥有效期等设置。

在达到我们需求的情况下，操作越简洁越好，此处选择 `--generate-key` 参数快速生成密钥对。填入用户 ID 与邮箱后，要求在弹框内输入授权口令，以保证私钥的合法使用，最后需要敲打键盘或移动鼠标，给随机数的生成提供足够的信息熵。快速生成密钥对的过程如下：

![gen](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/gen.png)

公私钥对生成后，通过 `--list-keys` 参数可查看公钥信息，`--list-secret-keys` 参数可查看私钥信息，`--list-signatures` 参数可查看签名信息：

![list](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/list.png)

# 0x02 验证公钥有效性

首先，输出公钥文件，其中 `--armor` 参数指定以 ASCII 格式输出公钥，`--output` 参数指定输出文件名，`--export` 参数指定用户 ID：

```bash
# Export ciphersaw's public key in ASCII format
gpg --armor --output pubkey --export ciphersaw
```

输出的公钥具有特定的存储格式：

```pgp
-----BEGIN PGP PUBLIC KEY BLOCK-----

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
49RD5y99bvDQhVy27RZszHinctF1du8=
=OHhr
-----END PGP PUBLIC KEY BLOCK-----
```

接下来，将上述公钥复制到 WeChall 的账户设置中，点击 **Upload Key** 上传公钥：

![setup](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/setup.png)

WeChall 会向用户邮箱发送一封用此公钥加密后的邮件：

![encrypted_auth](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/encrypted_auth.png)

注意，邮件内容不符合加密数据的存储格式，需要将其调整为标准格式：

```pgp
-----BEGIN PGP MESSAGE-----
Version: GnuPG v2

hQGMA8fQ72+bDdPvAQv/ZSO1r7T73G/HOUAG5OHtlZmiFiMN+4Zr2Ws2/9Jujw/j
Y39hUGS+R7KFMJ9uArukWlsyF47fo6jPxsQkoOYlAGnFD14CbRu9RZB8iu0RX6F1
M8yzbn5jsGENOVNExKUoX5XalAtRphGKKZyO+CneJp5JfEQ/nP7Now15MRhlUgd1
SgGvU9aaNoetmYYWXmnPUkf+B7IiIzbgiDvOUXHMhj1nQ/uTxF447JXWsr7BymwW
mN465mH64xmYI3Iw5syNnDx0uK8FSwbS/ogG0nC3xrupI/jWDl4ffGyq+0YvrLSf
yHcTfWYH6gk6qP1ZCXzCgSJ9QjRkgiMg141+Fo+GufXomVUaNMyASt1hboCpIZT+
Zxne9gZ/TEnylUPNejCzCpPyfHyLnxMO8ubpJ33O1N8gGCNx0yX/EunqoFnvJJ2z
2YZVyXnORIdn+ecphGrj5vCFewQix4N1AjBRTFJfZ98CArfMKHoLehf5EAlbFaGM
xiEA0gPVW92vcY7MPK3N0sDTAe7nyH9/V5u0Du/qki5ok4oyHwfglOE0eyAUg1jD
O1IV08jW/EMIgiLQZk4RBXVeJh1s/x1ESj+p1Ic4/xenf4tC5OyuIkxEihsBUp6l
Fe8rJIbSmDJnOzGmAMqSJvuyppiOklz+a9cQL7aTNwHr+CDnGP1A0gMX079+udue
NQN1X1PlcjazJfcBAtqKRPPqjCNlRcYU/mZje0y/A7DxBZM5iF3CZ+nkUuR6crl2
uA1ruWo0T3ECKnFX7KX3023LhPbAIss68K17t2Oz3+mw4jBjSD8ytAcgV9xHcXJn
T1BdfajYueClzNbL+JB5z09T6tvh201h5guKhDbCfSEr2Z5egPlLfosVaNS6VdhN
QCcuDhzogtBDGij6am0szcd1UfWPWCeISVVYWWyPx9IYTIAHtEzVqT7oA4s4UpZx
ftT+Fnoh+CDKx62VI2RvHGNQtHZkN1Xm1CdMeQgVB0nFzvUPUldCV/78N9DQxY0f
DY4BC2NMIB5iv4uY3CuiGJg5lDKhAmn6nGQ5mtl/HC3LjJ5LgQ==
=Fxrl
-----END PGP MESSAGE-----
```

将此加密数据保存为文件 `auth`，在 Kali Linux 下进行解密：

```bash
# Decrypt the encrypted data from WeChall
gpg --output auth.html --decrypt auth
```

其中 `--output` 参数指定解密后的输出文件名，`--decrypt` 参数需要解密的文件。注意，执行命令后要求输入私钥的授权口令，避免私钥被非法滥用。

解密后用浏览器打开 `auth.html`，发现明文邮件原来是一条验证链接：

![auth](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/auth.png)

最后，点击链接跳转至 WeChall，提示公钥已成功存储，并且可以正常使用：

![success](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/success.png)

# 0x03 解密获得 flag

回到题目链接，点击 **Send me encrypted mail please** 后，WeChall 会将公钥加密过的 flag 发送至用户邮箱：

![encrypted_flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/encrypted_flag.png)

同样地，将加密数据调整为标准格式：

```pgp
-----BEGIN PGP MESSAGE-----
Version: GnuPG v2

hQGMA8fQ72+bDdPvAQv9EQfqI9xc4JaK67/NDnNHFvd19qj0vk0nVnEKeTubCNj8
z1rQ3hfZAKF/700FT3aWM0qkGKz/iTnEg0GxQa+Q3nMfnja3wBij2BjMqHYnQNsJ
vLakqlPs83hM48N//qSSV+1jlprsoldUAr4Z9TswiYuKX3RZ1suxIGwlm7VFKOlX
31VrkIC3qSE/sEwGuKH2yTuMbTJfX0wWc95iUFYrVPd0v3AtlARwKCoZQ8sMXZCB
HtdlkQPNbpnvNl0rqaJCgtj76cetdot84QJNvE6MZCJ6dr0uOvnw4G0pupmUa8Ur
vkZ5Q2FkiCynAz6ITu5ui6j+0p/TJe2ijI7mU2vCuMC6YxDzJsRv4m24EAJWilnU
TXumU4EU/xYq+GIh7kL6MK5gQS5hFBpXAMSiXK/SYsFGTLOXDIMEdSwO573bdFOo
ltBZMOQEunJ1UpPwctePDY8V2GNbJ0SCZJ2MU0B4/nnlTtYH/oXuDWsx4Dx3OZ0i
HMnOyqpvZeK+tyFORB4h0sBHAf3YMRA610+FTAaXLkm7ot05fUC4rTKC07FuNu+I
yjJv26Mm0eBlZLleZPGfVjWwZmWnhfRs7gJC24xIkWB+XGIZbvC7t4QuBTQXB1MM
IjRgE0AkvxpJBonouWrLL93leJk+GQwKcQGG65kyz01eVx4xJIAHdjNGrwXaVYqk
NWss9a1AswvPt4L1InlhSEw2/9wpojfv5V6UY0XE36rHhGWdaPhTrBTM/BL1kiX0
zjNLjIkEZY+YtBiWK5GkuMFFtZzqYjfQ96N15hhiD1PfaTwk+8tVTdlIrgLVx8tX
iOAfpVrUK1Bp3a8Uae5TjDu4NzrhyQwNPKGCjz2lBp/N1331/T/Q40I=
=pxrG
-----END PGP MESSAGE-----
```

将此加密数据保存为文件 `flag`，同样在 Kali Linux 下进行解密：

```bash
# Decrypt the encrypted flag from WeChall
gpg --output flag.html --decrypt flag
```

解密后用浏览器打开 `flag.html`，即可获得 flag：

![flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_GPG/flag.png)

# 0x04 小结

本题只涉及到 GPG 的基本命令，让我们学会了如何生成公私钥对，以及如何加解密数据。

更全面的使用方法还需要继续专研实践，以下是几篇关于 GPG 的参考文章：

> [GPG入门教程](http://www.ruanyifeng.com/blog/2013/07/gpg.html)
> [The GNU Privacy Guard](https://seanxp.com/2017/02/gpg/)
> [GPG密钥的生成与使用](https://www.jianshu.com/p/7f19ceacf57c)