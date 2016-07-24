
---
title: Linux内核分析作业8：理解进程调度时机跟踪分析进程调度与进程切换的过程
date: 2016-03-31 01:50:15
tags: [linux,linux内核]
categories: linux内核分析
---

### 一、进程调度的基本知识

#### 1. linux进程调度的时机

**调度时机只是判断是否调度但是不一定真的调度**

- 进程状态转换的时刻：进程终止、进程睡眠  例如 调用sleep() wait()  调用sh
- 当前进程的时间片用完时  和中断返回一样
- 设备驱动程序 设备驱动程序执行长而重复的任务时，直接调用调度程序
- 进程从中断、异常及系统调用返回到用户态时 都会回到 ret_from_sys_call 对need_resched判断是否需要调度

老师的站在另外一个角度：

- 中断处理过程返回会调用 
- 内核线程可以直接调用schedule()进行进程切换
- 用户态进程无法直接调用。只能在进入内核态后才有机会。



#### 2. 时钟中断进程切换的简易流程(感觉其他的切换只是这个的一部分)

**schedule（）**：主要函数进程调度函数完成进程的选择和上下文切换
**do_timer（）**：时钟函数 
参考书上一段资料：
> 在CFS(unix引入的公平调度器)中，tick中断（do_timer()）首先更新调度信息。然后调整当前进程在红黑树中的位置。调整完成后如果发现当前进程不再是最左边的叶子(左边代表优先级最高)，就标记need_resched标志

**ret_from_sys_call（）**：当一个系统调用或中断完成时，该函数被调用，用于处理一些收尾工作。

do_timer() 修改进程信息、置标志位 --------> ret_from_sys_call 判断标志位 --------> call SYMBOL_NAME(schedule) 调用  schedule（）完成切换





	

### 二、进程切换过程跟踪 (没啥内容)

切换主要流程：
![Alt text](./1430066325270.png)

先进入schedule()
![Alt text](./1430066602474.png)

通过 pick_next_task 找到下一个切换的进程

![Alt text](./1430066690011.png)

进入context_switch进行进程上下文切换

![Alt text](./1430066761279.png)


这里跟踪到了 __switch_to但是没有找到switch_to

switch_to 主要是esp和eip切换
__switch_to 网上找的的说法是
切换浮点部件寄存器和状态 fpu
重设TSS的esp0 
设置current_task 这个还是很重要的。
![Alt text](./1430067352414.png)

另外一个小细节

由于调用__switch_to时不是通过call指令，而是jmp

然后 __switch_to也会return 这是就会执行标号1的内容了







### 三、switch_to 进程切换简要分析

在内核态，进程切换主要分两步：

1：切换页全局目录

2：切换堆栈和硬件上下文 switch_to 实现

switch_to:
		
- 把eflags和ebp寄存器保存到prev内核栈中。
- esp保存到prev->thread.sp 就是保存在进程状态描述符tss中。 把$1f保存到prev->thread.ip
- 恢复next进程的堆栈  把next指向的新进程的thread.esp保存到esp中，把next->thread.ip保存到eip中

__switch_to:

切换内核堆栈之后，TSS段也要相应的改变

> 这是因为对于linux系统来说同一个CPU上所有的进程共用一个TSS，进程切换了，因此TSS需要随之改变。
> 
> linux系统中主要从两个方面用到了TSS：
>
>(1)任何进程从用户态陷入内核态都必须从TSS获得内核堆栈指针
>
>(2)用户态读写IO需要访问TSS的权限位图。
> 

### 四、总结

马上要考试了。各位加油

参考文献：

- linux kernel development  一书 Robert.Lover

- [深入分析Linux内核源码](http://oss.org.cn/kernel-book/)
