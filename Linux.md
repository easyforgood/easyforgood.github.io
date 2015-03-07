##Linux内核分析作业1：X86体系下计算机是如何运行程序

-----
###一、 现代计算机模型---冯诺依曼体系结构

冯诺依曼体系结构就是指存储程序计算机

经典的存储程序计算机由以下五部分组成：
![jiego](http://baike.soso.com/p/20090709/20090709080850-1101162591.jpg)

(其中 实线代表 数据线 虚线代表 控制线)


1. 采用存储程序方式，指令和数据不加区别混合存储在同一个存储器中，（数据和程序在内存中是没有区别的,它们都是内存中的数据,当EIP指针指向哪 CPU就加载那段内存中的数据,如果是不正确的指令格式,CPU就会发生错误中断. 在现在CPU的保护模式中,每个内存段都其描述符,这个描述符记录着这个内存段的访问权限(可读,可写,可执行).这最就变相的指定了哪个些内存中存储的是指令哪些是数据）
指令和数据都可以送到运算器进行运算，即由指令组成的程序是可以修改的。
2. 存储器是按地址访问的线性编址的一维结构，每个单元的位数是固定的。
2. 指令由操作码和地址组成。操作码指明本指令的操作类型,地址码指明操作数和地址。操作数本身无数据类型的标志，它的数据类型由操作码确定。
2. 通过执行指令直接发出控制信号控制计算机的操作。指令在存储器中按其执行顺序存放，由指令计数器指明要执行的指令所在的单元地址。指令计数器只有一个，一般按顺序递增，但执行顺序可按运算结果或当时的外界条件而改变。
2. 以运算器为中心，I/O设备与存储器间的数据传送都要经过运算器。
2. 数据以二进制表示。

（上的现代微处理器体系结构这么课还提到了[哈佛结构](http://www.cnblogs.com/li-hao/archive/2011/12/21/2296010.html) 和冯诺依曼结构区别主要在于数据和指令分开存储）
###二、 X86计算机结构


[80X86寄存器详解](http://www.cnblogs.com/zhaoyl/archive/2012/05/15/2501972.html)
![结构](/images/r2.png)

###三、实验代码汇编分析
C语言代码如下：
``` c
int g(int x){
    return x-3;
}
int f(int x){
    return g(x);
}
int main(){
    return f(1)+2;
}
```
通过gcc进行编译后生成*.s汇编代码
```sh
$ gcc -S -o main.s main.c -m32
```
(注：-m32 代表以32bit为链接库编译 64bit操作系统需要安装[libc6:i386](http://andycoder.me/fix-32bug-under-ubuntu1404/) 32位库)

得到汇编代码main.s:
(这里删除了.long .global .section [节或汇编程序辅助信息](http://blog.csdn.net/jnu_simba/article/details/11747901))
```as
g:
    pushl	%ebp
	movl	%esp, %ebp
	movl	8(%ebp), %eax
	subl	$3, %eax
	popl	%ebp
	ret
f:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$4, %esp
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
	call	g
	leave
	ret
main:
	pushl	%ebp
	movl	%esp, %ebp
	subl	$4, %esp
	movl	$1, (%esp)
	call	f
	addl	$2, %eax
	leave
	ret

```
以下是分析：

main：
```
	pushl	%ebp
	movl	%esp, %ebp
```


这两条指令可以放在一起看 相当于enter

进入函数体都会最先执行这条enter指令

作用是切换到保存上一个栈的栈底，并且将当前栈顶位置设置为栈底


![结构](/images/1.png)


```
	subl	$4, %esp
	movl	$1, (%esp)
```
这两条指令也可以放在一起看

在main函数中我们是f(1)+2 吗？这里有个 立即数1 
我们要如何使用这个参数呢？肯定需要把他放在内存中放在堆栈中

所以这里 先是下移一个位置，指向一个空的区域，然后把 ‘1’ 放入这个空间中

相当于 push $1


![结构](/images/2.png)

![结构](/images/3.png)



```
    call f
```
call f 是两步操作构成的
- 将 eip 的值入栈。
- 将 f所指向指令的地址放入 eip中

执行完之后，程序就会跳转到f: 指向的命令中执行，此时栈结构如下：
![结构](/images/4.png)


f:
```
	pushl	%ebp
	movl	%esp, %ebp

```
前两条和main中相同

这时候栈结构我们可以发现。栈在逻辑上的划分：！！！函数调用栈

![结构](/images/5.png)

```
	subl	$4, %esp
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
```
关键是这三条指令 通过栈结构 
首先是分配一块空的空间 然后
我们可以发现ebp指向的是我们之前调用f中传入的参数 1 
所以eax = 1变成了


![结构](/images/6.png)

```
	call	g
```
![结构](/images/7.png)

保存eip，并给eip赋值为g指令的地址，进行跳转
```
	pushl	%ebp
	movl	%esp, %ebp
	movl	8(%ebp), %eax
	subl	$3, %eax
```
前两条指令同样是enter操作

![结构](/images/8.png)

```
movl	8(%ebp), %eax
```
![结构](/images/9.png)

通过栈结构知道 将参数放入eax中
然后 
```
    subl	$3, %eax
```
将eax的值-3并放入eax中

![结构](/images/10.png)

```
	popl	%ebp
```

![结构](/images/11.png)

可以看到esp指向的上一个函数调用栈的基址
popl恢复上一个函数调用栈的地址

```
    ret
``` 
ret 和call相反 popl eip 将esp弹出并赋值给eip

![结构](/images/12.png)

使得程序从上次调用的地方开始执行
即：
f:
```
	leave
	ret
```
leave 是和 enter 相反的过程
相当于
```
    movl %ebp,%esp
    popl %ebp
```

![结构](/images/13.png)

![结构](/images/14.png)

ebp的值为上一个之前保存的上一个函数调用栈的栈底地址
最后 ret 回到 main

![结构](/images/15.png)

main:
```
	addl	$2, %eax
	leave
	ret
```

![结构](/images/16.png)

之前的计算我们可以发现都是把
结果放在eax里的

所以 可以发现 return的值就保存在这里

所以 直接 通过eax进行计算
最后恢复保存的栈底并退出

完成整个程序的执行过程

实验截图：

![结构](/images/sy1.png)

![结构](/images/sy2.png)


###四、总结

冯诺依曼体系结构实际上就是按照线性的内存结构 执行程序的过程。
由于 结构是线性的，所以很容易找到数据所在的位置
比如：充分利用函数调用栈的机制，可以很容易找到上个函数传递过来的参数


除了内存意外，计算机在运行过程中，还需要关注体系结构中的寄存器。

不同的寄存器存放了不同的信息，记录数据和指令的位置。


> ###[有一个关于函数调用栈的细节](http://www.cnblogs.com/Quincy/archive/2012/03/27/2418835.html)
>就是为什么向下增长。因为觉得向上增长才是很自然地事情
查了一下大概有两个理由：

> 1. 这样的就不用给栈和堆划分明显的分界线
> 2. 由于堆是向上增长的，所以可以充分利用进程的内存空间


-------
附：






