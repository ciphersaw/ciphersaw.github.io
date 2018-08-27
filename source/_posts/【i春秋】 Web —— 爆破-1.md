---
title: 【i春秋】 Web —— 爆破-1
copyright: true
date: 2018-08-27 22:11:40
tags: [i春秋,CTF,writeup,audit,php,regex]
categories: [InfoSec,Web]
mathjax: true
---

# 0x00 前言

此题出自「百度杯」CTF 比赛 2017 二月场，是第一道 「爆破」系列的 Web 题，考察大家对 PHP 语言特性的熟练度，难度低，需要的基础知识有：**PHP、正则表达式**。

题目链接在「i春秋」的 CTF 大本营，解题链接通过创建在线靶场后得到：

- 题目链接：[https://www.ichunqiu.com/battalion?t=1&r=57475](https://www.ichunqiu.com/battalion?t=1&r=57475)

<!-- more -->

![question](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_1/question.png)

# 0x01 爆破六位变量？

打开链接，直接看到一段 PHP 源码，是 PHP 代码审计出题的常规手法，只需提交正确的 payload，绕过代码中设置的限制即可：

```php
<?php
include "flag.php";
$a = @$_REQUEST['hello'];
if(!preg_match('/^\w*$/',$a )){
  die('ERROR');
}
eval("var_dump($$a);");
show_source(__FILE__);
?>
```

由提示可知，flag 是藏在某六位变量中，有的同学一上来就跳进出题人挖的坑里，直接生成字典去爆破变量名。

不要着急，先看看代码第 4 行的变量名匹配规则，是通过[正则表达式](https://en.wikipedia.org/wiki/Regular_expression) `/^\w*$/` 完成的，其中：

- `^n`：匹配任何开头为 `n` 的字符串。
- `n$`：匹配任何结尾为 `n` 的字符串。
- `n*`：匹配任何包含零个或多个 n 的字符串。 
- `\w`：查找单词字符，包括大写字母 `A-Z`、小写字母 `a-z`、数字 `0-9`、下划线 `_`。

理解了匹配规则后，可推出以下两条线索：

- PHP 中满足正则表达式的六位变量共有 $53 \times 63^{5} = 52,599,136,779$ 种，每个变量占六字节，所以需要 $52,599,136,779 \times 6 = 315,594,820,674 \ B \approx 294 \ GB$ 的存储空间，用如此大的字典去爆破，通常计算机是无法承受的。
- 匹配字符串无限定长度，说明不一定非要提交六位变量。

入坑的朋友们，赶紧从坑里爬出来，转换一下思路吧！

# 0x02 超级全局变量 $GLOBALS

由第 3 行可知，通过 GET 请求或 POST 请求提交的 `hello` 参数，将其赋值给 PHP 变量 `$a`，再到第 7 行的代码执行函数 [`eval()`](http://www.php.net/eval) 中，由 [`var_dump()`](http://php.net/manual/en/function.var-dump.php) 函数变量的类型、值、结构等信息打印出来。

> 小贴士：`eval()` 函数的执行顺序，是先将变量 `$a` 解析得到字符串（设为 `xxx`），再与 `$` 拼接，最后执行 `var_dump($xxx);`。详情可参考：[玩转 PHP eval() 中的单双引号](https://ciphersaw.github.io/2017/11/16/%E7%8E%A9%E8%BD%AC%20PHP%20eval%28%29%20%E4%B8%AD%E7%9A%84%E5%8D%95%E5%8F%8C%E5%BC%95%E5%8F%B7/)。

既然 flag 存放在某个变量中，这时我们应该想到超级全局变量 [`$GLOBALS`](http://php.net/manual/en/reserved.variables.globals.php)，它是一个包含了全局作用域中全部变量的关联数组，变量名即为数组的键值，**注意变量名必须全部大写**。

因此，只需构造 payload `hello=GLOBALS` 提交 GET 请求，即可获得 flag，同时也看到了传说中的某六位变量 `$d3f0f8`。

![flag](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_1/flag.png)