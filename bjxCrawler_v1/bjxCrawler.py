import requests
from bs4 import BeautifulSoup
import re
import pymysql
import time
from random import choice, randint
from userAgents import agents

conn = pymysql.connect(host='127.0.0.1', port=3306, \
	user='root', passwd='passwd', db='mysql', charset='utf8')
cur = conn.cursor()
cur.execute('USE bjx_crawler')
print('已连接数据库')

rootUrls = []
with open('rootUrls.txt', 'r') as f:
	for line in f.readlines():
		rootUrls.append(line.strip())
crawlUrls = set(rootUrls)
finishUrls = set()
decodeErrorUrls = set()
with open('decodeErrorReading.txt', 'r') as f:
	for line in f.readlines():
		decodeErrorUrls.add(line.strip())

def cache():
	cur.execute('SELECT url FROM pages')
	results = cur.fetchall()
	cache = set()
	for result in results:
		cache.add(result[0])
	return cache

def store(url, title, source, author, editDate, editTime, content):
	cur.execute('INSERT INTO pages (url, title, source, author, edit_date, edit_time, content) VALUES (%s, %s, %s, %s, %s, %s, %s)', \
		(url, title, source, author, editDate, editTime, content))
	conn.commit()

def crawl(url):
	session = requests.Session()
	agent = choice(agents)
	headers = {'User-Agent': agent}
	time.sleep(randint(0,10))
	req = session.get(url, headers=headers, timeout=60)
	bsObj = BeautifulSoup(req.content.decode('gbk'), 'html5lib')
	return bsObj

def getInfo(bsObj):
	copy = bsObj.find('div', {'class': 'list_copy'}).get_text()
	infos = copy.split('\xa0')
	source = ''
	author = ''
	editDate = ''
	editTime = ''
	for info in infos:
		if info.startswith('来源:'):
			source = info[3:]
		elif info.startswith('作者:'):
			author = info[3:]
		elif re.match(r'^(\d+\/\d+\/\d+ \d+:\d+:\d+)$', info):
			editDatetime = info.split(' ')
			editDate = editDatetime[0]
			editTime = editDatetime[1]
	return source, author, editDate, editTime

def getContent(bsObj):
	contentList = bsObj.find('div', {'id': 'content'}).findAll('p')
	content = ''
	for para in contentList:
		content = content + para.get_text().strip() + '\n'
	return content

print('正在加载已读内容........')
finishUrls = cache()
print('加载完毕')
num = 0
try:
	print('正在读取以下内容:')
	while crawlUrls and num < 300:
		url = crawlUrls.pop()
		finishUrls.add(url)
		if url in decodeErrorUrls:
			continue
		bsObj = crawl(url)
		title = bsObj.find('h1').get_text().strip()
		source, author, editDate, editTime = getInfo(bsObj)
		content = getContent(bsObj)
		page = 1
		newBsObj = bsObj
		while newBsObj.find('a', {'title': '下一页'}):
			page = page + 1
			pageUrl = url[:-6] + '-%d' % page + url[-6:]
			newBsObj = crawl(pageUrl)
			content = content + getContent(newBsObj)
		store(url, title, source, author, editDate, editTime, content)
		num = num + 1
		print(url + '\n' + title)
		newUrls = bsObj.findAll('a', href = re.compile( \
			r'^http:\/\/news\.bjx\.com\.cn\/html\/\d+\/\d+\.shtml$'))
		if newUrls:
			for newUrl in newUrls:
				if newUrl.attrs['href'] not in finishUrls:
					crawlUrls.add(newUrl.attrs['href'])
except UnicodeDecodeError as e:
	with open('decodeErrorReading.txt', 'a') as f:
		f.write(url + '\n')
	print('编码错误' + url)
	print('Error:', e)
except Exception as e:
	print('读取错误' + url)
	print('Error:', e)
finally:
	cur.close()
	conn.close()
	print('已断开数据库')
	print('本次共读取%d条' % num)
	print('生成新的根链接:')
	with open('rootUrls.txt', 'w') as f:
		newRootUrls = list(crawlUrls)
		for i in range(0,50):
			newRootUrl = choice(newRootUrls)
			f.write(newRootUrl + '\n')
			print(newRootUrl)