import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
import time
from random import choice, randint
from userAgents import agents

keyword = '人口'

def crawl(url):
	session = requests.Session()
	agent = choice(agents)
	headers = {'User-Agent': agent}
	time.sleep(randint(0,3))
	req = session.get(url, headers=headers, timeout=60)
	bsObj = BeautifulSoup(req.content.decode('gbk'), 'html5lib')
	return bsObj

def getUrl(bsObj):
	newUrls = bsObj.find('ul', {'class': 'list_left_ztul'}). \
		findAll('a', href = re.compile( \
		r'^http:\/\/(([a-z]+\.bjx)|(www.chinasmartgrid))\.com\.cn\/[a-z]+\/\d+\/\d+\.shtml$'))
	if newUrls:
		for newUrl in newUrls:
			rootUrls.add(newUrl.attrs['href'])


url = 'http://news.bjx.com.cn/zt.asp?topic=' + quote(keyword, encoding='gbk') \
	+ '&page=1'
rootUrls = set()
with open('rootUrls.txt', 'r') as f:
	for line in f.readlines():
		rootUrls.add(line.strip())
try:
	print('正在生成根链接')
	bsObj = crawl(url)
	getUrl(bsObj)
	while bsObj.find('a', {'title': '下一页'}):
		page = int(url.split('page=')[1])
		page = page + 1
		print(page)
		url = url.split('page=')[0] + 'page=' + str(page)
		bsObj = crawl(url)
		if str(page) in bsObj.find('div', {'class': 'list_page'}).get_text():
			getUrl(bsObj)
		else:
			break
except Exception as e:
	print('Error:', e)
finally:
	print('共生成%d条根链接' % len(rootUrls))
	with open('rootUrls.txt', 'w') as f:
		for rootUrl in rootUrls:
			f.write(rootUrl + '\n')