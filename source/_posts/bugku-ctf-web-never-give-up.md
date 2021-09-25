---
title: 【Bugku CTF】 Web —— never give up
copyright: true
date: 2017-12-26 14:22:46
tags: [Bugku,CTF,Writeup,Web,Audit,PHP]
categories: [InfoSec,Web]
---

# 0x00 前言

此题为 Web 基础题，难度中低，需要的基础知识有：**HTML、PHP、HTTP 协议**。

首先考查**发现源码**的能力，其次重点考查 **PHP 黑魔法**的使用，相关链接如下：

- 题目链接：[http://123.206.31.85/challenges#never give  up](http://123.206.31.85/challenges#never%20give%20%20up)
- 解题链接：[http://120.24.86.145:8006/test/hello.php](http://120.24.86.145:8006/test/hello.php)

<!-- more -->

![question](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Bugku_CTF_Web_never_give_up/question.png)

# 0x01 拦截跳转

点开解题链接，除了一句 **never never never give up !!!** 之外空空如也，直接查看源码，发现一条注释中有线索：

![hello_php_source](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Bugku_CTF_Web_never_give_up/hello_php_source.png)

根据提示打开链接：[http://120.24.86.145:8006/test/1p.html](http://120.24.86.145:8006/test/1p.html)，发现跳转回 [Bugku](http://www.bugku.com/) 的主站，所以祭出 BurpSuite 进行抓包拦截。

请求数据包如下：

![request](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Bugku_CTF_Web_never_give_up/request.png)

响应数据包如下：

![response](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Bugku_CTF_Web_never_give_up/response.png)

# 0x02 三重解码

根据响应内容中变量 `Words` 的值，容易得出是一段 **URL 编码**后的数据：

``` url
%3Cscript%3Ewindow.location.href%3D%27http%3A//www.bugku.com%27%3B%3C/script%3E%20%0A%3C%21--JTIyJTNCaWYlMjglMjElMjRfR0VUJTVCJTI3aWQlMjclNUQlMjklMEElN0IlMEElMDloZWFkZXIlMjglMjdMb2NhdGlvbiUzQSUyMGhlbGxvLnBocCUzRmlkJTNEMSUyNyUyOSUzQiUwQSUwOWV4aXQlMjglMjklM0IlMEElN0QlMEElMjRpZCUzRCUyNF9HRVQlNUIlMjdpZCUyNyU1RCUzQiUwQSUyNGElM0QlMjRfR0VUJTVCJTI3YSUyNyU1RCUzQiUwQSUyNGIlM0QlMjRfR0VUJTVCJTI3YiUyNyU1RCUzQiUwQWlmJTI4c3RyaXBvcyUyOCUyNGElMkMlMjcuJTI3JTI5JTI5JTBBJTdCJTBBJTA5ZWNobyUyMCUyN25vJTIwbm8lMjBubyUyMG5vJTIwbm8lMjBubyUyMG5vJTI3JTNCJTBBJTA5cmV0dXJuJTIwJTNCJTBBJTdEJTBBJTI0ZGF0YSUyMCUzRCUyMEBmaWxlX2dldF9jb250ZW50cyUyOCUyNGElMkMlMjdyJTI3JTI5JTNCJTBBaWYlMjglMjRkYXRhJTNEJTNEJTIyYnVna3UlMjBpcyUyMGElMjBuaWNlJTIwcGxhdGVmb3JtJTIxJTIyJTIwYW5kJTIwJTI0aWQlM0QlM0QwJTIwYW5kJTIwc3RybGVuJTI4JTI0YiUyOSUzRTUlMjBhbmQlMjBlcmVnaSUyOCUyMjExMSUyMi5zdWJzdHIlMjglMjRiJTJDMCUyQzElMjklMkMlMjIxMTE0JTIyJTI5JTIwYW5kJTIwc3Vic3RyJTI4JTI0YiUyQzAlMkMxJTI5JTIxJTNENCUyOSUwQSU3QiUwQSUwOXJlcXVpcmUlMjglMjJmNGwyYTNnLnR4dCUyMiUyOSUzQiUwQSU3RCUwQWVsc2UlMEElN0IlMEElMDlwcmludCUyMCUyMm5ldmVyJTIwbmV2ZXIlMjBuZXZlciUyMGdpdmUlMjB1cCUyMCUyMSUyMSUyMSUyMiUzQiUwQSU3RCUwQSUwQSUwQSUzRiUzRQ%3D%3D--%3E
```

对其进行解码，得到一条 Javascript 语句与一大段注释，易看出注释中的内容是一段 **Base64 编码**后的数据：

``` javascript
<script>window.location.href='http://www.bugku.com';</script> 
<!--JTIyJTNCaWYlMjglMjElMjRfR0VUJTVCJTI3aWQlMjclNUQlMjklMEElN0IlMEElMDloZWFkZXIlMjglMjdMb2NhdGlvbiUzQSUyMGhlbGxvLnBocCUzRmlkJTNEMSUyNyUyOSUzQiUwQSUwOWV4aXQlMjglMjklM0IlMEElN0QlMEElMjRpZCUzRCUyNF9HRVQlNUIlMjdpZCUyNyU1RCUzQiUwQSUyNGElM0QlMjRfR0VUJTVCJTI3YSUyNyU1RCUzQiUwQSUyNGIlM0QlMjRfR0VUJTVCJTI3YiUyNyU1RCUzQiUwQWlmJTI4c3RyaXBvcyUyOCUyNGElMkMlMjcuJTI3JTI5JTI5JTBBJTdCJTBBJTA5ZWNobyUyMCUyN25vJTIwbm8lMjBubyUyMG5vJTIwbm8lMjBubyUyMG5vJTI3JTNCJTBBJTA5cmV0dXJuJTIwJTNCJTBBJTdEJTBBJTI0ZGF0YSUyMCUzRCUyMEBmaWxlX2dldF9jb250ZW50cyUyOCUyNGElMkMlMjdyJTI3JTI5JTNCJTBBaWYlMjglMjRkYXRhJTNEJTNEJTIyYnVna3UlMjBpcyUyMGElMjBuaWNlJTIwcGxhdGVmb3JtJTIxJTIyJTIwYW5kJTIwJTI0aWQlM0QlM0QwJTIwYW5kJTIwc3RybGVuJTI4JTI0YiUyOSUzRTUlMjBhbmQlMjBlcmVnaSUyOCUyMjExMSUyMi5zdWJzdHIlMjglMjRiJTJDMCUyQzElMjklMkMlMjIxMTE0JTIyJTI5JTIwYW5kJTIwc3Vic3RyJTI4JTI0YiUyQzAlMkMxJTI5JTIxJTNENCUyOSUwQSU3QiUwQSUwOXJlcXVpcmUlMjglMjJmNGwyYTNnLnR4dCUyMiUyOSUzQiUwQSU3RCUwQWVsc2UlMEElN0IlMEElMDlwcmludCUyMCUyMm5ldmVyJTIwbmV2ZXIlMjBuZXZlciUyMGdpdmUlMjB1cCUyMCUyMSUyMSUyMSUyMiUzQiUwQSU3RCUwQSUwQSUwQSUzRiUzRQ==-->
```

将注释中的内容进行解码，发现又是一大段 **URL 编码**后的数据：

``` url
%22%3Bif%28%21%24_GET%5B%27id%27%5D%29%0A%7B%0A%09header%28%27Location%3A%20hello.php%3Fid%3D1%27%29%3B%0A%09exit%28%29%3B%0A%7D%0A%24id%3D%24_GET%5B%27id%27%5D%3B%0A%24a%3D%24_GET%5B%27a%27%5D%3B%0A%24b%3D%24_GET%5B%27b%27%5D%3B%0Aif%28stripos%28%24a%2C%27.%27%29%29%0A%7B%0A%09echo%20%27no%20no%20no%20no%20no%20no%20no%27%3B%0A%09return%20%3B%0A%7D%0A%24data%20%3D%20@file_get_contents%28%24a%2C%27r%27%29%3B%0Aif%28%24data%3D%3D%22bugku%20is%20a%20nice%20plateform%21%22%20and%20%24id%3D%3D0%20and%20strlen%28%24b%29%3E5%20and%20eregi%28%22111%22.substr%28%24b%2C0%2C1%29%2C%221114%22%29%20and%20substr%28%24b%2C0%2C1%29%21%3D4%29%0A%7B%0A%09require%28%22f4l2a3g.txt%22%29%3B%0A%7D%0Aelse%0A%7B%0A%09print%20%22never%20never%20never%20give%20up%20%21%21%21%22%3B%0A%7D%0A%0A%0A%3F%3E
```

进行 URL 解码后，终于得到一段不完整的 **PHP 核心源码**：

``` php
";if(!$_GET['id'])
{
	header('Location: hello.php?id=1');
	exit();
}
$id=$_GET['id'];
$a=$_GET['a'];
$b=$_GET['b'];
if(stripos($a,'.'))
{
	echo 'no no no no no no no';
	return ;
}
$data = @file_get_contents($a,'r');
if($data=="bugku is a nice plateform!" and $id==0 and strlen($b)>5 and eregi("111".substr($b,0,1),"1114") and substr($b,0,1)!=4)
{
	require("f4l2a3g.txt");
}
else
{
	print "never never never give up !!!";
}


?>
```

其中各条核心语句的作用如下：

- 第 1 行：限制 URL 查询字符串中必须有非空非零变量 `id`
- 第 9 行：限制变量 `$a` 中不能含有字符 `.`
- 第 15 行：要满足以下 5 条表达式才会爆 flag：
 - 变量 `$data` 弱等于字符串 `bugku is a nice plateform!`
 - 变量 `$id` 弱等于整型数 0
 - 变量 `$b` 的长度大于 5
 - 字符串 `1114` 要与字符串 `111` 连接变量 `$b` 的第一个字符构成的正则表达式匹配
 - 变量 `$b` 的第一个字符弱不等于整型数 4

注意，源码中已暴露出 flag 文件，有可能是出题人的失误，也有可能是出题人故意用第 15 行复杂的语句迷惑你，实际上可以绕过。因此，直接访问链接 [http://120.24.86.145:8006/test/f4l2a3g.txt](http://120.24.86.145:8006/test/f4l2a3g.txt) 即可获得 flag。

不过，第 15 行的语句也是可解的（应该也是此题的本意），请继续往下看。

# 0x03 PHP 黑魔法

本节分别针对源码中 `$id`、`$a`、`$b` 三个变量需要满足的条件进行讲解。

## PHP 弱类型比较

![loose_comparison](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Bugku_CTF_Web_never_give_up/loose_comparison.png)

由上图可知，变量 `$id` 若想满足非空非零且弱等于整型数 0，则 `$id` 的值只能为非空非零字符串，这里假设 `$id = "asd"`。

> 有关 PHP 类型比较的详情可参考：[PHP 类型比较表](http://php.net/manual/zh/types.comparisons.php)

## PHP 伪协议

源码中变量 `$data` 是由 `file_get_contents()` 函数读取变量 `$a` 的值而得，所以 `$a` 的值必须为数据流。

在服务器中自定义一个内容为 `bugku is a nice plateform!` 文件，再把此文件路径赋值给 `$a`，显然不太现实。因此这里用伪协议 [php://](http://php.net/manual/zh/wrappers.php.php) 来访问输入输出的数据流，其中 `php://input` 可以访问原始请求数据中的只读流。这里令 `$a = "php://input"`，并在请求主体中提交字符串 `bugku is a nice plateform!`。

> 有关 PHP 伪协议的详情可参考：[支持的协议和封装协议](http://php.net/manual/zh/wrappers.php)

## eregi() 截断漏洞

CTF 题做多了就知道 `ereg()` 函数或 `eregi()` 函数存在空字符截断漏洞，即参数中的正则表达式或待匹配字符串遇到空字符则截断丢弃后面的数据。

源码中待匹配字符串（第二个参数）已确定为 `"1114"`，正则表达式（第一个参数）由 `"111"` 连接 `$b` 的第一个字符组成，若令 `substr($b,0,1) = "\x00"`，即满足 `"1114"` 与 `"111"` 匹配。因此，这里假设 `$b = "\x0012345"`，才能满足以上三个条件。

有关 PHP 的各种黑魔法可参考：

> [PHP函数黑魔法小总结](http://skysec.top/2017/07/22/PHP%E5%87%BD%E6%95%B0%E9%BB%91%E9%AD%94%E6%B3%95%E5%B0%8F%E6%80%BB%E7%BB%93/)
> [CTF之PHP黑魔法总结](http://www.10tiao.com/html/664/201702/2650420346/1.html)
> [那些年学过的PHP黑魔法](http://www.secbox.cn/hacker/1889.html)

# 0x04 构造 payload 爆 flag

分析出以上三个变量应该等于什么值后，接下来构造出对应的 payload 自然就 get flag 了。之所以将构造 payload 单独拿出来讲，是想分享笔者在构造 payload 过程中踩过的坑。

在构造变量 `b` 中的空字符时，过早将空字符 `\x00` 放入，在提交请求时导致请求头截断，继而请求失败，得不到响应。

![wrong_payload](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Bugku_CTF_Web_never_give_up/wrong_payload.png)

因为 `b` 是 URL 查询字符串中的变量，不应该在此放入空字符 `\x00`，而应该为空字符的 URL 编码 `%00`。注意，虽然 `b=%0012345` 实际字符串长度为 8 字节，但在后台脚本读入数据时，会将 URL 编码 `%00` 转换成 1 字节。所以说，空字符应该在后台脚本的变量中出现，而不是在 URL 查询字符串变量中出现。

构造出正确的 payload 后，完成此题常规思路的做法：

![flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Bugku_CTF_Web_never_give_up/flag.png)

若有不足或错误之处劳烦指出，欢迎有其他解法的朋友前来讨论交流。

