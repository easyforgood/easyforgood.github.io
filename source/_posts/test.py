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

# print changeLine("#####1231312");
# print changeLine("12312312");
for filename in flist:
	with open(filename,"r+") as f:
		newline=[changeLine(lineStr) for lineStr in f.readlines()]
 		f.seek(0)
		f.writelines(newline)

