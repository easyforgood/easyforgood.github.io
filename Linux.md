##Linux内核分析作业1：X86体系下计算机是如何运行程序

-----
###一、 现代计算机模型---冯诺依曼体系结构
###二、 X86计算机结构
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

![结构](.\images\1.png)


```
	subl	$4, %esp
	movl	$1, (%esp)
```
这两条指令也可以放在一起看

在main函数中我们是f(1)+2 吗？这里有个 立即数1 
我们要如何使用这个参数呢？肯定需要把他放在内存中放在堆栈中

所以这里 先是下移一个位置，指向一个空的区域，然后把 ‘1’ 放入这个空间中

相当于 push $1

![结构](.\images\2.png)
![结构](.\images\3.png)


```
    call f
```
call f 是两步操作构成的
- 将 eip 的值入栈。
- 将 f所指向指令的地址放入 eip中

执行完之后，程序就会跳转到f: 指向的命令中执行，此时栈结构如下：
![结构](.\images\4.png)


f:
```
	pushl	%ebp
	movl	%esp, %ebp

```
前两条和main中相同

这时候栈结构我们可以发现。栈在逻辑上的划分：！！！函数调用栈

![结构](.\images\5.png)

```
	subl	$4, %esp
	movl	8(%ebp), %eax
	movl	%eax, (%esp)
```
关键是这三条指令 通过栈结构 
首先是分配一块空的空间 然后
我们可以发现ebp指向的是我们之前调用f中传入的参数 1 
所以eax = 1变成了

![结构](.\images\6.png)

```
	call	g
```
![结构](.\images\7.png)

保存eip，并给eip赋值为g指令的地址，进行跳转
```
	pushl	%ebp
	movl	%esp, %ebp
	movl	8(%ebp), %eax
	subl	$3, %eax
```
前两条指令同样是enter操作
![结构](.\images\8.png)

```
movl	8(%ebp), %eax
```
![结构](.\images\9.png)

通过栈结构知道 将参数放入eax中
然后 
```
    subl	$3, %eax
```
将eax的值-3并放入eax中

![结构](.\images\10.png)

```
	popl	%ebp
```
![结构](.\images\11.png)
可以看到esp指向的上一个函数调用栈的基址
popl恢复上一个函数调用栈的地址

```
    ret
``` 
ret 和call相反 popl eip 将esp弹出并赋值给eip
![结构](.\images\12.png)

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
![结构](.\images\13.png)
![结构](.\images\14.png)

ebp的值为上一个之前保存的上一个函数调用栈的栈底地址
最后 ret 回到 main
![结构](.\images\15.png)
main:
```
	addl	$2, %eax
	leave
	ret
```
![结构](.\images\16.png)
之前的计算我们可以发现都是把结果放在eax里的

所以 可以发现 return的值就保存在这里

所以 直接 通过eax进行计算
最后恢复保存的栈底并退出

完成整个程序的执行过程

实验截图：
![结构](.\images\sy1.png)

-------
###四、总结

- 有一个关于函数调用栈的细节
    
就是向下增长





