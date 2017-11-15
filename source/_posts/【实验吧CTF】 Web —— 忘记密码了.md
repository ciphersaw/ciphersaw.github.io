---
title: 【实验吧CTF】 Web —— 忘记密码了
date: 2017-09-28 16:13:00
tags: [实验吧,CTF,writeup,audit]
categories: [InfoSec,Web]
---

# 0x00 前言

此题是Web基础题，难度中等，需要的基础知识有：**HTML、PHP、SQL、Linux、HTTP协议**。

共涉及三个页面，需要用到**浏览器调试技巧和搜索技巧**，还要有**关键点发现意识**，先附上链接。

- 题目链接：[http://www.shiyanbar.com/ctf/1808](http://www.shiyanbar.com/ctf/1808)
- 解题链接：[http://ctf5.shiyanbar.com/10/upload/step1.php](http://ctf5.shiyanbar.com/10/upload/step1.php)

<!-- more -->

![question](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/question.jpg)

# 0x01 先看看step1.php

看到一个输入框，随便填个root@xxx.com试试反应，结果得到一个弹框，得到第二个页面**step2.php**。

![step1](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/step1.jpg)

![alert](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/alert.jpg)

# 0x02 习惯性地翻源码

## 从step1.php源码可以得到以下线索：

- admin的邮箱是admin@simplexue.com
- 是用编辑器Vim编辑的

![step1_source](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/step1_source.jpg)

## 再看看step2.php源码可以发现：

- 怪不得马上跳转回step1.php，原来有一句：
```
<meta http-equiv=refresh content=0.5;URL="./step1.php">check error!
```
- 跟step1.php同样存在关于admin和editor信息
- 代码下半部分惊奇地发现一个表单，并且得到第三个页面**submit.php**，还知道需要通过**GET方法**向该页面发现两个参数**emailAddress**和**token**。

![step2_source](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/step2_source.jpg)

从以上线索看来只有一条路可走：**找出正确的emailAddress和token**发给submit.php。
尝试随便发点东西给submit.php，却得到无情的拒绝:(

![refuse](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/refuse.jpg)

# 0x03 一般人查到这就懵逼了

分析一下上述线索，只有**Vim编辑器**这条线索没用到了，去查查用Vim时会产生什么文件吧，从[https://segmentfault.com/q/1010000002692574](https://segmentfault.com/q/1010000002692574)可以看出有以下三种文件，逐一测试终于发现本题的关键文件`.submit.php.swp`（注意submit前面还有个.）

![vim](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/vim.jpg)

打开`.submit.php.swp`文件，终于看到关键代码：

![swp](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/swp.jpg)

要想输出$flag，必须使三个if的条件成立：
1. $emailAddress和$token非空
2. $token的长度为0
3. $token的值为0
4. 最后注意admin的邮箱地址要填正确，否则34行的$sql会赋值失败
根据上述条件，就可构建出正确的参数值**emailAddress=admin@simplexue.com&token=0000000000**，提交后可见flag：

![flag](http://oyhh4m1mt.bkt.clouddn.com/%E5%AE%9E%E9%AA%8C%E5%90%A7CTF_Web_%E5%BF%98%E8%AE%B0%E5%AF%86%E7%A0%81%E4%BA%86/flag.jpg)