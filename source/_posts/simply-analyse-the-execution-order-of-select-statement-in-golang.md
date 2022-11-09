---
title: 浅析 Go select 语句的执行顺序问题
copyright: true
date: 2022-11-09 23:07:19
tags: [Go,Syntax]
categories: [Programming,Go]
---

# 0x00 前言

Go 语言中的 select 语句，用于控制 channel 的通信操作，分为[发送操作](https://go.dev/ref/spec#Send_statements)与[接收操作](https://go.dev/ref/spec#Receive_operator)两类。

众所周知，大多数教程只是大致描述了 select 语句的执行流程：当 case 中存在一个或多个可执行的通信操作时，会随机选择进入其中一个，并完成该 case 下的相应语句。当不存在可执行的通道操作时，会先判断是否存在 default case，有则进入，无则阻塞，直至通信操作可执行。

然而，对 case 中表达式的执行顺序，却少有解释。接下来，本文**将根据官方对 select 语句的定义说明，重点阐述 case 中表达式的执行顺序问题**，并给出样例辅助理解，最后对整体执行流程做出总结。

<!-- more -->

# 0x01 select 语句官方说明

Go 语言对 select 语句的官方说明，对于初学者而言难免晦涩难懂。为了帮助读者更好地理解，本章先对官方说明进行中英对译，再重点阐述 case 中表达式的执行顺序问题。

## 中英对译

**Select statements**

**Select 语句**

A "select" statement chooses which of a set of possible [send](https://go.dev/ref/spec#Send_statements) or [receive](https://go.dev/ref/spec#Receive_operator) operations will proceed. It looks similar to a ["switch"](https://go.dev/ref/spec#Switch_statements) statement but with the cases all referring to communication operations.

select 语句用于从一组[发送操作](https://go.dev/ref/spec#Send_statements)或[接收操作](https://go.dev/ref/spec#Receive_operator)中，选出一个可执行的操作。这有点像 [switch](https://go.dev/ref/spec#Switch_statements) 语句，只不过 case 都换成了与通信相关的操作而已。

```go
SelectStmt = "select" "{" { CommClause } "}" .
CommClause = CommCase ":" StatementList .
CommCase   = "case" ( SendStmt | RecvStmt ) | "default" .
RecvStmt   = [ ExpressionList "=" | IdentifierList ":=" ] RecvExpr .
RecvExpr   = Expression .
```

> 译者注：这是一种名为 [Wirth syntax notation (WSN)](https://en.wikipedia.org/wiki/Wirth_syntax_notation) 的元语法标记，用于正式定义与描述 select 语句。考虑到上述标记在官方文档中均能找到定义，具有唯一性，因此后文不进行翻译。

A case with a RecvStmt may assign the result of a RecvExpr to one or two variables, which may be declared using a [short variable declaration](https://go.dev/ref/spec#Short_variable_declarations). The RecvExpr must be a (possibly parenthesized) receive operation. There can be at most one default case and it may appear anywhere in the list of cases.

case 中的 RecvStmt 可将 RecvExpr 的结果赋值给一个或两个变量，同时也支持[短变量声明](https://go.dev/ref/spec#Short_variable_declarations)。其中，RecvExpr 表达式（可能被括号括起）必须为接收操作。另外，可以在多个 case 之间的任何位置，添加至多一个 default case。

Execution of a "select" statement proceeds in several steps:

1. For all the cases in the statement, **the channel operands of receive operations** and **the channel and right-hand-side expressions of send statements** are evaluated exactly once, in source order, upon entering the "select" statement. The result is a set of channels to receive from or send to, and the corresponding values to send. Any side effects in that evaluation will occur irrespective of which (if any) communication operation is selected to proceed. Expressions on the left-hand side of a RecvStmt with a short variable declaration or assignment are not yet evaluated.

2. If one or more of the communications can proceed, a single one that can proceed is chosen via a uniform pseudo-random selection. Otherwise, if there is a default case, that case is chosen. If there is no default case, the "select" statement blocks until at least one of the communications can proceed.

3. Unless the selected case is the default case, the respective communication operation is executed.

4. If the selected case is a RecvStmt with a short variable declaration or an assignment, **the left-hand side expressions** are evaluated and **the received value (or values)** are assigned.

5. The statement list of the selected case is executed.

select 语句的执行流程有以下步骤：

1. 在真正进入 select 语句之前，会按照源代码的编写顺序，检视所有 case 中的表达式，并对其中**接收操作的通道操作数**，以及**发送语句中的通道与右值表达式**进行一次求值，其结果将作为接收或发送操作的通道，以及相应待发送的值。上述求值过程可能会出现意想不到的副作用，并且与哪一个通信操作被选择执行了（如果有的话）无关。注意，此时 RecvStmt 中的短变量声明或变量赋值语句，其左值表达式尚未进行求值。
2. 若存在一个或多个可执行的通信操作，则其中一个会被统一的伪随机算法选择执行。否则，若存在一个 default case，则会选择执行；若不存在 default case，select 语句会一直阻塞到至少存在一个可执行的通信操作为止。
3. 执行所选 case 中相应的通信操作，而 default case 不涉及。
4. 如果所选的 case 是短变量声明或变量赋值的 RecvStmt，则会对其**左值表达式**进行求值，并把**接收到的值**赋给它。
5. 最后依次执行所选 case 下的所有语句。

Since communication on `nil` channels can never proceed, a select with only `nil` channels and no default case blocks forever.

由于 `nil` 通道无法执行通信操作，因此只有 `nil` 通道且不存在 default case 的 select 语句将永远阻塞。

```go
var a []int
var c, c1, c2, c3, c4 chan int
var i1, i2 int
select {
case i1 = <-c1:
	print("received ", i1, " from c1\n")
case c2 <- i2:
	print("sent ", i2, " to c2\n")
case i3, ok := (<-c3):  // same as: i3, ok := <-c3
	if ok {
		print("received ", i3, " from c3\n")
	} else {
		print("c3 is closed\n")
	}
case a[f()] = <-c4:
	// same as:
	// case t := <-c4
	//	a[f()] = t
default:
	print("no communication\n")
}

for {  // send random sequence of bits to c
	select {
	case c <- 0:  // note: no statement, no fallthrough, no folding of cases
	case c <- 1:
	}
}

select {}  // block forever
```

## 流程解析

接下来，重点关注上述 select 语句的执行流程。

开发者通常遇到的场景，只要理解了流程中的第 2、3、5 步，即可编写出所需逻辑，这也是开头所说的，大多数教程对 select 语句执行流程的大致描述。

随着接触到的业务场景日益渐增，不可避免地需要编写复杂的代码逻辑，这要求 select 语句与其他表达式或数据类型结合使用，而不只是通道的直接发送或接收那么简单。**因此，能正确理解流程中的第 1、4 步，是完全掌握 select 语句用法的前提。**

为了更直观地理解第 1、4 步的含义，专门绘制以下对应关系图：

![step1-in-select-case](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/simply-analyse-the-execution-order-of-select-statement-in-golang/step1-in-select-case.png)

- 接收操作：`recv_ch` 是通道操作数，可为接收通道，或输出结果为接收通道的表达式。
- 发送操作：`send_ch` 是发送通道，或输出结果为发送通道的表达式；而 `expression` 是右值表达式，其值将会被发送至 `send_ch` 通道中。

![step4-in-select-case](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/simply-analyse-the-execution-order-of-select-statement-in-golang/step4-in-select-case.png)

- 接收操作：`<-recv_ch` 是从接收通道中获取的值，将赋值给左值表达式 `a[f()]`，此处 `a` 为 map 或 slice 类型的变量，因此需对 `f()` 进行求值以获取相应元素。注意，左值表达式可能为 int 或 string 等基本类型变量，也可能不存在，即赋值不是必须的。

# 0x02 样例验证

介绍完 select 语句的官方说明后，相信大家对它的整体执行流程有了一定理解。接下来，将用几个样例重点验证第 1、4 步流程，以助于巩固加强。

## 样例一

本样例的 select 语句构造了三个函数与三个 case，通过打印日志的方法以窥探其执行顺序：

- case 1：接收操作，从 `getIntChan()` 返回的无缓冲通道中，接收 int 类型数值并赋值给 `intArr[getInt(0)]` 元素，注意此处是通过 `getInt(0)` 来获取 `intArr` 的第一个元素。
- case 2：发送操作，将 `getInt(1)` 的求值结果，发送至 `getIntBufChan()` 返回的有缓冲通道中。
- default case：默认操作，只打印日志。

```go
package main

import "fmt"

var (
	intChan    = make(chan int)
	intBufChan = make(chan int, 2)
	intArr     = make([]int, 2)
)

func main() {
	go func() {
		intChan <- 0
	}()

	select {
	case intArr[getInt(0)] = <-getIntChan():
		fmt.Printf("select case 1\n")
	case getIntBufChan() <- getInt(1):
		fmt.Printf("select case 2\n")
	default:
		fmt.Printf("select default case\n")
	}
}

func getInt(i int) int {
	fmt.Printf("get int %d\n", i)
	return i
}

func getIntChan() chan int {
	fmt.Printf("get int chan\n")
	return intChan
}

func getIntBufChan() chan int {
	fmt.Printf("get int buf chan\n")
	return intBufChan
}
```

多次运行后，发现只有以下两种结果，而 default case 永远不会进入。

第一种结果选择 case 1，执行顺序为：`getIntChan()` -> `getIntBufChan()` -> `getInt(1)` -> `getInt(0)` -> `intArr[getInt(0)]` -> `fmt.Printf("select case 1\n")`

```go
get int chan
get int buf chan
get int 1
get int 0
select case 1
```

第二种结果选择 case 2，执行顺序为：`getIntChan()` -> `getIntBufChan()` -> `getInt(1)` -> `fmt.Printf("select case 2\n")`

```go
get int chan
get int buf chan
get int 1
select case 2
```

综上结果，与官方说明一致：执行流程第 1 步，先按代码编写顺序，分别对 `getIntChan()`、`getIntBufChan()`、`getInt(1)` 进行求值；执行流程第 4 步，若选择 case 1 的接收操作，则会对 `getInt(0)` 求值后进行赋值，否则 `getInt(0)` 不会执行。

## 样例二

本样例介绍一个在发送操作与接收操作中常见的理解误区，同样有三个函数与三个 case：

- case 1：发送操作与接收操作结合，将 `<-getIntChan()` 的求值结果，发送至 `getIntBufChan()` 返回的有缓冲通道中。
- case 2：接收操作，从 `getIntBufChan()` 返回的有缓冲通道中，接收 int 类型数值并赋值给 `intArr` 的第二个元素 `intArr[1]`。
- default case：默认操作，只打印日志。

```go
package main

import "fmt"

var (
	intChan    = make(chan int)
	intBufChan = make(chan int, 2)
	intArr     = make([]int, 2)
)

func main() {
	go func() {
		intBufChan <- 1
	}()

	select {
	case getIntBufChan() <- <-getIntChan():
		fmt.Printf("select case 1\n")
	case intArr[1] = <-getIntBufChan():
		fmt.Printf("select case 2\n")
	default:
		fmt.Printf("select default case\n")
	}
}

func getIntChan() chan int {
	fmt.Printf("get int chan\n")
	return intChan
}

func getIntBufChan() chan int {
	fmt.Printf("get int buf chan\n")
	return intBufChan
}
```

样例运行后，大家通常可能会认为 select 语句会选择 case 2，其实不然，在按顺序执行了 `getIntBufChan()`、`getIntChan()` 后，直接就报死锁错误了。

```go
get int buf chan
get int chan
fatal error: all goroutines are asleep - deadlock!

goroutine 1 [chan receive]:
main.main()
	C:/Go/src/select-test/main.go:17 +0x9d
```

以上结果的原因，在于对发送操作的右值表达式求值运算理解不到位：**select 语句需要获取 `<-getIntChan()` 表达式的求值结果，而不仅仅是 `getIntChan()` 的**。因此，在没有任何 goroutine 往 `intChan` 通道发送数据的情况下，想要从中接收数据必定是阻塞的，继而引发程序死锁。

在样例二的基础上，添加一个 goroutine 往 `intChan` 通道发送数据，即可解决问题：

```go
package main

import "fmt"

var (
	intChan    = make(chan int)
	intBufChan = make(chan int, 2)
	intArr     = make([]int, 2)
)

func main() {
	go func() {
		intChan <- 0
	}()
	go func() {
		intBufChan <- 0
	}()

	select {
	case getIntBufChan() <- <-getIntChan():
		fmt.Printf("select case 1\n")
	case intArr[1] = <-getIntBufChan():
		fmt.Printf("select case 2\n")
	default:
		fmt.Printf("select default case\n")
	}
}

func getIntChan() chan int {
	fmt.Printf("get int chan\n")
	return intChan
}

func getIntBufChan() chan int {
	fmt.Printf("get int buf chan\n")
	return intBufChan
}
```

多次运行后，同样发现只有以下两种结果，并且 default case 永远不会进入。

第一种结果选择 case 1，执行顺序为：`getIntBufChan()` -> `getIntChan()` -> `getIntBufChan()` -> `fmt.Printf("select case 1\n")`

```go
get int buf chan
get int chan
get int buf chan
select case 1
```

第二种结果选择 case 2，执行顺序为：`getIntBufChan()` -> `getIntChan()` -> `getIntBufChan()` -> `intArr[1]`-> `fmt.Printf("select case 2\n")`

```go
get int buf chan
get int chan
get int buf chan
select case 2
```

综上结果，需特别注意 `<-getIntChan()` 表达式在发送操作与接收操作中的区别：

- 接收操作：只需对 `getIntChan()` 求值，只要其返回结果是接收通道即可。
- 发送操作：需要对 `<-getIntChan()` 整体求值，其返回结果必须是发送通道相应的数据类型。

# 0x03 总结

至此，相信大家对 select 语句的整体执行流程有了更全面的理解，也欢迎大家提出不同见解，相互交流学习。

最后附上一张 select 语句完整的执行流程图：

![steps-in-select-statement](https://blog-1255335783.cos.ap-guangzhou.myqcloud.com/simply-analyse-the-execution-order-of-select-statement-in-golang/steps-in-select-statement.png)

## 参考

[1] [The Go Programming Language Specification - Select statements](https://go.dev/ref/spec#Select_statements)

[2] [Go 语言 select 语句](https://www.runoob.com/go/go-select-statement.html)

[3] [Go语言36讲笔记--11通道的高级使用方式](https://juejin.cn/post/7085618326516269064)

[4] [go语言select语句中的求值问题](https://blog.csdn.net/qmhball/article/details/120290804)