---
title: Javascript 判断 IP 地址是否属于 CIDR 范围
copyright: true
date: 2020-02-16 21:07:52
tags: [Javascript,ECMAScript,Network,RegEx]
categories: [Programming,Javascript]
---

# 0x00 前言

在项目过程中，曾遇到**根据 IP 地址判断 CIDR 网络区域、并且在前端展示**的需求。由于 Javascript 没有原生类库能对 IP 地址进行相关操作，因此本文将采用 ES6 的新特性**箭头函数**，精简地实现此判断功能。

<!-- more -->

# 0x01 基础概念

## 什么是 CIDR？

**[CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)（Classless Inter-Domain Routing，无类别域间路由）**是一种 IP 地址归类方法，主要用于分配 IP 地址与有效地路由 IP 数据包等功能。

CIDR 的表示方法为 `A.B.C.D/N`，其中 `A.B.C.D` 是点分十进制的 IPv4 地址，`N` 是 0 至 32 之间的整数，代表 CIDR 的前缀长度，两者用斜线 `/` 分隔。

若一个 IP 地址的前 `N` 位与 一个 CIDR 范围的前缀相同，则说明此 IP 地址在此 CIDR 范围中。以 CIDR 范围 `10.10.1.32/27` 为例，可知 `110.10.1.44` 属于该 CIDR 范围，而 `10.10.1.90` 则不属于。

![cidr-comparison](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/check-if-ip-belongs-to-cidr-by-javascript/cidr-comparison.png)

## 什么是箭头函数？

**[箭头函数](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions)表达式**是 ECMAScript 6 的新增语法，相比于普通函数表达式，它主要特点是具有更精简的表达语法，以及在函数体内不存在自己的 `this`、`arguments`、`super`、`new.target` 等变量。

以下变量 `a` 与 `b` 均可定义了一个平方数计算函数，可见 `a` 比 `b` 的定义更精简：

```javascript
const a = x => x * x;

// 等同于
const b = function(x) {
    return x * x;
};

a(2); // 4
b(2); // 4
```

箭头函数的特点及用法，请参考 0x03 中的相关教程，此处不再详解。

# 0x02 函数实现

## validateIp4

`validateIp4` 用于判断 IPv4 地址的合法性。需要满足以下三个要求：

- 由三个 `.` 符号分隔四部分整数
- 每部分整数范围是 0 至 255
- 每部分整数不能有前导 0

```javascript
const validateIp4 = ip =>
	/^((\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))(\.|$)){4}$/.test(ip) ? true : false;

validateIp4("192.168.1.1") // true
validateIp4("192.168.1") // false
validateIp4("192.168.1.1000") // false
validateIp4("192.168.1.01") // false
```

此函数通过正则表达式实现，其中：

- `(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))` 限定每部分整数取值只能为 0 至 9、10 至 99、100 至 255
- `(\.|$)` 限定每部分结尾只能是 `.` 符号或行尾

## validateCidr

`validateCidr` 用于判断 CIDR 范围的合法性。除了 IPv4 部分需要满足上述三个要求，前缀长度还需满足：

- 长度范围是 0 至 32
- 长度不能有前导 0

```javascript
const validateCidr = cidr =>
	/^((\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\.){3}((\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\/){1}(\d|[1-3]\d)$/.test(cidr) ? true : false;

validateCidr("192.168.1.1/24") // true
validateCidr("192.168.1.1") // false
validateCidr("192.168.1/24") // false
validateCidr("192.168.1.1/48") // false
validateCidr("192.168.1/024") // false
```

由于 IPv4 地址最后一部分不再匹配行尾，因此正则表达式拆分成两部分：IPv4 地址前三部分末尾匹配 `.` 符号，最后一部分末尾匹配 `/` 符号。此外，`(\d|[1-3]\d)` 限定前缀范围为 0 至 32。

## ip4ToInt

`ip4ToInt` 用于计算 IPv4 地址每部分整数的移位累加和。可以理解为，在去除 `.` 符号后，得到从左至右排列的 32 位二进制整数，再将其转换为十进制整数。

```javascript
const ip4ToInt = ip =>
	ip.split('.').reduce((sum, part) => (sum << 8) + parseInt(part, 10), 0) >>> 0;

ip4ToInt("192.168.1.1") // 3232235777
ip4ToInt("192.168.1") // 12625921
ip4ToInt("192.168.1.1000") // 3232236776
ip4ToInt("192.168.1.01") // 3232235777
```

由测试结果可见，函数暂未做 IPv4 地址合法性判断，适用于任何点分数字字符串，其中：

- `split('.')` 将 IPv4 地址的每部分取出，例如 `"192.168.1.1".split('.')` 将得到 `["192", "168", "1", "1"]`
- `reduce((sum, part) => (sum << 8) + parseInt(part, 10), 0)` 将计算每个数组元素的移位累加和，详细用法请参考：[Array.prototype.reduce()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/Reduce)
  - `sum` 为累加和，作为 `reduce` 函数的结果返回，初始值设置为 0
  - `part` 为每个数组元素，转换为十进制整数后，与左移 8 位后的 `sum` 相加
- `>>> 0 ` 将计算结果转换为 32 位无符号整数，详细含义请参考：[What is the JavaScript >>> operator and how do you use it?](https://stackoverflow.com/questions/1822350/what-is-the-javascript-operator-and-how-do-you-use-it)

## isIp4InCidr

`isIp4InCidr` 用于判断 IPv4 地址是否属于 CIDR 范围。函数中嵌套了子函数，`isIp4InCidr(ip)` 返回一个以 `cidr` 作为参数的函数，便于后续对多个 CIDR 范围进行判断。

```javascript
const isIp4InCidr = ip => cidr => {
    if (validateIp4(ip) && validateCidr(cidr)) {
        const [range, bits] = cidr.split('/');
        const mask = ~(2 ** (32 - bits) - 1);
        return (ip4ToInt(ip) & mask) === (ip4ToInt(range) & mask);
    } else {
        return false
    }
};

isIp4InCidr("192.168.1.1")("192.168.1.1/24") // true
isIp4InCidr("192.168.1.1")("192.168.1.1/48") // false
isIp4InCidr("192.168.1")("192.168.1.1/24") // false
```

若 IPv4 地址与 CIDR 范围均合法，则继续进行判断，否则返回 `false`，其中：

- `[range, bits] = cidr.split('/')` 使用了 ES6 的新特性[解构赋值](http://es6.ruanyifeng.com/#docs/destructuring)，`range` 为 CIDR 范围的 IPv4 部分，`bits` 为前缀长度部分
- `mask = ~(2 ** (32 - bits) - 1)` 根据前缀长度计算掩码，掩码的前 `bits` 位为 `1`，后 `32 - bits` 位为 `0`
- 若 `ip` 与 `range` 的前 `bits` 位相同，则返回 `true`，否则返回 `false`

## isIp4InCidrs

`isIp4InCidrs` 用于判断 IPv4 地址是否属于 CIDR 数组内的其中一个范围。函数基于 `isIp4InCidr`  实现。

```javascript
const isIp4InCidrs = (ip, cidrs) => cidrs.some(isIp4InCidr(ip));

isIp4InCidrs('192.168.10.1', ['10.10.0.0/16', '192.168.1.1/24']); // false
isIp4InCidrs('192.168.10.1', ['10.10.0.0/16', '192.168.1.1/16']); // true
isIp4InCidrs('10.10.10.10', ['10.10.0.0/48', '10.10.0.0/16']); // true
```

若 IPv4 地址属于CIDR 数组内的其中一个范围，则返回 `true`，结束判断，否则返回 `false`，其中：

- `some(isIp4InCidr(ip))` 将判断 CIDR 数组中，是否至少有一个元素满足 `isIp4InCidr(ip)` 为真，即 IPv4 地址属于某个 CIDR 范围，详细用法请参考：[Array.prototype.some()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/Some)

# 0x03 小结

本文主要是利用 ECMAScript 6 的新特性与 Array 对象的方法，精简地实现了 IPv4 地址是否属于某个 CIDR 范围的判断功能，文中不足或错误之处，恳请读者告知。

对功能实现与箭头函数有疑惑的读者，可参考以下文章：

[Determining if an IPv4 address is within a CIDR range in JavaScript](https://tech.mybuilder.com/determining-if-an-ipv4-address-is-within-a-cidr-range-in-javascript/)
[ES6 In Depth: Arrow functions](https://hacks.mozilla.org/2015/06/es6-in-depth-arrow-functions/)
[ECMAScript 6 入门教程——函数的扩展](http://es6.ruanyifeng.com/#docs/function)