#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import urllib
import urllib2
from pyquery import PyQuery as pq
import time
import getip
'''
var base_url = window.base_url ? window.base_url : '';
function getSubDown(id , s_id) {
    window.location.href = base_url + "index.php?m=down&a=sub&id=" + id + "&s_id=" + s_id;
}
'''

Local = '/media/robin/sorry/spider/new_conversition/'
global Be_Banded
Be_Banded = False
base_url = 'http://www.subom.net/sinfo/'
PAGE_START = 2881
PAGE_END = 194910
global page_num
page_num = PAGE_START
total_num = PAGE_END
def index_page(response):
        #have chinese or not
    global page_num    
    flag = False
    suffix = ''
    for each in response('.div_content'):
        tmp_str = pq(each).text()
        #print tmp_str
        if(suffix=='' and tmp_str.find(u"下载地址")!=-1 and tmp_str.find(u"zip")>-1):
          suffix=".zip"
        if(suffix=='' and tmp_str.find(u"下载地址")!=-1 and tmp_str.find(u"rar")>-1):
          suffix=".rar"
        if(tmp_str.find(u"字幕语种")>-1):
            if(tmp_str.upper().find(u"VOBSUB")>-1):
                flag = False
                break
            if(tmp_str.find(u"简")>-1) or (tmp_str.find(u"中")>-1):
                flag = True
            break
    if(flag == True):
         print "should download"
         for tmp_class in response('.div_content')('ul'):
           tmp_html=pq(tmp_class).html()
           start_pos=tmp_html.find('getSubDown')
           if(start_pos>-1):
                 tmp=pq(tmp_html).find('li').eq(0)('a').attr('onclick').split("'")
                 url = base_url + str(page_num)+"/index.php?m=down&a=sub&id="+str(tmp[1])+"&s_id="+str(tmp[3])
                 print "urlopen..."
                 try:
                   f = urllib2.urlopen(url,timeout=10) 
                   data = f.read() 
                   if(data.find("ERROR.")>-1):
                      global Be_Banded
                      Be_Banded=True
                      print "fuck! I am banded!"
                      return
                   with open(Local+str(tmp[1])+suffix, "wb") as code:     
                    code.write(data)
                    print "write:"+Local+str(tmp[1])
                 except Exception,e:
                  
                  page_num -= 1
                 #time.sleep(1)
if __name__ == '__main__':     
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    proxies = getip.getListProxies()
    while page_num<=total_num:
      '''
      print page_num
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
      '''
      for proxy in proxies:
        Be_Banded = False
        print "new proxy"
        proxy_support = urllib2.ProxyHandler(proxy)
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        while page_num<=total_num:
            print page_num
            url = base_url + str(page_num)
            request = urllib2.Request(url,headers = headers)
            try:  
              response = urllib2.urlopen(request,timeout=10)
              content = response.read().decode('utf-8')
            #print content
              index_page(pq(content))
              if(Be_Banded == True):
                break
            except Exception,e:  
              print Exception,":",e
              if hasattr(e,"reason"):
                print e.reason
                if(e.reason[1].find("Connection refused")>-1):
                  break
              else:
                page_num-=1
            page_num += 1    
      proxies = getip.getListProxies()       