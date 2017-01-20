#-*-coding:utf-8 -*-
import re  
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

def subReplace(line):
    regex = re.compile(ur"[^\u4e00-\u9fa5，．、：；（） ！]")
    return regex.sub('',line.decode('utf-8'))

file_object = open('result.txt')
try:
     for line in file_object:
        t_line = subReplace(line)
        #print t_line
        for char in t_line:
            if(char==u"，"or char==u"．"or char==u"、"or char==u"："or char==u"；"or char==u"（"or char==u"）"or char==u"！"):
                print 'EOS'
            else:
                #t_res.append(char.encode('utf8'))
                #print char,
                sys.stdout.write(char)
finally:
     file_object.close( )
     #file_w.close( )