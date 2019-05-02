---
title: Microsoft Word 2013 公式自动编号与交叉引用
date: 2019-01-30 19:00:53
tags: [Microsoft,Word,MathType]
categories: [Tips,Microsoft Word]
copyright: true
mathjax: true
---

# 0x00 前言

在科技论文写作中，必不可少要使用到数学公式，虽然编辑公式简单，但要**将一系列公式自动编号，并且在文中交叉引用**，成为了科研工作者亟需解决的我问题。本文将采用 **Microsoft Word 2013 + MathType**，向大家介绍一种一劳永逸的解决方案，在其他版本的 Microsoft Word 中也基本适用。

<!-- more -->

# 0x01 准备工作

## 安装 MathType

[MathType](http://www.mathtype.cn/) 是一款专业的数学公式编辑工具，能与 Microsoft Word 完美结合，加上显示效果不俗，因此成为了广大理科男在 Word 上编辑公式的首选。此外，MathType 是共享软件，有 30 天的试用期，有需要的用户可以购买完整版，不过基本版的功能已满足大部分用户的需求了。

安装完成后，新建并打开一个 Word 文档 `新建 Microsoft Word 文档.docx`，正常情况下顶部菜单栏会增加一个 **MathType** 选项，说明已安装成功。

![mathtype_installation](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/mathtype_installation.png)

## 插入公式

点击 **MathType -> 内联**，在公式编辑框内输入一个勾股定理表达式 $a^2 + b^2 = c^2$，按下 **Ctrl + S** 保存后关闭编辑框，表达式已在文档中显示。

![formula_edit](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/formula_edit.png)

## 显示编辑标记

点击 **开始 -> 显示/隐藏编辑标记**，可显示制表符、分页符、空格等标记，有助于对后续操作的直观理解。

![show_mark](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/show_mark.png)

# 0x02 插入题注

## 无章节序号

点击 **引用 -> 插入题注 -> 新建标签**，在框内输入左小括号 `（`：

![new_mark_normal](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/new_mark_normal.png)

点击确定后，在 **题注** 内显示 `（ 1`，在 **标签** 内显示 `（`：

![display_mark_normal](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/display_mark_normal.png)

点击确定后，发现 `（` 与 `1` 之间有个小点，此为空格标记（该空格默认自带，无法再编辑题注中删除）。将此空格删除后，并在末尾补充上右小括号 `）`：

![modify_mark_normal](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/modify_mark_normal.png)

## 有章节序号

点击 **引用 -> 插入题注 -> 新建标签**，若想在第一章插入题注，则在框内输入左小括号 `（1-`：

![new_mark_chapter](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/new_mark_chapter.png)

点击确定后，在 **题注** 内显示 `（1- 1`，在 **标签** 内显示 `（1-`：

![display_mark_chapter](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/display_mark_chapter.png)

同样地，点击确定后，将 `（1-` 与 `1` 之间的空格删除，并在末尾补充上右小括号 `）`：

![modify_mark_chapter](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/modify_mark_chapter.png)

以上根据有无章节序号，介绍了两种插入题注的风格，读者可按需选用。

# 0x03 创建段落样式

## 新建样式

点击 **开始 -> 样式** 中右下角的小箭头，在弹出框的左下角点击 **新建样式**，将新样式编辑框中的 **属性 -> 名称** 改为 `公式`，并点击左下角的 **格式 -> 制表位**：

![initiate_pattern](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/initiate_pattern.png)

在 **制表位位置** 输入 `20 字符`，将 **对齐方式** 选为 `居中` 后点击确定：

![tab_middle](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/tab_middle.png)

再次点击左下角的 **格式 -> 制表位**，在 **制表位位置** 输入 `40 字符`，将 **对齐方式** 选为 `右对齐` 后点击确定：

![tab_right](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/tab_right.png)

建议将样式编辑框中的 **格式 -> 中文** 设置为 `宋体`，将 **格式 -> 西文** 设置为 `Times New Roman`，最后点击确定，在 **开始 -> 样式** 中出现了刚添加的样式：

![complete_pattern](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/complete_pattern.png)

## 使用样式

以无章节序号的公式编号为例，将光标放至公式所在行的任意位置，点击 **开始 -> 样式** 中的 `公式` 后，分别在公式前面、公式与编号之间按下 **Tab** 键（向右的小箭头即为 Tab 标记），出现了公式居中、编号右对齐的效果：

![format_with_pattern](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/format_with_pattern.png)

此外，为了在交叉引用时，只引用编号而不引用公式，需要在公式与编号之间添加一个[样式分隔符](https://answers.microsoft.com/en-us/office/forum/office_2010-word/ctrlaltenter-function-in-word-2010/3d3f2583-f56a-4aaf-8e38-267c5723eedc)。在公式下方另起一空行，按下 **Ctrl + Alt + Enter**，发现在原来的 Enter 标记前，多了一个被虚线框起的 Enter 标记：

![initiate_style_separator](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/initiate_style_separator.png)

被虚线框起的 Enter 标记即为样式分隔符，将其复制到公式与编号之间，最终效果如下：

![insert_style_separator](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/insert_style_separator.png)

# 0x04 保存至自动图文集

完成上述步骤后，已达到基本使用要求，但为了后续的方便使用，最好将公式编号的模板保存至自动图文集中。

点击 **文件 -> 选项 -> 快速访问工具栏**，在 **选择命令** 下拉框内选择 `所有命令`，将 `自动图文集` 添加至快速访问工具栏：

![add_quick_access](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/add_quick_access.png)

添加完成后点击确定，在顶部工具栏出现了自动图文集的图标。接着全选公式所在行，再点击 **自动图文集 -> 将所选内容保存到自动图文集库**：

![save_normal_pattern](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/save_normal_pattern.png)

此处将**新建构建基块**的名称设置为 `公式编号_交叉引用_普通版`，点击确定后即可完成：

![name_normal_pattern](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/name_normal_pattern.png)

将公式编号由无章节序号更改为有章节序号后，同样全选公式所在行，再点击 **自动图文集 -> 将所选内容保存到自动图文集库**：

![save_chapter_pattern](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/save_chapter_pattern.png)

处将**新建构建基块**的名称设置为 `公式编号_交叉引用_章节版`，点击确定后即可完成：

![name_chapter_pattern](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/name_chapter_pattern.png)

将以上两种公式编号的模板保存至自动图文集后，即可在 **自动图文集** 中选择所需模板，最后记得要替换模板内的默认公式。

# 0x05 交叉引用

>  小贴士：[交叉引用](https://en.wikipedia.org/wiki/Cross-reference)是指在 Microsoft Word 文档中引用其他位置的内容，例如编号项、标题、脚注、尾注、题注、书签、表格、公式等，引用的内容可随着被引用主体的改变而改变。

继续以无章节序号的公式编号为例，演示如何在文中交叉引用公式编号：

![inserting_cross_reference](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/inserting_cross_reference.png)

若想在光标出插入公式（1）的引用，需要点击 **插入 -> 交叉引用**，在 **引用类型** 下拉框内选择 `（`，在 **引用内容** 下拉框内选择 `整项题注`，在 **引用哪一个题注** 中选择 `（1）`：

![select_reference](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/select_reference.png)

点击确定后，发现文中确实多了对公式（1）的引用：

![inserted_cross_reference](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/inserted_cross_reference.png)

接下来讨论一种常见情况，假设在公式（1）前面新插入一个圆面积计算公式 $S  = π r^2$，这时会出现两个公式（1）：

![insert_new_formula](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/insert_new_formula.png)

此时只需要按下 **Ctrl + A** 选择全文，再按下 **F9** [更新域](https://support.office.com/en-us/article/update-fields-7339a049-cb0d-4d5a-8679-97c20c643d4e)，原来的公式（1）则变为公式（2），完美诠释了「引用的内容可随着被引用主体的改变而改变」这一大优势：

![update_cross_reference](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/Microsoft_Word_2013_%E5%85%AC%E5%BC%8F%E8%87%AA%E5%8A%A8%E7%BC%96%E5%8F%B7%E4%B8%8E%E4%BA%A4%E5%8F%89%E5%BC%95%E7%94%A8/update_cross_reference.png)

# 0x06 小结

在 Microsoft Word 2013 下对公式进行自动编号与交叉引用的方法较多，本文根据笔者自身需求总结而成，以备日后写作之需，若有理解上或操作上的疑惑还请读者不吝告知，谢谢。

相关参考文章如下：

> [WORD中公式的自动编号和交叉引用方法](https://jingyan.baidu.com/article/4dc408486da1e1c8d946f133.html)
> [在 Word 2013 中编写公式并标号](https://blog.csdn.net/wihiw/article/details/64443494)
> [Word论文写作如何实现公式居中、编号右对齐](https://jingyan.baidu.com/article/948f592421b812d80ef5f971.html)