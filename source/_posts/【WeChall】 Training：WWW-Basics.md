---
title: 【WeChall】 Training：WWW-Basics
copyright: true
date: 2019-04-30 14:54:15
tags: [wechall,CTF,writeup,VPS,linux,bash,web,http,python]
categories: [InfoSec,Web]
---

# 0x00 前言

本题的思路很明确：搭建一个 Web 服务后，使 WeChall 能够访问特定网页的内容。

但问题来了，WeChall 是向用户登录的 IP 地址发起访问请求。一方面，运营商分配给普通用户的 IP 地址通常是经过多层 NAT 的，所有无法在个人 PC 上搭建 Web 服务，让公网用户访问；另一方面，租借一台 VPS 虽然能拥有公网独立 IP 地址，但服务器的操作系统通常是命令行界面，难以通过浏览器访问题目链接，再点击按钮使 WeChall 访问服务器的特定网页。

鉴于此，解决方案如下：**租借一台 VPS 搭建起 Web 服务，通过 Python 脚本模拟浏览器访问题目链接，使 WeChall 成功访问服务器的特定网页**。

- 题目链接：[https://www.wechall.net/challenge/training/www/basic/index.php](https://www.wechall.net/challenge/training/www/basic/index.php)

<!-- more -->

![question](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/question.png)

# 0x01 搭建 Web 服务

关于 VPS 的选取，经过调研后决定使用 [Vultr](https://www.vultr.com/)，其提供的服务实惠便捷，非常适用于本题的小型部署实验场景。

值得一提的是， Vultr 同时支持支付宝与微信充值，方便了国内用户使用。创建完账户后，充值 10 美元能保证正常使用即可，VPS 是按时按量计费的，删除停用后将不会继续扣费。

## 部署环境

在服务器部署页面中，保持默认选择的云计算实例 **Vultr Cloud Compute (VC2)** 。第一步，选择地理位置，以 **America -> New York (NJ)** 为例：

![location](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/location.png)

第二步，选择服务器类型。由于我们只需搭建 Web 服务，因此可选择一键部署应用，省去了自行部署环境的过程，以 **Application -> LEMP -> CentOS 7** 为例：

> 小贴士：**[LEMP](https://lemp.io/)** 是一组用于开发部署 Web 应用的自由软件的名称首字母缩写，通常指 Linux + Nginx + MySQL + PHP，使用说明请参考 [One-Click LEMP](https://www.vultr.com/docs/one-click-lemp)。

![type](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/type.png)

第三步，选择服务器配置。由于实验所需的资源甚少，所以选择最低配置 **$5/mo**：

![size](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/size.png)

其余设置可忽略，最后点击 **Deploy Now** 部署服务器。部署完成后，在 **Servers** 页面可看到 VPS 的概览：

![overview](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/overview.png)

可见，VPS 的 IP 地址为 **45.63.23.131**，在浏览器若能成功访问，则说明 Web 服务环境已部署完成：

![index](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/index.png)

此外，点击 **··· -> Server Details** 可查看 VPS 的详情信息，包括系统用户名与口令，以及各种资源的使用情况：

![detail](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/detail.png)

## 编写特定网页

接下来，需要用终端模拟器远程控制 VPS，向特定网页写入内容。本文选用 **[Xshell](https://www.netsarang.com/en/xshell/)** 进行连接，在新建会话属性框内，在 **主机** 栏中填入 IP 地址，在 **名称** 栏中按需自定义会话名称：

![create](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/create.png)

点击确定并连接后，在 SSH 安全警告框内点击 **一次性接受**，在 SSH 用户名框内输入 **root**，在 SSH 用户身份验证框内输入 VPS 详情中的口令。成功连接后，提示符将变为 `[root@vultr ~]#`：

![login](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/login.png)

参考 One-Click LEMP 的使用说明，在 Xshell 中输入以下命令，向 `/usr/share/nginx/html/ciphersaw/ciphersaw.html` 文件内写入 `My name is ciphersaw and iChall.`：

```bash
# Enter the directory /usr/share/nginx/html
cd /usr/share/nginx/html

# Create the directory ./ciphersaw and enter it
mkdir ciphersaw && cd ciphersaw

# Write "My name is ciphersaw and iChall." into ciphersaw.html
echo -n "My name is ciphersaw and iChall." > ciphersaw.html
```

> 小贴士：若执行 `echo` 命令时不带参数 `-n`，则会在末尾自动添加换行符，导致不符合题目要求。此外，直接使用 `vim` 命令进行文本编辑，保存退出后也会出现上述问题。

执行完上述命令后，若能在浏览器内访问 **45.63.23.131/ciphersaw/ciphersaw.html**，则说明题目要求的 Web 服务已搭建完成：

![ciphersaw](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/ciphersaw.png)

# 0x02 安装依赖工具

CentOS 7 系统自带 Python 2.7.5，但未提供 Python 包管理工具 **pip**。因此，需要先用系统的包管理工具 yum 安装 pip，才能继续安装 Python 脚本中所需的 HTTP 网络通信库 **requests**。此外，建议先在个人 PC 上完成 Python 脚本的编辑，再将其上传至 VPS，所以还需要安装文件传输工具 **lrzsz**。

正常情况下，依次执行以下命令，可完成依赖工具的安装：

```bash
# Install pip
yum -y install python-pip

# Upgrade pip
pip install --upgrade pip

# Install requests
pip install requests

# Install lrzsz
yum -y install lrzsz
```

# 0x03 人生苦短，我用 Python

通过 Python 脚本模拟浏览器访问 WeChall，关键点有两个：一是要**携带用户身份认证信息**，即我们熟知的 Cookie；二是要**携带点击按钮发送的表单数据**。

## 编写脚本

Python 脚本主要是通过 [requests](https://2.python-requests.org/en/master/) 库向题目链接发送 POST 请求，模拟浏览器中的点击操作，使 WeChall 访问服务器的特定网页。

注意，由于个人 PC 与 VPS 的 IP 地址不同，因此在 PC 上登录 WeChall 用户时，切勿勾选 **Restrict Session to this IP**，否则 Cookie 与 PC 的 IP 地址绑定，导致在 VPS 上无法正常使用。

登录后进入题目链接，先按下 **F12** 打开 Chrome 浏览器的开发者工具，再点击页面中的按钮，在 **Network -> Name -> Headers** 中可查看当前用户的 Cookie 与表单数据的内容：

![f12](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/f12.png)

最后根据 Cookie 与表单数据编写出 Python 脚本：

```python
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import requests

url = 'https://www.wechall.net/challenge/training/www/basic/index.php'
cookie = {'WC': '11477596-43556-xxxxxxxxxxxxdYAW'}
args = {'port': '80', 'go': 'I have set it up. Please check my server.'}
res = requests.post(url, cookies = cookie, data = args)
print res.text
```

## 上传脚本

回到 Xshell，输入 `rz` 命令后，选择 Python 脚本文件（此处命名为 payload.py）上传即可：

![payload](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/payload.png)

## 执行脚本

继续输入 `python payload.py` 执行脚本，若执行成功，则会在返回内容中出现相关提示：

![result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/WeChall_Training_WWW_Basics/result.png)

# 0x04 小结

本题对初学者而言是非常好的锻炼，既能了解在 Linux 下搭建真实 Web 服务器的过程，又能学习如何使用 Python 脚本模拟浏览器发起访问请求。另外，建议感兴趣的同学尝试手动部署 LEMP 环境，这能够加深对 Web 服务器的理解。

最后的最后，用完了 VPS ，别忘了在 **Servers** 页面点击 **Server Destroy** 删除停用服务喔：)