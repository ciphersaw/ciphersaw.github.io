---
title: Python 绝技 —— UDP 服务器与客户端
copyright: true
date: 2018-06-15 09:38:58
tags: [python,network,udp,socket,tool,doc]
categories: [Programming,Python]
---

# 0x00 前言

在上一篇文章[「Python 绝技 —— TCP 服务器与客户端」](https://ciphersaw.github.io/2018/05/23/Python%20%E7%BB%9D%E6%8A%80%20%E2%80%94%E2%80%94%20TCP%20%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%E5%AE%A2%E6%88%B7%E7%AB%AF/)中，介绍了传输层的核心协议 TCP ，并运用 Python 脚本的 socket 模块演示了 TCP 服务器与客户端的通信过程。

本篇将按照同样的套路，先介绍传输层的另一个**核心协议 UDP**，再比较 TCP 与 UDP 的特点，最后借助 Python 脚本演示 **UDP 服务器与客户端**的通信过程。

<!-- more -->

# 0x01 UDP 协议

[UDP（User Datagram Protocol，用户数据报协议）](https://en.wikipedia.org/wiki/User_Datagram_Protocol)是一种无连接、不可靠、基于数据报的传输层通信协议。

- UDP 的通信过程与 TCP 相比较为简单，不需要复杂的三次握手与四次挥手，体现了**无连接**；
- UDP 传输速度比 TCP 快，但容易丢包、数据到达顺序无保证、缺乏拥塞控制、秉承尽最大努力交付的原则，体现了**不可靠**；
- UDP 的无连接与不可靠特性注定无法采用字节流的通信模式，由协议名中的「Datagram」与 socket 类型中的「SOCK_DGRAM」即可体现它**基于数据报**的通信模式。

为了更直观地比较 TCP 与 UDP 的异同，笔者将其整理成以下表格：

|                  |           TCP           |          UDP          |
| :--------------: | :---------------------: | :-------------------: |
|     连接模式     |  面向连接（单点通信）   |  无连接（多点通信）   |
|    传输可靠性    |          可靠           |        不可靠         |
|     通信模式     |       基于字节流        |      基于数据报       |
|     报头结构     |   复杂（至少20字节）    |     简单（8字节）     |
|     传输速度     |           慢            |          快           |
|     资源需求     |           多            |          少           |
|     到达顺序     |          保证           |        不保证         |
|     流量控制     |           有            |          无           |
|     拥塞控制     |           有            |          无           |
|     应用场合     |      大量数据传输       |     少量数据传输      |
| 支持的应用层协议 | Telnet、FTP、SMTP、HTTP | DNS、DHCP、TFTP、SNMP |

# 0x02 Network Socket

[**Network Socket（网络套接字）**](https://en.wikipedia.org/wiki/Network_socket)是计算机网络中进程间通信的数据流端点，广义上也代表操作系统提供的一种进程间通信机制。

[**进程间通信（Inter-Process Communication，IPC）**](https://en.wikipedia.org/wiki/Inter-process_communication)的根本前提是**能够唯一标示每个进程**。在本地主机的进程间通信中，可以用 **[PID（进程 ID）](https://en.wikipedia.org/wiki/Process_identifier)**唯一标示每个进程，但 PID 只在本地唯一，在网络中不同主机的 PID 则可能发生冲突，因此采用**「IP 地址 + 传输层协议 + 端口号」**的方式唯一标示网络中的一个进程。

> 小贴士：网络层的 IP 地址可以唯一标示主机，传输层的 TCP/UDP 协议和端口号可以唯一标示该主机的一个进程。注意，同一主机中 TCP 协议与 UDP 协议的可以使用相同的端口号。

所有支持网络通信的编程语言都各自提供了一套 socket API，下面以 Python 3 为例，讲解服务器与客户端建立 UDP 通信连接的交互过程：

![udp_socket_python](http://oyhh4m1mt.bkt.clouddn.com/Python_%E7%BB%9D%E6%8A%80_UDP_%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%E5%AE%A2%E6%88%B7%E7%AB%AF/udp_socket_python.png)

可见，UDP 的通信过程比 TCP 简单许多，服务器少了监听与接受连接的过程，而客户端也少了请求连接的过程。客户端只需要知道服务器的地址，直接向其发送数据即可，而服务器也敞开大门，接收任何发往自家地址的数据。

> 小贴士：由于 UDP 采用无连接模式，可知 UDP 服务器在接收到客户端发来的数据之前，是不知道客户端的地址的，因此**必须是客户端先发送数据，服务器后响应数据**。而 TCP 则不同，TCP 服务器接受了客户端的连接后，既可以先向客户端发送数据，也可以等待客户端发送数据后再响应。

# 0x03 UDP 服务器

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 6000))
print("UDP bound on port 6000...")

while True:
	data, addr = s.recvfrom(1024)
	print("Receive from %s:%s" % addr)
	if data == b"exit":
		s.sendto(b"Good bye!\n", addr)
		continue
	s.sendto(b"Hello %s!\n" % data, addr)
```

- Line 5：创建 socket 对象，第一个参数为 *socket.AF_INET*，代表采用 IPv4 协议用于网络通信，第二个参数为 *socket.SOCK_DGRAM*，代表采用 UDP 协议用于无连接的网络通信。
- Line 6：向 socket 对象绑定服务器主机地址 ("127.0.0.1", 6000)，即本地主机的 UDP 6000 端口。
- Line 9：进入与客户端交互数据的循环阶段。
- Line 10：接收客户端发来的数据，包括 bytes 对象 data，以及客户端的 IP 地址和端口号 addr，其中 addr 为二元组 (host, port)。
- Line 11：打印接收信息，表示从地址为 addr 的客户端接收到数据。
- Line 12：若 bytes 对象为 `b"exit"`，则向地址为 addr 的客户端发送结束响应信息 `b"Good bye!\n"`。发送完毕后，继续等待其他 UDP 客户端发来数据。
- Line 15：若 bytes 对象不为 `b"exit"`，则向地址为 addr 的客户端发送问候响应信息 `b"Hello %s!\n"`，其中 `%s` 是客户端发来的 bytes 对象。发送完毕后，继续等待任意 UDP 客户端发来数据。

与 TCP 服务器相比，UDP 服务器不必使用多线程，因为它**无需为每个通信过程创建独立连接，而是采用「即收即发」的模式**，又一次体现了 UDP 的无连接特性。

# 0x04 UDP 客户端

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("127.0.0.1", 6000)

while True:
	data = input("Please input your name: ")
	if not data:
		continue
	s.sendto(data.encode(), addr)
	response, addr = s.recvfrom(1024)
	print(response.decode())
	if data == "exit":
		print("Session is over from the server %s:%s\n" % addr)
		break

s.close()
```

- Line 5：创建 socket 对象，第一个参数为 *socket.AF_INET*，代表采用 IPv4 协议用于网络通信，第二个参数为 *socket.SOCK_DGRAM*，代表采用 UDP 协议用于无连接的网络通信。
- Line 6：初始化 UDP 服务器的地址 ("127.0.0.1", 6000)，即本地主机的 UDP 6000 端口。
- Line 8：进入与服务器交互数据的循环阶段。
- Line 9：要求用户输入名字。
- Line 10：当用户的输入为空时，则重新开始循环，要求用户重新输入。
- Line 12：当用户的输入非空时，则将字符串转换为 bytes 对象后，发送至地址为 ("127.0.0.1", 6000) 的 UDP 服务器。
- Line 13：接收服务器的响应数据，包括 bytes 对象 response，以及服务器的 IP 地址和端口号 addr，其中 addr 为二元组 (host, port)。
- Line 14：将响应的 bytes 对象 response 转换为字符串后打印输出。
- Line 15：当用户的输入为 `"exit"` 时，则打印会话结束信息，终止与服务器交互数据的循环阶段，即将关闭套接字。
- Line 19：关闭套接字，不再向服务器发送数据。

# 0x05 UDP 进程间通信

将 UDP 服务器与客户端的脚本分别命名为 `udp_server.py` 与 `udp_client.py`，然后存至桌面，笔者将在 Windows 10 系统下用 PowerShell 进行演示。

> 小贴士：读者进行复现时，要确保本机已安装 Python 3，注意笔者已将默认的启动路径名 `python` 改为了 `python3`。

## 单服务器 VS 多客户端

![one_server_vs_multiple_clients](http://oyhh4m1mt.bkt.clouddn.com/Python_%E7%BB%9D%E6%8A%80_UDP_%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8E%E5%AE%A2%E6%88%B7%E7%AB%AF/one_server_vs_multiple_clients.png)

1. 在其中一个 PowerShell 中运行命令 `python3 ./udp_server.py`，服务器绑定本地主机的 UDP 6000 端口，并打印信息 `UDP bound on port 6000...`，等待客户端发来数据；
2. 在另两个 PowerShell 中分别运行命令 `python3 ./udp_client.py`，并向服务器发送字符串 `Client1`、`Client2`；
3. 服务器打印接收信息，表示分别从 UDP 63643、63644端口接收到数据，并分别向客户端发送问候响应信息；
4. 客户端 `Client1` 发送空字符串，则被要求重新输入；
5. 客户端 `Client2` 先发送字符串 `Alice`，得到服务器的问候响应信息，再发送字符串 `exit`，得到服务器的结束响应信息，最后打印会话结束信息，终止与服务器的数据交互；
6. 客户端 `Client1` 发送字符串 `exit`，得到服务器的结束响应信息，并打印会话结束信息，终止与服务器的数据交互；
7. 服务器按照以上客户端的数据发送顺序打印接收信息，并继续等待任意 UDP 客户端发来数据。

# 0x06 Python API Reference

## socket 模块

本节介绍上述代码中用到的[内建模块 socket](https://docs.python.org/3/library/socket.html)，是 Python 网络编程的核心模块。

### socket() 函数

[socket() 函数](https://docs.python.org/3/library/socket.html#socket.socket)用于创建网络通信中的套接字对象。函数原型如下：

```python
socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)
```

- *family* 参数代表[地址族（Address Family）](https://docs.python.org/3/library/socket.html#socket-families)，默认值为 *AF_INET*，用于 IPv4 网络通信，常用的还有 *AF_INET6*，用于 IPv6 网络通信。*family* 参数的可选值取决于本机操作系统。
- *type* 参数代表套接字的类型，默认值为 *SOCK_STREAM*，用于 TCP 协议（面向连接）的网络通信，常用的还有 *SOCK_DGRAM*，用于 UDP 协议（无连接）的网络通信。
- *proto* 参数代表套接字的协议，默认值为 *0*，一般忽略该参数，除非 *family* 参数为 *AF_CAN*，则 *proto* 参数需设置为 *CAN_RAW* 或 *CAN_BCM*。
- *fileno* 参数代表套接字的文件描述符，默认值为 *None*，若设置了该参数，则其他三个参数将会被忽略。

创建完套接字对象后，需使用对象的内置函数完成网络通信过程。**注意，以下函数原型中的「socket」是指 socket 对象，而不是上述的 socket 模块。**

### bind() 函数

[bind() 函数](https://docs.python.org/3/library/socket.html#socket.socket.bind)用于向套接字对象绑定 IP 地址与端口号。注意，套接字对象必须未被绑定，并且端口号未被占用，否则会报错。函数原型如下：

```python
socket.bind(address)
```

- *address* 参数代表套接字要绑定的地址，其格式取决于套接字的 *family* 参数。若 *family* 参数为 *AF_INET*，则 *address* 参数表示为二元组 (host, port)，其中 host 是用字符串表示的主机地址，port 是用整型表示的端口号。

### sendto() 函数

[sendto() 函数](https://docs.python.org/3/library/socket.html#socket.socket.sendto)用于向远程套接字对象发送数据。注意，该函数用于 UDP 进程间的无连接通信，远程套接字的地址在参数中指定，因此使用前不需要先与远程套接字连接。相对地，TCP 进程间面向连接的通信过程需要用 send() 函数。函数原型如下：

```python
socket.sendto(bytes[, flags], address)
```

- *bytes* 参数代表即将发送的 [bytes 对象](https://docs.python.org/3/library/stdtypes.html#bytes-objects)数据。例如，对于字符串 `"hello world!"` 而言，需要用 encode() 函数转换为 bytes 对象 `b"hello world!"` 才能进行网络传输。
- *flags* 可选参数用于设置 sendto() 函数的特殊功能，默认值为 *0*，也可由一个或多个预定义值组成，用位或操作符 `|` 隔开。详情可参考 Unix 函数手册中的 [sendto(2)](https://linux.die.net/man/2/sendto)，*flags* 参数的常见取值有 MSG_OOB、MSG_EOR、MSG_DONTROUTE 等。
- *address* 参数代表远程套接字的地址，其格式取决于套接字的 *family* 参数。若 *family* 参数为 *AF_INET*，则 *address* 参数表示为二元组 (host, port)，其中 host 是用字符串表示的主机地址，port 是用整型表示的端口号。

sendto() 函数的返回值是发送数据的字节数。

### recvfrom() 函数

[recvfrom() 函数](https://docs.python.org/3/library/socket.html#socket.socket.recvfrom)用于从远程套接字对象接收数据。注意，与 sendto() 函数不同，recvfrom() 函数既可用于 UDP 进程间通信，也能用于 TCP 进程间通信。函数原型如下：

```python
socket.recvfrom(bufsize[, flags])
```

- *bufsize* 参数代表套接字可接收数据的最大字节数。注意，为了使硬件设备与网络传输更好地匹配，*bufsize* 参数的值最好设置为 2 的幂次方，例如 *4096*。
- *flags* 可选参数用于设置 recv() 函数的特殊功能，默认值为 *0*，也可由一个或多个预定义值组成，用位或操作符 `|` 隔开。详情可参考 Unix 函数手册中的 [recvfrom(2)](https://linux.die.net/man/2/recvfrom)，*flags* 参数的常见取值有 MSG_OOB、MSG_PEEK、MSG_WAITALL 等。

recvfrom() 函数的返回值是二元组 (bytes, address)，其中 bytes 是接收到的 bytes 对象数据，address 是发送方的 IP 地址与端口号，用二元组 (host, port) 表示。注意，recv() 函数的返回值只有 bytes 对象数据。

### close() 函数

[close() 函数](https://docs.python.org/3/library/socket.html#socket.socket.close)用于关闭本地套接字对象，释放与该套接字连接的所有资源。

```python
socket.close()
```

# 0x07 总结

本文介绍了 UDP 协议的基础知识，并与 TCP 协议进行对比，再用 Python 3 实现并演示了 UDP 服务器与客户端的通信过程，最后将脚本中涉及到的 Python API 做成了的参考索引，有助于读者理解实现过程。

感谢各位的阅读，笔者水平有限，若有不足或错误之处请谅解并告知，希望自己对 TCP 和 UDP 的浅薄理解，能帮助读者更好地理解传输层协议。

本文的相关参考请移步至：

> [TCP和UDP的最完整的区别](https://blog.csdn.net/Li_Ning_/article/details/52117463)
> [TCP和UDP之间的区别](http://blog.51cto.com/feinibuke/340272)
> [UDP编程 - 廖雪峰的官方网站](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432004977916a212e2168e21449981ad65cd16e71201000)