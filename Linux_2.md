---
layout: page
title: Linux内核分析作业2：
tagline: 一个简单的时间片轮转多道程序内核代码
---
{% include JB/setup %}

####朋翔 原创作品转载请注明出处《Linux内核分析》MOOC课程http://mooc.study.163.com/course/USTC-1000029000 

---
github项目：[Mykernel](https://github.com/mengning/mykernel)

###一、步骤整理

请先在下载好[linux-3.9.4.tar.xz](https://www.kernel.org/pub/linux/kernel/v3.x/linux-3.9.4.tar.xz ) 

1. 安装 qemu

		sudo apt-get install qemu # install QEMU
		sudo ln -s /usr/bin/qemu-system-i386 /usr/bin/qemu
2. 解压 linux
	
		xz -d linux-3.9.4.tar.xz
		tar -xvf linux-3.9.4.tar
3. 打内核补丁  [mykernel_for_linux3.9.4sc.patch](https://github.com/mengning/mykernel/blob/master/mykernel_for_linux3.9.4sc.patch)

		patch -p1 < ../mykernel_for_linux3.9.4sc.patch
4. 编译运行 
			
			make allnoconfig
			make
			qemu -kernel arch/x86/boot/bzImage

实验截图：


![enter image description here](/linux2/lab2_1.png)


![enter image description here](/linux2/lab2_2.png)

![enter image description here](/linux2/lab2_3.png)

5. 将 mypcb.h 、mymain.c、myinterrupt.c 放入mykernel 文件夹 并编译运行 

![enter image description here](/linux2/lab2_4.png)


###二、内核代码执行过程

核心代码主要由：mypcb.h 、mymain.c、myinterrupt.c三个文件构成

####1. mypcb.h

	#define MAX_TASK_NUM        4
	#define KERNEL_STACK_SIZE   1024*8

	/* CPU-specific state of this task */
	struct Thread {
	    unsigned long		ip;
	    unsigned long		sp;
	};
	
	typedef struct PCB{
	    int pid;
	    volatile long state;	/* -1 unrunnable, 0 runnable, >0 stopped */
	    char stack[KERNEL_STACK_SIZE];
	    /* CPU-specific state of this task */
	    struct Thread thread;
	    unsigned long	task_entry;
	    struct PCB *next;
	}tPCB;
	
	void my_schedule(void);

这里主要是定义了进程控制块的参数。
参数主要包括了：
> - pid 进程标识符
> - state 进程运行状态
> - thread 进程寄存器的信息 包括了 堆栈sp指针和当前进程指令ip
> - task_entry 进程运行代码的入口
> - 下一个进程控制块（进程控制块是以链表的方式组织的）

####2. mymain.h

先说下my_process()
这个函数是进程调度时会运行的代码

		void my_process(void)
	{
	    int i = 0;
	    while(1)
	    {
	        i++;
	        if(i%10000000 == 0)
	        {
	            printk(KERN_NOTICE "this is process %d -\n",my_current_task->pid);
	            if(my_need_sched == 1)
	            {
	                my_need_sched = 0;
	        	    my_schedule();
	        	}
	        	printk(KERN_NOTICE "this is process %d +\n",my_current_task->pid);
	        }     
	    }

逻辑很简单，就是进程执行循环执行某个人物，当执行到i%10000000=0时，会进行调度。

如果my_need_sched =1 会进行主动调度，执行调度函数 my_schedule()

而这个 my_need_sched=1 是每次时钟中断发生时会改变一次，我们后面会看到

接着分析，my_main.c中主要的

	void __init my_start_kernel(void)
	{
		int pid = 0;
	    int i;
	    /* Initialize process 0*/
	    task[pid].pid = pid;
	    task[pid].state = 0;/* -1 unrunnable, 0 runnable, >0 stopped */
	    task[pid].task_entry = task[pid].thread.ip = (unsigned long)my_process;
	    task[pid].thread.sp = (unsigned long)&task[pid].stack[KERNEL_STACK_SIZE-1];
	    task[pid].next = &task[pid];
	    /*fork more process */
	    for(i=1;i<MAX_TASK_NUM;i++)
	    {
	        memcpy(&task[i],&task[0],sizeof(tPCB));
	        task[i].pid = i;
	        task[i].state = -1;
	        task[i].thread.sp = (unsigned long)&task[i].stack[KERNEL_STACK_SIZE-1];
	        task[i].next = task[i-1].next;
	        task[i-1].next = &task[i];
	    }
    /* start process 0 by task[0] */
	    /* start process 0 by task[0] */
	    pid = 0;
	    my_current_task = &task[pid];
		asm volatile(
	    	"movl %1,%%esp\n\t" 	/* set task[pid].thread.sp to esp */
	    	"pushl %1\n\t" 	        /* push ebp */
	    	"pushl %0\n\t" 	        /* push task[pid].thread.ip */
	    	"ret\n\t" 	            /* pop task[pid].thread.ip to eip */
	    	"popl %%ebp\n\t"
	    	: 
	    	: "c" (task[pid].thread.ip),"d" (task[pid].thread.sp)	/* input c or d mean %ecx/%edx*/
		);
	}   

前半部分比较简单。是初始化进程控制块，把他们连接在一起（这是一个循环链表），然后将当前进程my_current_task=task[0];

之后的操作就该是执行该控制块了。有这段汇编实现（**重点**）

	asm volatile(
		    	"movl %1,%%esp\n\t" 	/* set task[pid].thread.sp to esp */
		    	"pushl %1\n\t" 	        /* push ebp */
		    	"pushl %0\n\t" 	        /* push task[pid].thread.ip */
		    	"ret\n\t" 	            /* pop task[pid].thread.ip to eip */
		    	"popl %%ebp\n\t"
		    	: 
		    	: "c" (task[pid].thread.ip),"d" (task[pid].thread.sp)	/* input c or d mean %ecx/%edx*/
			);

这里应该是进行三步：

1.  切换esp
2.  保存上一个堆栈框架的ebp并且将ebp=esp（相当于entry **这里没有ebp=esp 不够严谨**）
3. 跳转到task[0]的执行流里（实现方式是先push到esp中，然后ret，当esp指向的元素pop到eip中）

这样一个进程就开始执行了。

####3. myinterrupt.c

这里是时钟中断发生的处理函数：

		void my_timer_handler(void)
	{
	#if 1
	    if(time_count%1000 == 0 && my_need_sched != 1)
	    {
	        printk(KERN_NOTICE ">>>my_timer_handler here<<<\n");
	        my_need_sched = 1;
	    } 
	    time_count ++ ;  
	#endif
	    return;  	
	}

主要的就是会修改 my_need_sched 这个值触发调度

my_schedule(void) 调度函数

	tPCB * next;
    tPCB * prev;

    if(my_current_task == NULL 
        || my_current_task->next == NULL)
    {
    	return;
    }
    printk(KERN_NOTICE ">>>my_schedule<<<\n");
    /* schedule */
    next = my_current_task->next;
    prev = my_current_task;

这一端代码的意思是

next 为下一个进程

prev 为当前进程

	if(next->state == 0)/* -1 unrunnable, 0 runnable, >0 stopped */
	    {
	    	/* switch to next process */
	    	asm volatile(	
	        	"pushl %%ebp\n\t" 	    /* save ebp */
	        	"movl %%esp,%0\n\t" 	/* save esp */
	        	"movl %2,%%esp\n\t"     /* restore  esp */
	        	"movl $1f,%1\n\t"       /* save eip */	
	        	"pushl %3\n\t" 
	        	"ret\n\t" 	            /* restore  eip */
	        	"1:\t"                  /* next process start here */
	        	"popl %%ebp\n\t"
	        	: "=m" (prev->thread.sp),"=m" (prev->thread.ip)
	        	: "m" (next->thread.sp),"m" (next->thread.ip)
	    	); 
	    	my_current_task = next; 
	    	printk(KERN_NOTICE ">>>switch %d to %d<<<\n",prev->pid,next->pid);   	
	    }
	    else
	    {
	        next->state = 0;
	        my_current_task = next;
	        printk(KERN_NOTICE ">>>switch %d to %d<<<\n",prev->pid,next->pid);
	    	/* switch to new process */
	    	asm volatile(	
	        	"pushl %%ebp\n\t" 	    /* save ebp */
	        	"movl %%esp,%0\n\t" 	/* save esp */
	        	"movl %2,%%esp\n\t"     /* restore  esp */
	        	"movl %2,%%ebp\n\t"     /* restore  ebp */
	        	"movl $1f,%1\n\t"       /* save eip */	
	        	"pushl %3\n\t" 
	        	"ret\n\t" 	            /* restore  eip */
	        	: "=m" (prev->thread.sp),"=m" (prev->thread.ip)
	        	: "m" (next->thread.sp),"m" (next->thread.ip)
	    	);          
	    }   

next->state 代表运行状态  =0 代表已经运行  =-1 代表 还没有运行

当next进程还没有运行时 进程切换的代码是这样的：

	asm volatile(	
	        	"pushl %%ebp\n\t" 	    /* save ebp */
	        	"movl %%esp,%0\n\t" 	/* save esp */
	        	"movl %2,%%esp\n\t"     /* restore  esp */
	        	"movl %2,%%ebp\n\t"     /* restore  ebp */
	        	"movl $1f,%1\n\t"       /* save eip */	
	        	"pushl %3\n\t" 
	        	"ret\n\t" 	            /* restore  eip */
	        	: "=m" (prev->thread.sp),"=m" (prev->thread.ip)
	        	: "m" (next->thread.sp),"m" (next->thread.ip)

步骤如下

首先要保存现场： 

1. 保存ebp到当前进程的esp中 pushl %%ebp\n\t
2. 保存当前esp的内容到 当前进程 movl %%esp,%0
3.  保存eip movl $1f,%1 这里的$1f是下次运行时第一条指令的位置，代表为f （forward）向前方向上 1 标号 所指指令的地址。

还有切换到当前进程的现场：

1.  恢复esp。movl %2,%%esp
2.  恢复ebp。movl %2,%%ebp  （**刚开始运行 ebp=esp**）

最后跳转到next进程的执行流中:
和之前一样

	pushl %3
	ret   

然后 ret的值就是my_process()这个函数的起始位置。开始执行该函数。

然后 这样运行第一圈之后，又会回到task[0] 此时task[0]已经运行了。所以会执行一下汇编进行进程切换。

	asm volatile(	
	        	"pushl %%ebp\n\t" 	    /* save ebp */
	        	"movl %%esp,%0\n\t" 	/* save esp */
	        	"movl %2,%%esp\n\t"     /* restore  esp */
	        	"movl $1f,%1\n\t"       /* save eip */	
	        	"pushl %3\n\t" 
	        	"ret\n\t" 	            /* restore  eip */
	        	"1:\t"                  /* next process start here */
	        	"popl %%ebp\n\t"
	        	: "=m" (prev->thread.sp),"=m" (prev->thread.ip)
	        	: "m" (next->thread.sp),"m" (next->thread.ip)
	    	); 

保存现场和恢复现场的部分是和之前一样的。
除了恢复现场没有恢复ebp

关键是还记得上一次我们保存 当前进程的eip的时候，保存的值是$1f嘛？
所以 

	pushl %3
	ret     
要进入下一个进程的执行流时，此时的eip 为 1 标号所对应的指令

	1：popl %%ebp

这样过程就完整了，恢复现场的工作完成了，ebp指向了正确的值。


###三、总结

其实，整个过程最重要的就是理解函数调用栈的框架。

这个框架大概是这样的

![enter image description here](/linux2/end.png)

保持这个框架的完整性即可

###四、补充

- volatile 限定符 变量放在register中  执行流 取的时候 要放到寄存器 放到内存会有问题