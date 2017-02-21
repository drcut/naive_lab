#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import os.path

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
headers = {'User-Agent': user_agent}

def getListProxies():
    session = requests.session()
    page = session.get("http://www.xicidaili.com/nn", headers=headers)
    soup = BeautifulSoup(page.text, 'lxml')

    proxyList = []
    taglist = soup.find_all('tr', attrs={'class': re.compile("(odd)|()")})
    for trtag in taglist:
        tdlist = trtag.find_all('td')
        proxy = {'http': tdlist[1].string + ':' + tdlist[2].string,
                 'https': tdlist[1].string + ':' + tdlist[2].string}
        url = "http://ip.chinaz.com/getip.aspx"  #用来测试IP是否可用的url
        try:
            response = session.get(url, proxies=proxy, timeout=5)
            proxyList.append(proxy)
            if(len(proxyList) == 10):
                break
        except Exception, e:
            continue
    return proxyList

if __name__ == '__main__':     
    proxies = getListProxies()
    for ip in proxies:
        print ip