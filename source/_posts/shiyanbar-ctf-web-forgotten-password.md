---
title: 【实验吧 CTF】 Web —— 忘记密码了
date: 2017-09-28 16:13:00
tags: [实验吧,CTF,Writeup,Audit,PHP,Vim]
categories: [InfoSec,Web]
copyright: true
---

# 0x00 前言

此题是 Web 基础题，难度中低，需要的基础知识有：**HTML、PHP、SQL、Linux、HTTP 协议**。

共涉及三个页面，需要用到**浏览器调试技巧和搜索技巧**，还要有**关键点发现意识**，先附上链接。

- 题目链接：[http://www.shiyanbar.com/ctf/1808](http://www.shiyanbar.com/ctf/1808)
- 解题链接：[http://ctf5.shiyanbar.com/10/upload/step1.php](http://ctf5.shiyanbar.com/10/upload/step1.php)

<!-- more -->

![question](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/question.jpg)

# 0x01 先看看 step1.php

看到一个输入框，随便填个 root@xxx.com 试试反应，结果得到一个弹框，得到第二个页面 **step2.php**。

![step1](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/step1.jpg)

![alert](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/alert.jpg)

# 0x02 习惯性地翻源码

## 从 step1.php 源码可以得到以下线索：

- admin 的邮箱是 admin@simplexue.com
- 是用编辑器 Vim 编辑的

![step1-source](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/step1-source.jpg)

## 再看看 step2.php 源码可以发现：

- 怪不得马上跳转回 step1.php，原来有一句：
```
<meta http-equiv=refresh content=0.5;URL="./step1.php">check error!
```
- 跟 step1.php 同样存在关于 admin 和 editor 信息
- 代码下半部分惊奇地发现一个表单，并且得到第三个页面 **submit.php**，还知道需要通过 **GET 方法**向该页面发送两个参数 **emailAddress** 和 **token**。

![step2-source](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/step2-source.jpg)

从以上线索看来只有一条路可走：**找出正确的 emailAddress 和 token** 发给 submit.php。
尝试随便发点东西给 submit.php，却得到无情的拒绝:(

![refuse](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/refuse.jpg)

# 0x03 一般人查到这就懵逼了

分析一下上述线索，只有 **Vim 编辑器** 这条线索没用到了，去查查用 Vim 时会产生什么文件吧，从[https://segmentfault.com/q/1010000002692574](https://segmentfault.com/q/1010000002692574)可以看出有以下三种文件，逐一测试终于发现本题的关键文件 `.submit.php.swp`（注意 submit 前面还有个.）

![vim](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/vim.jpg)

打开 `.submit.php.swp` 文件，终于看到关键代码：

![swp](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/swp.jpg)

要想输出 `$flag`，必须使三个 if 的条件成立：
1. `$emailAddress` 和 `$token` 非空
2. `$token` 的长度为 10
3. `$token` 的值为 0
4. 最后注意 admin 的邮箱地址要填正确，否则 37 行 `$r['num']` 的查询返回结果为 0

根据上述条件，就可构建出正确的参数值 `emailAddress=admin@simplexue.com&token=0000000000`，提交后可见 flag：

![flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/shiyanbar-ctf-web-forgotten-password/flag.jpg)