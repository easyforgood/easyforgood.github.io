---
title: python 处理博客的md文件
date: 2016-04-01 02:04:42
tags:
categories:
---
关于 list comprehension 

作用是读取当前文件夹下的 md文件，然后 将###这类的标题后面加上一个空格。

用到list comprehension 一个fp的特性 再此mark



``` python
#  -*- coding:utf-8 -*-
import re
import os

def changeLine(str=""):
	p = re.compile("^#+")
	match=p.match(str)
	if match: #and match.group(1).start:
		str= match.group(0)+ " "+p.split(str)[1]
	return str

flist=os.listdir("./")

mdflist=[res for res  in flist if re.compile("^.*\.md$").match(res)]

filename='./Linux.md'

for filename in flist:
	with open(filename,"r+") as f:
		newline=[changeLine(lineStr) for lineStr in f.readlines()]
 		f.seek(0)
		f.writelines(newline)


```

### python 的 推导式

列表表达式的基本格式是; 
[表达式 for 变量 in 列表]    或者  [表达式 for 变量 in 列表 if 条件]

python 中支持的推导式

- 列表推导式
处理嵌套列表的实现
```
>>> names = [['Tom','Billy','Jefferson','Andrew','Wesley','Steven','Joe'],  
         ['Alice','Jill','Ana','Wendy','Jennifer','Sherry','Eva']]  
         
>>> [name for lst in names for name in lst if name.count('e')>=2]  #注意遍历顺序，这是实现的关键  
['Jefferson', 'Wesley', 'Steven', 'Jennifer']  

看下等价的实现就理解原理了
tmp = []  
for lst in names:  
    for name in lst:  
        if name.count('e') >= 2:  
            tmp.append(name)  
  
print tmp  
#输出结果  
['Jefferson', 'Wesley', 'Steven', 'Jennifer']  
结果就是被过滤的 name

```
- 字典推导式
```
>>> strings = ['import','is','with','if','file','exception']  
>>> D = {key: val for val,key in enumerate(strings)}  
```

- 集合推导式
```
>>> strings = ['a','is','with','if','file','exception']  
>>> {len(s) for s in strings}    #有长度相同的会只留一个，这在实际上也非常有用  
```
- 生成器推导式
*(用于列表太多占内存但是只需要计算一次的情况)*
```
>>>  L = (i for i in range(10) if i % 2 != 1)  
>>> L.next() 
0 
>>> L.next()
2  
```

### 推导式的原理

和数学上的策梅洛-弗兰克尔集合论[Zermelo-Fraenkel Set Theory](http://en.wikipedia.org/wiki/Zermelo-Frankel_set_theory)一样，被称为集合抽象

> 求集合Ａ中奇数的平方
> B = {square x | x ∈ A & odd x}


### 总结： 

推导式本质是一种语法糖，它提供了一种简洁高效的方式来创建列表和迭代器

很方便但是遇到复杂的情况就不好用了。比如说复杂的if判断和循环处理的时候。

这里就强行写了函数用来处理。


