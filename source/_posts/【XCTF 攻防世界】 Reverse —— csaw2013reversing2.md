---
title: 【XCTF 攻防世界】 Reverse —— csaw2013reversing2
copyright: true
date: 2019-05-28 22:53:48
tags: [XCTF,攻防世界,CTF,Writeup,Reverse,Disassembly,Decompile,IDA,PE]
categories: [InfoSec,Reverse]
---

# 0x00 前言

此题出自 CSAW CTF 2014，是分值为 200 的 Reverse 题，重点是使用 IDA **对关键函数的逆向分析，并修改程序的运行流程**后，得到正确结果。

题目链接：[https://adworld.xctf.org.cn/task/answer?type=reverse&number=4&grade=0&id=5081](https://adworld.xctf.org.cn/task/answer?type=reverse&number=4&grade=0&id=5081)

<!-- more -->

![question](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/question.png)

# 0x01 逆向分析主函数

依据题目的提示，双击程序后果然发现运行结果全是乱码：

![mess](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/mess.png)

在 Kali Linux 中用 `file` 命令查看程序，发现是 Windows 下的 32 位 PE 文件：

![file](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/file.png)

接下来，使用 IDA Pro 7.0 (32 bit) 打开程序，默认进入主函数的反汇编窗口，按下 **F5** 后进行反编译，自动生成类 C 语言的伪代码：

![main](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/main.png) 

可见，若 `sub_40102A()` 或 `IsDebuggerPresent()` 的返回值为真，则执行调试断点指令 `__debugbreak()`、子函数 `sub_401000(v3 + 4, lpMem)`、结果进程函数 `ExitProcess(0xFFFFFFFF)`，否则直接执行 `MessageBoxA(0, lpMem + 1, "Flag", 2u)`，弹出全是乱码的 Flag 提示框。

双击 `sub_40102A()` 查看其反编译代码，发现返回值恒为零：

![sub_40102A](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/sub_40102A.png)

而对于库函数 [`IsDebuggerPresent()`](https://docs.microsoft.com/en-us/windows/desktop/api/debugapi/nf-debugapi-isdebuggerpresent)，若程序处于调试模式下，则返回值为非零；若未处于调试模式下，则返回值为零。显然，程序不处于调试模式下，即无法满足 `if` 语句的条件。

双击 `sub_401000()` 查看其反编译代码，目测是对以上乱码数据的解密函数：

![sub_401000](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/sub_401000.png)

综上，解题思路大致为：**进入 `if` 语句块，跳过调试断点，并执行解密函数，最终弹框输出 Flag。**

# 0x02 修改运行流程

在主函数的反汇编窗口中，核心的语句块如下：

![core](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/core.png)

首先，`int 3` 中断即为调试断点指令，需将其改为空指令 `nop`。

将光标置于中断指令所在行，依次点击 **Edit -> Patch program -> Assemble**，弹出指令修改框：

![modify_int](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/modify_int.png)

将 `int 3` 改为 `nop` 后点击 **OK** 即可。

> 小贴士：点击 **OK** 后，IDA 会自动弹出下一条指令的修改框，通常无需修改，点击 **Cancel** 即可。

根据上述操作，依次将 `jmp short loc_4010EF` 修改为 `jmp short loc_4010B9`，将 `jz short loc_4010B9` 修改为 `jmp short loc_401096`，修改完运行流程如下：

![modified](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/modified.png)

最后，依次点击 **Edit -> Patch program -> Apply patches to input file...**，弹出设置框，选择待打补丁程序，按需选择对原程序进行备份：

![apply_patches](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/apply_patches.png)

设置完毕后点击 **OK** 即可。找到修改后的程序，双击执行可获得 `flag{reversing_is_not_that_hard!}`：

![flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/XCTF_%E6%94%BB%E9%98%B2%E4%B8%96%E7%95%8C_Reverse_csaw2013reversing2/flag.png)

# 0x03 小结

本题要求挑战者精确定位核心函数，分析并正确修改程序的运行流程，得到解密数据。对于逆向初学者而言，不仅锻炼了基础的逆向分析能力，还掌握了使用 IDA 修改汇编指令等基本操作。

本题的其他 writeup 还可参考：

> [CSAW CTF 2014: csaw2013reversing2.exe](https://github.com/ctfs/write-ups-2014/tree/master/csaw-ctf-2014/csaw2013reversing2.exe)
> [CSAW CTF Quals 2014 - csaw2013reversing2.exe (200pts) writeup](https://www.mrt-prodz.com/blog/view/2014/09/csaw-ctf-quals-2014---csaw2013reversing2exe-200pts-writeup)
> [CSAW CTF QUAL 2014 – CSAW2013REVERSING2.EXE WRITEUP](https://infamoussyn.wordpress.com/2014/09/22/csaw-ctf-qual-2014-csaw2013reversing2-exe-writeup/)