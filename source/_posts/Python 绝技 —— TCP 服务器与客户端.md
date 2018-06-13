---
title: Python 绝技 —— TCP 服务器与客户端
copyright: true
date: 2018-05-23 22:33:19
tags: [python,network,tcp,socket,tool,doc]
categories: [Programming,Python]
---

# 0x00 前言

「网络」一直以来都是黑客最热衷的竞技场。数据在网络中肆意传播：主机扫描、代码注入、网络嗅探、数据篡改重放、拒绝服务攻击......黑客的功底越深厚，能做的就越多。

Python 作为一种解释型脚本语言，自 1991 年问世以来，其简洁、明确、可读性强的语法深受黑客青睐，特别在网络工具的编写上，避免了繁琐的底层语法，没有对运行速度的高效要求，使得 Python 成为安全工作者的必备杀手锏。

本文作为「Python 绝技」系列工具文章的开篇，先介绍因特网的**核心协议 TCP** ，再以 Python 的 socket 模块为例介绍网络套接字，最后给出 **TCP 服务器与客户端**的 Python 脚本，并演示两者之间的通信过程。

<!-- more -->

# 0x01 TCP 协议

**[TCP（Transmission Control Protocol，传输控制协议）](https://en.wikipedia.org/wiki/Transmission_Control_Protocol)**是一种面向连接、可靠的、基于字节流的传输层通信协议。

TCP 协议的运行分为连接创建（Connection Establishment）、数据传送（Data Transfer）和连接终止（Connection Termination）三个阶段，其中「连接创建」阶段是耳熟能详的 [**TCP 协议三次握手（TCP Three-way Handshake）**](https://en.wikipedia.org/wiki/Handshaking#TCP_three-way_handshake)，也是理解本文 TCP 服务器与客户端通信过程的阶段。

## 连接创建（Connection Establishment）

所谓的「三次握手」，即 TCP 服务器与客户端成功建立通信连接必经的三个步骤，共需通过三个报文完成。

### Handshake Step 1

客户端向服务器发送 SYN 报文（$SYN = 1$）请求连接。此时报文的初始序列号为 $seq = x$，确认号为 $ack = 0$。

### Handshake Step 2

服务器接收到客户端的 SYN 报文后，发送 ACK + SYN 报文（$ACK = 1，SYN = 1$）确认客户端的连接请求，并也向其发起连接请求。此时报文的序列号为 $seq = y$，确认号为 $ack = x + 1$。

### Handshake Step 3

客户端接收到服务器的 SYN 报文后，发送 ACK 报文（$ACK = 1$）确认服务器的连接请求。此时报文的序列号为 $seq = x + 1$，确认号为 $ack = y + 1$。

对于上述过程的理解，需要注意以下几点：

- 报文的功能在 TCP 协议头的**标记符（Flags）**区段中定义，该区段位于第 104~111 比特位，共占 8 比特，每个比特位对应一种功能，置 1 代表开启，置 0 代表关闭。例如，SYN 报文的标记符为 `00000010`，ACK + SYN 报文的标记符为 `00010010`。
- 报文的序列号在 TCP 协议头的**序列号（Sequence Number）**区段中定义，该区段位于第 32~63 比特位，共占 32 比特。在「三次握手」过程中，初始序列号 $seq$ 由数据发送方随机生成。
- 报文的确认号在 TCP 协议头的**确认号（Acknowledgement Number）**区段中定义，该区段位于第 64~95 比特位，共占 32 比特。在「三次握手」过程中，确认号 $ack$ 为前序接收报文的序列号加 1。

为了更方便地理解，下面给出一张 TCP 协议三次握手的示意图：

![tcp_three_way_handshake](http://oyhh4m1mt.bkt.clouddn.com/Python_%E7%BB%9D%E6%8A%80_TCP_%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%E5%AE%A2%E6%88%B7%E7%AB%AF/tcp_three_way_handshake.png)

# 0x02 Network Socket

[**Network Socket（网络套接字）**](https://en.wikipedia.org/wiki/Network_socket)是计算机网络中进程间通信的数据流端点，广义上也代表操作系统提供的一种进程间通信机制。

[**进程间通信（Inter-Process Communication，IPC）**](https://en.wikipedia.org/wiki/Inter-process_communication)的根本前提是**能够唯一标示每个进程**。在本地主机的进程间通信中，可以用 **[PID（进程 ID）](https://en.wikipedia.org/wiki/Process_identifier)**唯一标示每个进程，但 PID 只在本地唯一，在网络中不同主机的 PID 则可能发生冲突，因此采用**「IP 地址 + 传输层协议 + 端口号」**的方式唯一标示网络中的一个进程。

> 小贴士：网络层的 IP 地址可以唯一标示主机，传输层的 TCP/UDP 协议和端口号可以唯一标示该主机的一个进程。注意，同一主机中 TCP 协议与 UDP 协议的可以使用相同的端口号。

所有支持网络通信的编程语言都各自提供了一套 socket API，下面以 Python 3 为例，讲解服务器与客户端建立 TCP 通信连接的交互过程：

![tcp_socket_python](http://oyhh4m1mt.bkt.clouddn.com/Python_%E7%BB%9D%E6%8A%80_TCP_%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%E5%AE%A2%E6%88%B7%E7%AB%AF/tcp_socket_python.png)

脑海中先对上述过程产生一定印象后，更易于理解下面两节 TCP 服务器与客户端的 Python 实现。

# 0x03 TCP 服务器

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import threading

def tcplink(conn, addr):
	print("Accept new connection from %s:%s" % addr)
	conn.send(b"Welcome!\n")
	while True:
		conn.send(b"What's your name?")
		data = conn.recv(1024).decode()
		if data == "exit":
			conn.send(b"Good bye!\n")
			break
		conn.send(b"Hello %s!\n" % data.encode())
	conn.close()
	print("Connection from %s:%s is closed" % addr)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 6000))
s.listen(5)
print("Waiting for connection...")

while True:
	conn, addr = s.accept()
	t = threading.Thread(target = tcplink, args = (conn, addr))
	t.start()
```

- Line 6：定义一个 tcplink() 函数，第一个 *conn* 参数为服务器与客户端交互数据的套接字对象，第二个 *addr* 参数为客户端的 IP 地址与端口号，用二元组 (host, port) 表示。
- Line 8：连接成功后，向客户端发送问候信息 `"Welcome!\n"`。
- Line 9：进入与客户端交互数据的循环阶段。
- Line 10：向客户端发送询问信息 `"What's your name?"`。
- Line 11：接收客户端发来的非空字符串。
- Line 12：如果非空字符串为 `"exit"`，则向客户端发送结束信息 `"Good bye!\n"`，并结束与客户端交互数据的循环阶段。
- Line 15：如果非空字符串不为 `"exit"`，则向客户端发送问候信息 `"Hello %s!\n"`，其中 `%s` 是客户端发来的非空字符串。
- Line 16：关闭套接字，不再向客户端发送数据。
- Line 19：创建 socket 对象，第一个参数为 *socket.AF_INET*，代表采用 IPv4 协议用于网络通信，第二个参数为 *socket.SOCK_STREAM*，代表采用 TCP 协议用于面向连接的网络通信。
- Line 20：向 socket 对象绑定服务器主机地址 ("127.0.0.1", 6000)，即本地主机的 TCP 6000 端口。
- Line 21：开启 socket 对象的监听功能，等待客户端的连接请求。
- Line 24：进入监听客户端连接请求的循环阶段。
- Line 25：接收客户端的连接请求，并获得与客户端交互数据的套接字对象 conn 与客户端的 IP 地址与端口号 addr，其中 addr 为二元组 (host, port)。
- Line 26：利用多线程技术，为每个请求连接的 TCP 客户端创建一个新线程，实现了一台服务器同时与多台客户端进行通信的功能。
- Line 27：开启新线程的活动。

# 0x04 TCP 客户端

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 6000))
print(s.recv(1024).decode())

data = "client"
while True:
	if data:
		print(s.recv(1024).decode())
	data = input("Please input your name: ")
	if not data:
		continue
	s.send(data.encode())
	print(s.recv(1024).decode())
	if data == "exit":
		break

s.close()
```

- Line 5：创建 socket 对象，第一个参数为 *socket.AF_INET*，代表采用 IPv4 协议用于网络通信，第二个参数为 *socket.SOCK_STREAM*，代表采用 TCP 协议用于面向连接的网络通信。
- Line 6：向 ("127.0.0.1", 6000) 主机发起连接请求，即本地主机的 TCP 6000 端口。
- Line 7：连接成功后，接收服务器发送过来的问候信息 `"Welcome!\n"`。
- Line 9：创建一个非空字符串变量 data，并赋初值为 `"client"`（只要是非空字符串即可），用于判断是否接收来自服务器发来的询问信息 `"What's your name?"`。
- Line 10：进入与服务器交互数据的循环阶段。
- Line 12：当用户的输入非空且不等于 `"exit"`（记为非法字符串）时，则接收服务器发来的询问信息。
- Line 13：要求用户输入名字，一条合法字符串即可。
- Line 14：当用户输入非空，则重新开始循环，要求用户重新输入合法字符串。
- Line 16：当用户输入合法字符串时，则将字符串转换为 bytes 对象后发送至服务器。
- Line 17：接收服务器的响应数据，并将 bytes 对象转换为字符串后打印输出。
- Line 18：当用户输入字符串 `"exit"` 时，则结束与服务器交互数据的循环阶段，即将关闭套接字。
- Line 21：关闭套接字，不再向服务器发送数据。

# 0x05 TCP 进程间通信

将 TCP 服务器与客户端的脚本分别命名为 `tcp_server.py` 与 `tcp_client.py`，然后存至桌面，笔者将在 Windows 10 系统下用 PowerShell 进行演示。

> 小贴士：读者进行复现时，要确保本机已安装 Python 3，注意笔者已将默认的启动路径名 `python` 改为了 `python3`。

## 单服务器 VS 单客户端

![one_server_vs_one_client](http://oyhh4m1mt.bkt.clouddn.com/Python_%E7%BB%9D%E6%8A%80_TCP_%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%E5%AE%A2%E6%88%B7%E7%AB%AF/one_server_vs_one_client.png)

1. 在其中一个 PowerShell 中运行命令 `python3 ./tcp_server.py`，服务器显示 `Waiting for connection...`，并监听本地主机的 TCP 6000 端口，进入等待连接状态；
2. 在另一个 PowerShell 中运行命令 `python3 ./tcp_client.py`，服务器显示 `Accept new connection from 127.0.0.1:42101`，完成与本地主机的 TCP 42101 端口建立通信连接，并向客户端发送问候信息与询问信息，客户端接收到信息后打印输出；
3. 若客户端向服务器发送字符串 `Alice` 与 `Bob`，则收到服务器的问候响应信息；
4. 若客户端向服务器发送空字符串，则要求重新输入字符串；
5. 若客户端向服务器发送字符串 `exit`，则收到服务器的结束响应信息；
6. 客户端与服务器之间的通信连接已关闭，服务器显示 `Connection from 127.0.0.1:42101 is closed`，并继续监听客户端的连接请求。

## 单服务器 VS 多客户端

![one_server_vs_multiple_clients](http://oyhh4m1mt.bkt.clouddn.com/Python_%E7%BB%9D%E6%8A%80_TCP_%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%E5%AE%A2%E6%88%B7%E7%AB%AF/one_server_vs_multiple_clients.png)

1. 在其中一个 PowerShell 中运行命令 `python3 ./tcp_server.py`，服务器显示 `Waiting for connection...`，并监听本地主机的 TCP 6000 端口，进入等待连接状态；
2. 在另三个 PowerShell 中分别运行命令 `python3 ./tcp_client.py`，服务器同时与本地主机的 TCP 42719、42721、42722 端口建立通信连接，并分别向客户端发送问候信息与询问信息，客户端接收到信息后打印输出；
3. 三台客户端分别向服务器发送字符串 `Client1`、`Client2`、`Client3`，并收到服务器的问候响应信息；
4. 所有客户端分别向服务器发送字符串 `exit`，并收到服务器的结束响应信息；
5. 所有客户端与服务器之间的通信连接已关闭，服务器继续监听客户端的连接请求。

# 0x06 Python API Reference

## socket 模块

此小节介绍上述代码中用到的 [socket 模块内置函数](https://docs.python.org/3/library/socket.html#functions)，也是 socket 编程的核心函数。

### socket() 函数

[socket() 函数](https://docs.python.org/3/library/socket.html#socket.socket)用于创建网络通信中的套接字对象。函数原型如下：

```python
socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)
```

- *family* 参数代表[地址族（Address Family）](https://docs.python.org/3/library/socket.html#socket-families)，默认值为 *AF_INET*，用于 IPv4 网络通信，常用的还有 *AF_INET6*，用于 IPv6 网络通信。*family* 参数的可选值取决于本机操作系统。
- *type* 参数代表套接字的类型，默认值为 *SOCK_STREAM*，用于 TCP 协议（面向连接）的网络通信，常用的还有 *SOCK_DGRAM*，用于 UDP 协议（无连接）的网络通信。
- *proto* 参数代表套接字的协议，默认值为 *0*，一般忽略该参数，除非 *family* 参数为 *AF_CAN*，则 *proto* 参数需设置为 *CAN_RAW* 或 *CAN_BCM*。
- *fileno* 参数代表套接字的文件描述符，默认值为 *None*，若设置了该参数，则其他三个参数将会被忽略。

## socket 对象

此小节介绍上述代码中用到的 [socket 对象内置函数](https://docs.python.org/3/library/socket.html#socket-objects)，也是 socket 编程的常见函数。注意，以下函数原型中的「socket」是指 socket 对象，而不是 socket 模块。

### bind() 函数

[bind() 函数](https://docs.python.org/3/library/socket.html#socket.socket.bind)用于向套接字对象绑定 IP 地址与端口号。注意，套接字对象必须未被绑定，并且端口号未被占用，否则会报错。函数原型如下：

```python
socket.bind(address)
```

- *address* 参数代表套接字要绑定的地址，其格式取决于套接字的 *family* 参数。若 *family* 参数为 *AF_INET*，则 *address* 参数表示为二元组 (host, port)，其中 host 是用字符串表示的主机地址，port 是用整型表示的端口号。

### listen() 函数

[listen() 函数](https://docs.python.org/3/library/socket.html#socket.socket.listen)用于 TCP 服务器开启套接字的监听功能。函数原型如下：

```python
socket.listen([backlog])
```

- *backlog* 可选参数代表套接字在拒绝新连接之前，操作系统可以挂起的最大连接数。*backlog* 参数一般设置为 *5*，若未设置，系统会为其自动设置一个合理的值。

### connect() 函数

[connect() 函数](https://docs.python.org/3/library/socket.html#socket.socket.connect)用于 TCP 客户端向 TCP 服务器发起连接请求。函数原型如下：

```python
socket.connect(address)
```

- *address* 参数代表套接字要连接的地址，其格式取决于套接字的 *family* 参数。若 *family* 参数为 *AF_INET*，则 *address* 参数表示为二元组 (host, port)，其中 host 是用字符串表示的主机地址，port 是用整型表示的端口号。

### accept() 函数

[accept() 函数](https://docs.python.org/3/library/socket.html#socket.socket.accept)用于 TCP 服务器接受 TCP 客户端的连接请求。函数原型如下：

```python
socket.accept()
```

accept() 函数的返回值是一个二元组 (conn, address)，其中 conn 是服务器用来与客户端交互数据的套接字对象，address 是客户端的 IP 地址与端口号，用二元组 (host, port) 表示。

### send() 函数

[send() 函数](https://docs.python.org/3/library/socket.html#socket.socket.send)用于向远程套接字对象发送数据。注意，本机的套接字必须与远程的套接字成功连接后才能使用该函数，否则会报错。可见，send() 函数只能用于 TCP 进程间通信，而对于 UDP 进程间通信应该用 sendto() 函数。函数原型如下：

```python
socket.send(bytes[, flags])
```

- *bytes* 参数代表即将发送的 [bytes 对象](https://docs.python.org/3/library/stdtypes.html#bytes-objects)数据。例如，对于字符串 `"hello world!"` 而言，需要用 encode() 函数转换为 bytes 对象 `b"hello world!"` 才能进行网络传输。
- *flags* 可选参数用于设置 send() 函数的特殊功能，默认值为 *0*，也可由一个或多个预定义值组成，用位或操作符 `|` 隔开。详情可参考 Unix 函数手册中的 [send(2)](https://linux.die.net/man/2/send)，*flags* 参数的常见取值有 MSG_OOB、MSG_PEEK、MSG_WAITALL 等。

send() 函数的返回值是发送数据的字节数。

### recv() 函数

[recv() 函数](https://docs.python.org/3/library/socket.html#socket.socket.recv)用于从远程套接字对象接收数据。注意，与 send() 函数不同，recv() 函数既可用于 TCP 进程间通信，也能用于 UDP 进程间通信。函数原型如下：

```python
socket.recv(bufsize[, flags])
```

- *bufsize* 参数代表套接字可接收数据的最大字节数。注意，为了使硬件设备与网络传输更好地匹配，*bufsize* 参数的值最好设置为 2 的幂次方，例如 *4096*。
- *flags* 可选参数用于设置 recv() 函数的特殊功能，默认值为 *0*，也可由一个或多个预定义值组成，用位或操作符 `|` 隔开。详情可参考 Unix 函数手册中的 [recv(2)](https://linux.die.net/man/2/recv)，*flags* 参数的常见取值有 MSG_OOB、MSG_PEEK、MSG_WAITALL 等。

recv() 函数的返回值是接收到的 bytes 对象数据。例如，接收到 bytes 对象 `b"hello world!"`，最好用 decode() 函数转换为字符串 `"hello world!"` 再打印输出。

### close() 函数

[close() 函数](https://docs.python.org/3/library/socket.html#socket.socket.close)用于关闭本地套接字对象，释放与该套接字连接的所有资源。

```python
socket.close()
```

## threading 模块

此小节介绍上述代码中用到的 threading 模块内置类，也是 Python 多线程编程的核心。

### Thread() 类

[Thread() 类](https://docs.python.org/3/library/threading.html#threading.Thread)可以创建线程对象，用于调用 start() 函数启动新线程。类原型如下：

```python
class threading.Thread(group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None)
```

- *group* 参数作为以后实现 ThreadGroup() 类的保留参数，目前默认值为 *None*。
- *target* 参数代表线程被 run() 函数激活后调用的函数，默认值为 *None*，即没有任何函数会被调用。
- name 参数代表线程名，默认值为 *None*，则系统会自动为其命名，格式为「Thread-*N*」，*N* 是从 *1* 开始的十进制数。
- *args* 参数代表 *target* 参数指向函数的普通参数，用元组（tuple）表示，默认值为空元组 `()`。
- *kwargs* 参数代表 *target* 参数指向函数的关键字参数，用字典（dict）表示，默认值为空字典 `{}`。
- *daemon* 参数用于标示进程是否为守护进程。若设置为 *True*，则标示为守护进程；若设置为 *False*，则标示为非守护进程；若设置为 *None*，则继承当前父线程的 *daemon* 参数值。

## threading 对象

此小节介绍上述代码中用到的 threading 对象内置函数，也是多线程编程的必用函数。注意，以下函数原型中的「threading」是指 threading 对象，而不是 threading 模块。

### start() 函数

[start() 函数](https://docs.python.org/3/library/threading.html#threading.Thread.start)用于开启线程活动。函数原型如下：

```python
threading.start()
```

注意，每个线程对象只能调用一次 start() 函数，否则会导致 [RuntimeError](https://docs.python.org/3/library/exceptions.html#RuntimeError) 错误。

# 0x07 总结

本文介绍了 TCP 协议与 socket 编程的基础知识，再用 Python 3 实现并演示了 TCP 服务器与客户端的通信过程，其中还运用了简单的多线程技术，最后将脚本中涉及到的 Python API 做成了的参考索引，有助于理解实现过程。

笔者水平有限，若文中出现不足或错误之处，还望大家不吝相告，多多包涵，欢迎读者前来交流技术，感谢阅读。

本文的相关参考请移步至：

> [简单理解Socket](http://www.cnblogs.com/dolphinX/p/3460545.html)
> [TCP编程 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432004374523e495f640612f4b08975398796939ec3c000)
> [多线程 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/00143192823818768cd506abbc94eb5916192364506fa5d000)