---
title: 【巅峰极客 2018】 Misc —— warmup
copyright: true
date: 2018-07-29 21:08:54
tags: [巅峰极客,CTF,Writeup,Steganography,Encoding,Crypto]
categories: [InfoSec,Misc]
mathjax: true
---

# 0x00 前言

本届「巅峰极客」网络安全技能挑战赛共有三道 Misc 题，此题是最简单的一道，分值为 100pt，难度不大，涉及**图片隐写**与**三种特殊的编码方式**，主要考察选手们对常见 Misc 题知识点的综合运用能力。 题目下载链接如下：

- 下载链接：[warmup.bmp](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/%E5%B7%85%E5%B3%B0%E6%9E%81%E5%AE%A2_2018_Misc_warmup/warmup.bmp)

<!-- more -->

# 0x01 LSB 隐写

[**RGB**](https://baike.baidu.com/item/RGB) 色彩模式是工业界的一种颜色标准，通过红（R）、绿（G）、蓝（B）三原色的相互叠加得到各种颜色。

**24 比特模式**是当前最主流的表示方法，即使用三个 8 比特无符号整数分别代表红色、绿色和蓝色，每个像素点用 24 比特表示，可以产生 $2^{24} = 16,777,216$ 种颜色组合。

**LSB 隐写**是指将信息隐藏在每个颜色通道的最低有效位（Least Significant Bit）。由于改变的是每个颜色通道的最低位，对颜色改变的影响极小，因此用肉眼是无法察觉出来的。

显然，每个像素的三个通道可以隐藏 3 比特信息；每个 ASCII 字符有 8 比特，至少需要三个像素点，若只隐藏在某一个颜色通道，则需要八个像素点。

下面以**连续八个像素点的红色通道隐藏字符 `a`** 为例进行讲解：

| 像素序号 | 像素隐写前         | 隐写信息 | 像素隐写后         |
| -------- | ------------------ | -------- | ------------------ |
| 1        | (**35**, 21, 33)   | 0        | (**34**, 21, 33)   |
| 2        | (**96**, 89, 52)   | 1        | (**97**, 89, 52)   |
| 3        | (**57**, 211, 123) | 1        | (**57**, 211, 123) |
| 4        | (**48**, 110, 245) | 0        | (**48**, 110, 245) |
| 5        | (**113**, 201, 97) | 0        | (**112**, 201, 97) |
| 6        | (**62**, 52, 134)  | 0        | (**62**, 52, 134)  |
| 7        | (**168**, 65, 159) | 0        | (**168**, 65, 159) |
| 8        | (**240**, 76, 193) | 1        | (**241**, 76, 193) |

字符 `a` 的二进制 ASCII 码是 `01100001`，每个比特分别隐写在每个像素点红色通道的最低有效位。无论隐写前该颜色通道的值或奇或偶，若隐写信息为 `0` 比特，则隐写后值为偶数；若隐写信息为 `1` 比特，则隐写后值为奇数。

# 0x02 定位隐写点

[**Stegsolve**](http://www.caesum.com/handbook/stego.htm) 是专用于分析图片隐写的大杀器，用 Java 语言编写，主要功能如下所示：

- 显示图片文件的格式信息。
- 迅速浏览每个颜色通道的位平面，以及图片的一些简单变换。
- 摘取任意颜色通道比特位的信息。
- 按特定偏移量移动解析图片。
- 剥离动图的每一帧。
- 合并两张不同的图片。

当我们用 Stegsolve 加载图片 warmup.bmp 后，分别在 RGB 通道最低位的位平面上方发现了异常，由此猜测可能存在隐写。

![rgb-lsb](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/peak-geek-2018-misc-warmup/rgb-lsb.png)

# 0x03 摘取隐写信息

## Stegsolve 摘取数据

点击 Stegsolve 的 **Analyse -> Data Extract**，在红色通道最低位上打勾，点击 **Preview** 后，即可在提取数据的上方发现隐写信息，最后点击 **Save Bin** 保存为二进制文件 red.bin。

![red-data-extract](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/peak-geek-2018-misc-warmup/red-data-extract.png)

接着对绿色与蓝色通道进行相同操作，分别得到二进制文件 green.bin 和 blue.bin，用文本编辑器打开后，即可摘取数据上方的隐写信息。

![rgb-info](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/peak-geek-2018-misc-warmup/rgb-info.png)

除了使用 Stegsolve 摘取数据外，还可以尝试另一个自动化图片隐写检测工具 zsteg。

## zsteg 摘取数据

[**zsteg**](https://github.com/zed-0xff/zsteg) 是俄罗斯黑客开发的一款开源工具，专用于检测 PNG 与 BMP 格式图片中的隐写信息，用 Ruby 语言开发，主要用法如下所示：

```bash
$ zsteg -h

Usage: zsteg [options] filename.png [param_string]

    -c, --channels X                 channels (R/G/B/A) or any combination, comma separated
                                     valid values: r,g,b,a,rg,rgb,bgr,rgba,...
    -l, --limit N                    limit bytes checked, 0 = no limit (default: 256)
    -b, --bits N                     number of bits (1..8), single value or '1,3,5' or '1-8'
        --lsb                        least significant BIT comes first
        --msb                        most significant BIT comes first
    -P, --prime                      analyze/extract only prime bytes/pixels
    -a, --all                        try all known methods
    -o, --order X                    pixel iteration order (default: 'auto')
                                     valid values: ALL,xy,yx,XY,YX,xY,Xy,bY,...
    -E, --extract NAME               extract specified payload, NAME is like '1b,rgb,lsb'

    -v, --verbose                    Run verbosely (can be used multiple times)
    -q, --quiet                      Silent any warnings (can be used multiple times)
    -C, --[no-]color                 Force (or disable) color output (default: auto)

PARAMS SHORTCUT
	zsteg fname.png 2b,b,lsb,xy  ==>  --bits 2 --channel b --lsb --order xy
```

在 Kali Linux 中，自带 Ruby 的包管理器 RubyGems，因此直接用以下命令安装后即可使用：

```bash
$ gem install zsteg
```

切换至图片 warmup.bmp 所在目录下，分别输入以下命令：

```
$ zsteg warmup.bmp --bits 1 --channel r --lsb --order xy --limit 2048
$ zsteg warmup.bmp --bits 1 --channel g --lsb --order xy --limit 2048
$ zsteg warmup.bmp --bits 1 --channel b --lsb --order xy --limit 2048
```

- `--bits 1`：每次只摘取颜色通道中的第 1 个比特。
- `--channel r`：只摘取红色通道的比特位。
- `--lsb`：按最低有效位优先的顺序进行摘取。
- `--order xy`：按照从左至右、从上至下的顺序对图像素点进行摘取。
- `--limit 2048`：最多摘取输出 2048 字节。

即可自动摘取出隐写在图片内的信息：

![rgb-zsteg](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/peak-geek-2018-misc-warmup/rgb-zsteg.png)

仔细的读者还会发现，有一个懒人专属的选项 `--all`，可将所有可能的摘取方法都尝试一遍：

```
$ zsteg warmup.bmp --all
```

最终在结果中挑选出可能的隐写信息：

![rgb-zsteg-all](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/peak-geek-2018-misc-warmup/rgb-zsteg-all.png)

# 0x04 辨识特殊编码

上述分别由 RGB 通道得到的隐写信息，属于三种特殊的编码方式，同时也是  [Andreas Gohr](https://www.splitbrain.org/personal) 的开源项目，可在其博客上的 [Brainfuck/Ook! Obfuscation/Encoding](https://www.splitbrain.org/services/ook) 在线工具中解码。

以上编码方式的实现，读者不必知道其原理，只需在做题过程中能辨识出来是哪种编码即可，解码的工作留给工具完成。

## Short Ook!

由 red.bin 得到的隐写信息如下所示：

```Short_Ook!
..... ..... ..... ..... !?!!. ?.... ..... ..... ..... .?.?! .?... .!...
..... ..... !.?.. ..... !?!!. ?!!!! !!?.? !.?!! !!!.. ..... ..... .!.?.
..... ...!? !!.?. ..... ..?.? !.?.. ..... .!.?. ..... ...!? !!.?! !!!!!
!!?.? !.?!! !!!!! !!!!! !!!.! !!!!. ?.... ..... ....! ?!!.? !!!!! !!!!!
!!?.? !.?!! !!!!! !!!!! !!!!! .!!!! !.!!! !!!!! !.... ..... !.!!! .....
..!.! !!!!! !!!!! !!!!! !!!.? .
```

以上编码方式称为 **Short Ook!**，其包含的字符集如下所示：

| 字符 | 含义 | ASCII 码   |
| ---- | ---- | ---------- |
| !    | 叹号 | 33（\x21） |
| .    | 句号 | 46（\x2E） |
| ?    | 问号 | 63（\x3F） |

将上述隐写信息用工具解码后得到字符串 `flag{db640436-`：

![short-ook!](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/peak-geek-2018-misc-warmup/short-ook!.png)

## Ook!

由 green.bin 得到的隐写信息如下所示：

```Ook!
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook!
Ook? Ook! Ook! Ook. Ook? Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook.
Ook. Ook. Ook. Ook. Ook? Ook. Ook? Ook! Ook. Ook? Ook. Ook. Ook. Ook. Ook.
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook. Ook. Ook. Ook! Ook. Ook! Ook!
Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. Ook. Ook. Ook. Ook. Ook.
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook. Ook? Ook. Ook. Ook. Ook. Ook.
Ook. Ook. Ook! Ook? Ook! Ook! Ook. Ook? Ook! Ook! Ook! Ook! Ook! Ook! Ook?
Ook. Ook? Ook! Ook. Ook? Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. Ook. Ook.
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook. Ook!
Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. Ook. Ook. Ook. Ook. Ook. Ook.
Ook. Ook. Ook. Ook. Ook! Ook. Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook!
Ook! Ook! Ook. Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. Ook? Ook. Ook. Ook.
Ook. Ook. Ook. Ook. Ook! Ook? Ook! Ook! Ook. Ook? Ook. Ook. Ook. Ook. Ook.
Ook. Ook? Ook. Ook? Ook! Ook. Ook? Ook. Ook. Ook. Ook. Ook! Ook. Ook! Ook!
Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook! Ook. Ook! Ook. Ook. Ook. Ook.
Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook. Ook! Ook. Ook? Ook.
```

以上编码方式称为 **Ook!**，其包含的字符集如下所示：

| 字符 | 含义       | ASCII 码    |
| ---- | ---------- | ----------- |
| !    | 叹号       | 33（\x21）  |
| .    | 句号       | 46（\x2E）  |
| ?    | 问号       | 63（\x3F）  |
| O    | 大写字母 O | 79（\x4F）  |
| k    | 小写字母 k | 107（\x6B） |
| o    | 小写字母 o | 111（\x6F） |

将上述隐写信息用工具解码后得到字符串 `7839-4050-8339`：

![ook!](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/peak-geek-2018-misc-warmup/ook!.png)

## Brainfuck

由 blue.bin 得到的隐写信息如下所示：

```
+++++ +[->+ +++++ <]>++ +++++ ++.<+ ++[-> +++<] >+.-- .<+++ +++[- >++++
++<]> +++++ +++.< +++++ +[->- ----- <]>-- --.-- .---- -.<++ +++++ [->++
+++++ <]>++ +.--- .<+++ +++[- >---- --<]> ----- ----- ..--. <++++ ++[->
+++++ +<]>+ +++++ +++++ +.<++ +++[- >++++ +<]>+ .<
```

以上编码方式称为 **Brainfuck**，其包含的字符集如下所示：

| 字符 | 含义     | ASCII 码   |
| ---- | -------- | ---------- |
| +    | 加号     | 43（\x2B） |
| -    | 减号     | 45（\x2D） |
| .    | 句号     | 46（\x2E） |
| <    | 小于号   | 60（\x3C） |
| >    | 大于号   | 62（\x3E） |
| [    | 左方括号 | 91（\x5B） |
| ]    | 右方括号 | 93（\x5D） |

将上述隐写信息用工具解码后得到字符串 `-75a972fc553c}`：

![brainfuck](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/peak-geek-2018-misc-warmup/brainfuck.png)

# 0x05 总结

对以上三种编码进行解码后，将得到的字符串拼接起来即得到本题的 flag：

```flag
flag{db640436-7839-4050-8339-75a972fc553c}
```

笔者借助此题，将常见的图片隐写分析方法与特殊的编码方式进行了总结，既有助于初学者学习理解，也方便自己日后查看。文中的不足或错误之后还望读者多多包涵，不吝赐教。

最后贴出两篇较好的 writeup 供读者学习：

> [WriteUp:巅峰极客 Misc](https://ihomura.cn/2018/07/25/WriteUp-%E5%B7%85%E5%B3%B0%E6%9E%81%E5%AE%A2-Misc/)
> [巅峰极客第一场CTF部分writeup](http://120.79.189.7/?p=453)