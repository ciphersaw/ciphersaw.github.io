---
title: 玩转 PHP eval() 中的单双引号
date: 2017-11-16 19:17:16
tags: [php,web]
categories: [Programming,PHP]
copyright: true
---

# 0x00 前言

在一次偶然学习 PHP eval() 函数的过程中，发现[官方文档](http://php.net/manual/zh/function.eval.php)对该函数的示例说明很有意思，刚开始有点无法理解，想通之后便记录下此次辛酸的思考历程。

<!-- more -->

# 0x01 eval() 函数

官方文档将 eval() 函数的解释为**【把字符串参数当作 PHP 代码执行】**，说明如下：

``` php
mixed eval ( string $code )
```

- 参数 `$code` 是需要被执行的字符串
- 返回值类型 `mixed` 是指存在多种不同类型的返回值，默认返回 **NULL**；如果代码中 **return** 了一个值，则该值也作为函数的返回值返回；如果代码中出现解析错误，则在 PHP7 之前，返回 **FALSE**，在 PHP7 之后，抛出 ParseError 异常。

下面说明几点注意事项：

1. 字符串中代码不要忘记语句末尾的分号；
2. return 语句会终止当前字符串的执行；
3. eval() 函数中任何的变量定义或修改，都会在函数结束后被保留；
4. 若在代码执行过程中产生致命错误，则整个脚本都会终止。

接下来就是有趣的例子 —— 简单的文本合并：

``` php
<?php
$string = 'cup';
$name = 'coffee';
$str = 'This is a $string with my $name in it.';
echo $str. "\n";
eval("\$str = \"$str\";");
echo $str. "\n";
?>
```

输出结果为：

```
This is a $string with my $name in it.
This is a cup with my coffee in it.
```

刚开始看到输出结果，怎么想也想不通，`eval("\$str = \"$str\";");` 语句不就把字符串当成 PHP 代码来执行吗？为什么去掉 eval() 函数后的语句 `$str = "$str";` 的输出结果就变成了 `This is a $string with my $name in it.` 呢？

# 0x02 示例解析

要理解上述现象，首先要知道以下两条规则：

## **Rule1：单引号内不解析变量，双引号内解析变量**

下面给出 Rule1 的 PoC：

``` php
<?php 
$name = 'Alice';
$x = 'hello $name';  //单引号内变量不被解析
$y = "hello $name";  //双引号内变量会被解析
echo $x, '<br />';
echo $y, '<br />';	
?> 
```

结果输出：

```
hello $name
hello Alice
```

因此在 `eval("\$str = \"$str\";");` 语句中，`\$str` 是为了变量不被解析成字符串，`\"` 是为了转义内层的双引号，避免与外层的双引号闭合。

## **Rule2：php中嵌套引号的解析是由外向里的，且只解析一次**

换句话说，即只解析最外层的引号，下面给出 Rule2 的 PoC：

``` php
<?php 
$name = 'Alice';

$x = 'hello $name';      //单引号内变量不被解析
echo $x, '<br />';       //直接输出变量$x，即字符串hello $name
echo '$x', '<br />';     //变量$x在单引号内不被解析，故输出字符串$x
echo "$x", '<br />';     //变量$x在双引号内会被解析，故输出$x的值，即字符串hello $name
echo "'$x'", '<br />';   //只有双引号起作用，变量$x会被解析，故输出字符串'hello $name'
echo '"$x"', '<br />';   //只有单引号起作用，变量$x不被解析，故输出字符串"$x"
echo "'\$x'", '<br />';  //只有双引号起作用，变量$x被转义而不被解析，故输出字符串'$x'
echo '"\$x"', '<br />';  //只有单引号起作用，变量$x不被解析，故输出字符串"\$x"
echo '\'$x\'', '<br />'; //只有外层单引号起作用，内层单引号需转义，变量$x不被解析，故输出字符串'\$x'
echo "\"$x\"", '<br />'; //只有外层双引号起作用，内层双引号需转义，变量$x会被解析，故输出字符串"hello $name"

echo "<br />";

$y = "hello $name";      //双引号内变量会被解析
echo $y, '<br />';       //直接输出变量$y的实际值，即字符串hello Alice
echo '$y', '<br />';     //变量$y在单引号内不被解析，故输出字符串$y
echo "$y", '<br />';     //变量$y在双引号内会被解析，故输出$y的值，即字符串hello Alice
echo "'$y'", '<br />';   //只有双引号起作用，变量$y会被解析，故输出字符串'hello Alice'
echo '"$y"', '<br />';   //只有单引号起作用，变量$y不被解析，故输出字符串"$y"
echo "'\$y'", '<br />';  //只有双引号起作用，变量$y被转义而不被解析，故输出字符串'$y'
echo '"\$y"', '<br />';  //只有单引号起作用，变量$y不被解析，故输出字符串"\$y"
echo '\'$y\'', '<br />'; //只有外层单引号起作用，内层单引号需转义，变量$y不被解析，故输出字符串'\$y'
echo "\"$y\"", '<br />'; //只有外层双引号起作用，内层双引号需转义，变量$y会被解析，故输出字符串"hello Alice"
?> 
```

结果输出：

```
hello $name
$x
hello $name
'hello $name'
"$x"
'$x'
"\$x"
'$x'
"hello $name"

hello Alice
$y
hello Alice
'hello Alice'
"$y"
'$y'
"\$y"
'$y'
"hello Alice"
```

下面开始解析以下代码，为了方便说明，对官网文档中示例代码的变量名稍作修改，并将 eval() 函数中的字符串语句抽离出来，单独执行：

``` php
<?php 
$string = 'cup';
$name = 'coffee';
$origin = 'This is a $string with my $name in it.';
echo $origin. "\n";

$result_1 = "$origin";
echo $result_1. "\n";

eval("\$result_2 = \"$origin\";");
echo $result_2. "\n";
?> 
```

以上代码输出如下，也就是本人困惑的地方：

```
This is a $string with my $name in it.
This is a $string with my $name in it.
This is a cup with my coffee in it.
```

 - `$origin` 的输出没有问题，根据 Rule1 即可理解；
 - `$result_1` 的输出为什么不变呢？理解了 `$result_1 = "$origin";` 就明白了。根据 Rule1，`$origin` 会被解析，得到它本身的值，即字符串 `'This is a $string with my $name in it.'` （注意两边的引号与 `$origin` 的相同，此处为单引号），因此 `$result_1` 的输出与 `$origin` 一样；
 - `$result_2` 为什么会改变，是最难理解的。根据 Rule2，可知 eval() 函数最外层的双引号会被解析，内层被转义的双引号原封不动，因此函数内执行的语句相当于 `$result_2 = "This is a $string with my $name in it."`，此时字符串两边变成了双引号，因此 `$result_2` 的输出会将字符串中的变量转义。

讲到这里，肯定有人疑问：不是说转义后字符串两边引号跟 `$origin` 相同吗？按理说应该是 `$result_2 = "'This is a $string with my $name in it.'"`，那么输出应该跟 Rule2 PoC 中的 `echo "'$x'"` 一样。请注意，此处因为有个 eval() 函数，所以可以有双层转义，即第一层是 eval() 函数最外层的双引号，第二层是执行语句中的双引号，而类似 `echo "'$x'"` 的引号嵌套，只有单层转义，因此 `result_1` 中 `'This is a $string with my $name in it.'` 的单引号与 `$origin` 的相同，而 `result_2` 中 `"This is a $string with my $name in it."` 的引号则由第二层的双引号赋予。

可能还有人不死心，非要在赋值语句中构造双层转义，那我们就来试试看吧。在 `$result_1 = "$origin";` 的基础上，再加个双引号吧，得到 `$result_1 = ""$origin"";`，简直完美、帅气、机智...

```
PHP Parse error:  syntax error, unexpected '$origin' (T_VARIABLE)
```

咳咳，已经丧失理智到忘记相邻两个双引号会闭合吗？不行就转义吧，于是有 `$result_1 = "\"$origin\"";`，再于是就有 `请参见 Rule2 PoC 吧同学`，以及脑海中一堆类似 `$result_1 = ''$origin'';`、`$result_1 = '\'$origin\'';` 等等的语句在风中凌乱。这个故事告诉我们一个道理：**单凭赋值语句是完成不了字符串单双引号转换的**。

----------

# 0x03 玩法进阶

对于官方文档中示例代码的疑惑，看到分割线以上就 OK 了，想再深入理解的可继续看下面的玩法（玩法之间互不干扰）：

## **玩法1：将 eval() 函数的第二层转义改为单引号（注意这里单引号不需要转义了，因为第一层是双引号）：**

``` php
eval("\$result_2 = '$origin';");
```

此时输出结果为：

```
This is a $string with my $name in it.
This is a $string with my $name in it.
This is a $string with my $name in it.
```

如果理解了上面 `result_2` 的输出原理，结果容易理解，即相当于执行了 `$result_2 = 'This is a $string with my $name in it.'`，自然与 `$origin` 和 `result_1` 相同。

## **玩法2：将 `$origin` 字符串两边改为双引号：**

``` php
$origin = "This is a $string with my $name in it.";
```

此时输出结果为：

```
This is a cup with my coffee in it.
This is a cup with my coffee in it.
This is a cup with my coffee in it.
```

这种情况也容易理解，原始字符串一开始就是双引号，那自然是一直转义到底。

## **玩法3：将 eval() 函数的第二层转义改为单引号，并将 `$origin` 字符串两边改为双引号：**

``` php
$origin = "This is a $string with my $name in it.";
eval("\$result_2 = '$origin';");
```

此时输出结果为：

```
This is a cup with my coffee in it.
This is a cup with my coffee in it.
This is a cup with my coffee in it.
```

输出结果与玩法2相同，这里注意一点，就是 eval() 函数第一层转义后，返回值为 `$result_2 = 'This is a cup with my coffee in it.'`，即得到的是所有变量都转义后的字符串。

## **玩法4：将 eval() 函数的第一层转义改为单引号（注意这第二层的双引号不需要转义了，因为第一层是单引号，并且单号内本身就不会转义 `$`，所以 `$` 前面的转义字符也可以去除）：**

``` php
eval('$result_2 = "$origin";');
```

此时输出结果为：

```
This is a $string with my $name in it.
This is a $string with my $name in it.
This is a $string with my $name in it.
```

输出结果与玩法1相同，但输出原理却不同了。第一层转义时，`$origin` 是原封不动保留下来的，即 `$result_2 = "$origin"`，跟 `result_1` 的情况完全相同。

## **玩法5：将 eval() 函数的第一层和第二层转义都改为单引号（注意这时第二层的单引号就需要转义了）：**

``` php
eval('$result_2 = \'$origin\';');
```

此时输出结果为：

```
This is a $string with my $name in it.
This is a $string with my $name in it.
$origin
```

这次的输出结果有点意思，跟玩法4一样，在第一层转义时，`$origin` 原封不动保留下来，即 `$result_2 = '$origin'`，但在第二层转义时也要原封不动地输出字符串 `$origin`。

还有两种玩法（即分别在玩法4和玩法5的基础上，将 `$origin` 字符串两边改为双引号）大同小异，这里就不详述了，有兴趣的读者可以自行推导验证。