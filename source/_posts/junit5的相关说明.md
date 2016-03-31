---
title: junit5的相关说明
date: 2016-03-31 01:50:15
tags: 测试
categories:
---

 >  Junit上一次大版本更新已经是在10年前了。Junit后来变得维护，出现了有很多未解决的bug以及并没有融入java尤其是java8的新特性导致已经有些跟不上时代了。因此Marc Philipp 进行众筹junit-lamabda活动，让更多的开发者参与到新的junit项目来，为junit提供更好服务和扩展。 
 >  junit 5 是基于 junit-lamabda诞生的。

*开源软件要不有基金会。要不然有社区氛围才行。不然真的很难坚持，众筹这个方法挺好*

[indiegogo的众筹首页](https://www.indiegogo.com/projects/junit-lambda#/)

------------------------------------

##### 目前版本情况：

junit 5 已经推出了alpha版本，预计今年4月底的时候会发布5.0 M1。


*[github上里程碑](https://github.com/junit-team/junit5/milestones)*


##### 关于新的特点：

*具体可以参考[user guide ](http://junit.org/junit5/)*

1. Annotation 产生了变化 之前的feature 特性有不同

- @Before and @After no longer exist; use @BeforeEach and @AfterEach instead.
- @BeforeClass and @AfterClass no longer exist; use @BeforeAll and @AfterAll instead.
- @Ignore no longer exists: use @Disabled instead.
- @Category no longer exists; use @Tag instead.
- @RunWith no longer exists; superseded by @ExtendWith.
- @Rule and @ClassRule no longer exist; superseded by @ExtendWith.

2. grouped assertions，支持lamada以及assert 多个值进行判断

``` java
//junit4 断言只能判断一个值就会中断
assertAll("address",
            () -> assertEquals("John", address.getFirstName()),
            () -> assertEquals("User", address.getLastName())
        );
     
```

3.  **extension model**  扩展你的程序
提供了 单独的 extension api。
之前必须要重写 runner 或者rule 或者class rule 才可以。 扩展性更加统一了。强大了。

4.  **The JUnit 5 Launcher API** 更加强大而且独立的启动选项	
主要强大的地方在于提供了  discover, filter, and execute JUnit tests. 的机制。
 
 独立性比原来更好。可以从外部配置以及执行
 而且希望第三方运行库包括Spock, Cucumber, and FitNesse 可以结合进来。

5.  其他小地方
- 可以在test方法里面添加参数 以及 添加日志信息
MethodParameterResolver 
这个地方是可以通过extension api扩展的
- 嵌套测试

- 对测试异常的支持 expectthrows 提供简单的方式支持复杂的异常断言
``` java
Throwable exception = expectThrows(IllegalArgumentException.class,
            () -> { throw new IllegalArgumentException("a message"); }
    );

    assertEquals("a message", exception.getMessage());
```






--------------------
参考：

http://blog.csdn.net/chszs/article/details/50662639

http://www.infoq.com/cn/news/2016/03/junit5-alpha


