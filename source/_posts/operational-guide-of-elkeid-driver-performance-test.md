---
title: Elkeid Driver 性能测试操作指引
copyright: true
date: 2023-05-02 22:16:21
tags: [Linux,Kernel,Bash,C,Python,HIDS,Elkeid,LTP,Benchmark]
categories: [InfoSec,HIDS]
---

# 0x00 前言

在研究字节跳动 [Elkeid](https://github.com/bytedance/Elkeid) HIDS 开源项目的过程中，发现其 [Driver](https://github.com/bytedance/Elkeid/blob/main/driver/README.md) 组件通过 [Kprobe](https://docs.kernel.org/trace/kprobes.html) 内核探测技术，能够在内核层 hook 系统调用函数，为入侵检测引擎提供了更加丰富可靠的数据源。

然而，在 Driver 组件介绍文档中的**性能测试**部分，只粗略地给出了测试机器配置、压测命令及测试结果，**缺少对测试操作流程的详细描述**，导致社区开发者在修改代码后，难以自行完成性能测试。

因此，笔者将根据测试结果查阅相关资料，倒推出测试操作流程，以作为 Elkeid Driver 组件开发者的参考指引。

<!-- more -->

本文操作使用的虚拟机配置如下：

| 配置名称 | 配置内容                                         |
| :------- | ------------------------------------------------ |
| CPU      | Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz 1 Core |
| 内存     | 2 GB                                             |
| 系统版本 | CentOS Linux release 7.9.2009 (Core)             |
| 内核版本 | 3.10.0-1160.71.1.el7.x86_64                      |

# 0x01 测试工具简介

根据 Elkeid 项目 Issues 中的 [Driver 性能测试报告 #145](https://github.com/bytedance/Elkeid/issues/145)，得知 Driver 组件的性能测试结果是由 [LTP](https://linux-test-project.github.io/) 与 [trace-cmd](https://www.trace-cmd.org/) 两种工具配合完成的，因此本章将分别介绍两种工具的安装过程与相关用法。

## LTP

LTP（Linux Test Project）是由 SGI 公司发起，并由 IBM、Cisco、Fujitsu、SUSE、Red Hat 等公司开发维护的联合项目，旨在向开源社区提供测试套件，以验证 Linux 内核及其相关功能的可靠性与稳定性。

根据[项目说明文档](https://github.com/linux-test-project/ltp)，先从 Github 仓库下载当前最新版本的 LTP 20230127 测试套件：

```bash
$ git clone https://github.com/linux-test-project/ltp.git
$ ll ./ltp/
```

![git-clone-ltp](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/git-clone-ltp.png)

尝试直接配置自动编译工具，若提示相关依赖库缺失，则需参考 INSTALL 文档，通过执行 `./ci/centos.sh` 脚本补充安装相关依赖库：

```bash
$ cd ./ltp/
$ ./ci/centos.sh
```

![yum-install-centos-ltp-libs](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/yum-install-centos-ltp-libs.png)

安装依赖库后，继续配置自动编译工具：

```bash
$ make autotools
$ ./configure
```

![make-autotools-and-configure](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/make-autotools-and-configure.png)

LTP 支持「单测试用例快速编译」与「全测试用例编译安装」。为了便于后续操作，下面将编译安装所有测试用例：

```bash
$ make
$ make install
```

![make-all-testcases](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/make-all-testcases.png)

![make-install-all-testcases](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/make-install-all-testcases.png)

由于测试用例较多，需要等待一段时间。安装完毕后，在 /opt/ltp/ 目录下可见完整版的 LTP 测试套件，并通过执行 `./runltp -h` 命令查看相关用法：

```bash
$ cd /opt/ltp/
$ ll
$ ./runltp -h
```

![runltp-help](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/runltp-help.png)

## trace-cmd

trace-cmd 是一个 Linux 系统内核跟踪调试工具，它允许用户对内核函数进行动态跟踪分析，以便发现系统中的活动及其性能问题，

参考[项目说明文档](https://github.com/rostedt/trace-cmd)，可通过 yum 源自动下载安装 trace-cmd 工具：

![yum-install-trace-cmd](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/yum-install-trace-cmd.png)

安装后直接执行 `trace-cmd` 命令，可查看当前 v2.7 版本对应的相关用法：

![trace-cmd-help](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/trace-cmd-help.png)

# 0x02 测试操作流程

准备工作完成后，测试操作流程正式开始：

首先，下载 Elkeid 项目，并编译装载其 Driver 组件；接下来，执行指定系统调用函数的相关 LTP 测试用例，并同时使用 trace-cmd 工具，对 Driver 组件中编写的内核函数进行跟踪分析；最后，等待 trace-cmd 跟踪任务结束后得到分析结果，即可停止 LTP 测试用例。

## 装载 Elkeid Driver

从 Github 仓库下载当前最新版本的 Elkeid 项目，并编译得到其 Driver 组件的内核模块文件 hids_driver.ko，使用 `modinfo` 命令查看内核模块信息，使用 `insmod` 命令装载内核模块，使用 `lsmod` 命令查看系统已装载的内核模块：

```bash
$ git clone https://github.com/bytedance/Elkeid.git
$ cd ./Elkeid/driver/LKM/
$ make
$ modinfo ./hids_driver.ko
$ insmod ./hids_driver.ko
$ lsmod | grep hids_driver
```

![make-elkeid-driver](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/make-elkeid-driver.png)

![modinfo-insmod-elkeid-driver](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/modinfo-insmod-elkeid-driver.png)

## 执行 LTP 测试用例

在 Driver 组件介绍文档中得知，针对 `connect`、`bind`、`execve`、`security_inode_create`、`ptrace` 等五个系统调用函数，执行了相关测试用例：

![elkeid-driver-testing-load](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/elkeid-driver-testing-load.png)

下面将选取 connect 系统调用函数的测试用例作为演示，并持续执行 5 分钟：

```bash
$ /opt/ltp/runltp -f syscalls -s connect -t 5m
```

![runltp-syscalls-connect](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/runltp-syscalls-connect.png)

`runltp` 命令的相关参数含义如下：

- `-f CMDFILES`：Execute user defined list of testcases (separate with ',')
- `-s PATTERN`：Only run test cases which match PATTERN.
- `-t DURATION` ：Execute the testsuite for given duration.

通过 `-f syscalls` 指定与系统调用函数相关的测试集，备选测试集位于 /opt/ltp/runtest 路径下；而通过 `-s connect` 指定测试集中命名格式与 connect 字符串相匹配的测试用例：

```bash
$ ls /opt/ltp/runtest
$ cat /opt/ltp/runtest/syscalls | grep connect
```

![runltp-runtest](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/runltp-runtest.png)

## 使用 trace-cmd 跟踪分析

在以上 LTP 测试用例的执行过程中，同时在另一个终端使用 trace-cmd 工具，通过 `-p function_graph` 启用「函数调用图追踪器」，通过 `-l connect_syscall_entry_handler` 指定 Driver 组件中的内核函数，通过 `-o connect_syscall_entry_handler_data` 指定结果保存文件，持续进行 90 秒的跟踪分析：

```bash
$ trace-cmd record -p function_graph -l connect_syscall_entry_handler -o connect_syscall_entry_handler_data sleep 90
```

` trace-cmd record` 命令的相关参数含义如下：

- `-p`：run command with plugin enabled
- `-l`：filter function name
- `-o`：data output file [default trace.dat]

![trace-cmd-record](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/trace-cmd-record.png)

若读者不熟悉 trace-cmd 的追踪器类型，或不明确需跟踪的内核函数，则可以使用 `trace-cmd list` 命令查看：

```bash
$ trace-cmd list -t
$ trace-cmd list -f hids_driver | grep connect
```

` trace-cmd list` 命令的相关参数含义如下：

- `-t`：list available tracers
- `-f [regex] `：list available functions to filter on

![trace-cmd-list](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/trace-cmd-list.png)

跟踪任务结束后，通过 `-i connect_syscall_entry_handler_data` 指定需输出展示的结果文件，发现共有 57891 条记录：

```bash
$ trace-cmd report -i connect_syscall_entry_handler_data | wc -l
$ trace-cmd report -i connect_syscall_entry_handler_data | head
```

` trace-cmd report` 命令的相关参数含义如下：

- `-i`：input file [default trace.dat]

![trace-cmd-report](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/trace-cmd-report.png)

对照 Elkeid 项目中性能测试的原始数据，可见其文件格式与 trace-cmd 的测试结果保持一致，说明上述测试操作流程基本推导正确：

```bash
$ cd ./Elkeid/driver/benchmark_data/handler/
$ head connect_syscall_entry_handler_data
```

![elkeid-driver-benchmark-data](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/elkeid-driver-benchmark-data.png)

# 0x03 测试结果分析

测试操作流程结束后，需对 trace-cmd 的跟踪任务结果进行分析：

首先，解读 Elkeid Driver 组件的性能测试结果及相关指标；再依据此，编写通用自动化分析脚本，完成对上述测试结果的分析。

## 指标解读

针对 Driver 组件中编写的内核函数，均包含 Average Delay(us)、TP99(us)、TP95(us)、TP90(us) 等四个指标，用于说明每个内核函数执行的耗时开销：

- `Average Delay`：针对某个内核函数，其所有执行操作的平均耗时。
- `TP99`：针对某个内核函数，其中 99% 的执行操作耗时不超过 TP99，即在 99% 概率下的耗时上限。TP95 与 TP90 同理。

![elkeid-driver-testing-result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/elkeid-driver-testing-result.png)

从上图性能测试结果分析可知：

- connect_syscall_entry_handler 函数执行的 Average Delay 为 0.0675 微秒，TP99 为 0.3 微秒，说明此函数有 99% 的执行操作耗时不超过 0.3 微秒。
- 其余大部分函数执行的 Average Delay 在 10 微秒内，最大不超过 20 微秒；而大部分 TP99 在 20 微秒内，最大不超过 100 微秒。

## 自动化分析

为了从 trace-cmd 测试结果中快速获取上述指标，编写了以下 Python3 自动化分析脚本：

```python
import sys, re

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auto_statistics.py [filename]")
        sys.exit(1)
    filename = sys.argv[1]
    usList = getUsList(filename)
    print('Total Counts: %d' % len(usList))
    print('Average Delay: %.4fus' % getAvg(usList))
    print('TP99: %.4fus' % getTP(usList, 0.99)[1])
    print('TP95: %.4fus' % getTP(usList, 0.95)[1])
    print('TP90: %.4fus' % getTP(usList, 0.90)[1])

def getUsList(filename):
    usList = []
    pattern = r"([\d\.]+) us"
    with open(filename, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                usList.append(float(match.group(1)))
    usList.sort()
    return usList

def getAvg(list):
    avg = 0
    for index, us in enumerate(list):
        avg = avg * (index/(index+1)) + us * (1/(index+1))
    return avg

def getTP(list, ratio):
    index = int(ratio * len(list)) - 1
    return index, list[index]

if __name__ == '__main__':
    main()
```

将此脚本保存至 auto_statistics.py 文件中，并对本文的 connect_syscall_entry_handler_data 测试结果进行分析，得到 Average Delay 为 0.0737 微秒，TP99 为 0.2920 微秒，TP95 为 0.1730 微秒，TP90 为 0.1270 微秒，可见与官方分析结果基本一致：

```bash
$ trace-cmd report -i connect_syscall_entry_handler_data > connect_syscall_entry_handler_data.txt
$ python3 auto_statistics.py connect_syscall_entry_handler_data.txt
```

![auto-statistics-connect-data](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/operational-guide-of-elkeid-driver-performance-test/auto-statistics-connect-data.png)

# 0x04 总结

本文针对 Elkeid Driver 组件的性能测试，从测试工具、测试操作流程、测试结果分析等方面进行了详细介绍，为 Driver 组件的开发者提供了操作指引，甚至对 Linux 内核模块的开发测试也具有一定参考意义。

感谢各位阅读，若发现有错误之处恳请指出，也欢迎读者提出与文章结构或内容描述相关的修订意见，以助于改进。

## 参考资料

[1] [LTP 第一章 LTP 介绍及内部机制](https://jitwxs.cn/51dc9e04) 

[2] [使用 trace-cmd 追踪内核](https://linux.cn/article-13852-1.html)

[3] [ftrace和trace-cmd：跟踪内核函数的利器](https://blog.csdn.net/weixin_44410537/article/details/103587609)

[4] [What do we mean by "top percentile" or TP based latency?](https://stackoverflow.com/questions/17435438/what-do-we-mean-by-top-percentile-or-tp-based-latency)