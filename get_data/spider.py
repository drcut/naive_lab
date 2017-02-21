#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import urllib
import urllib2
from pyquery import PyQuery as pq
import time
'''
var base_url = window.base_url ? window.base_url : '';
function getSubDown(id , s_id) {
    window.location.href = base_url + "index.php?m=down&a=sub&id=" + id + "&s_id=" + s_id;
}
'''
PAGE_START = 500
#PAGE_END = 500
PAGE_END = 194910
Local = '/media/robin/sorry/spider/new_conversition/'
global Be_Banded
Be_Banded = False
base_url = 'http://www.subom.net/sinfo/'
page_num = PAGE_START
total_num = PAGE_END
def Schedule(a,b,c):
    '''''
    a:已经下载的数据块
    b:数据块的大小
    c:远程文件的大小
   '''
    if(c == 33):
        global Be_Banded
        Be_Banded=True

def index_page(response):
        #have chinese or not
    flag = False
    for each in response('.div_content'):
        tmp_str = pq(each).text()
        if(tmp_str.find(u"字幕语种")>-1):
            if(tmp_str.upper().find(u"VOBSUB")>-1):
                flag = False
                break
            if(tmp_str.find(u"简")>-1) or (tmp_str.find(u"中")>-1):
                flag = True
            break
    if(flag == True):
         for tmp_class in response('.div_content')('ul'):
           tmp_html=pq(tmp_class).html()
           start_pos=tmp_html.find('getSubDown')
           if(start_pos>-1):
                 tmp=pq(tmp_html).find('li').eq(0)('a').attr('onclick').split("'")
                 url = base_url + str(page_num)+"/index.php?m=down&a=sub&id="+str(tmp[1])+"&s_id="+str(tmp[3])
                 urllib.urlretrieve(url, Local+str(tmp[1]),Schedule)
                 time.sleep(1)
if __name__ == '__main__':     
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    while page_num <= total_num:
          print float(page_num)/float(total_num)
          url = base_url + str(page_num)
          request = urllib2.Request(url,headers = headers)
          response = urllib2.urlopen(request)
          content = response.read().decode('utf-8')
          #print content
          index_page(pq(content))
          if(Be_Banded == True):
            print "fuck! I am banded!"
            break
          page_num += 1               