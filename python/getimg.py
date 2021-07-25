import os
import time
import urllib.error
import urllib.request

from bs4 import BeautifulSoup

url = 'https://news.yahoo.co.jp/list/'
ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '\
     'AppleWebKit/537.36 (KHTML, like Gecko) '\
     'Chrome/55.0.2883.95 Safari/537.36 '

req = urllib.request.Request(url, headers={'User-Agent': ua})
html = urllib.request.urlopen(req)

soup = BeautifulSoup(html, "html.parser")

url_list = [img.get('data-src') for img in soup.find(class_='list').find_all('img')]