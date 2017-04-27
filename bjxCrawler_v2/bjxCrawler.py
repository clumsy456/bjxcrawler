import requests
from bs4 import BeautifulSoup
import re
import pymysql
import time
import datetime
from random import choice, randint
from userAgents import agents

IDStep = 100

urlHeads = ['news.bjx.com.cn/html/',
			'shupeidian.bjx.com.cn/html/',
			'shupeidian.bjx.com.cn/news/',
			'shoudian.bjx.com.cn/html/',
			'shoudian.bjx.com.cn/news/',
			'guangfu.bjx.com.cn/news/',
			'huanbao.bjx.com.cn/news/',
			'xinxihua.bjx.com.cn/news/',
			'www.chinasmartgrid.com.cn/news/']

conn = pymysql.connect(host='127.0.0.1', port=3306, \
	user='root', passwd='passwd', db='mysql', charset='utf8')
cur = conn.cursor()
cur.execute('USE bjx_crawler')
print('已连接数据库')

rootUrls = set()
with open('rootUrls.txt', 'r') as f:
	for line in f.readlines():
		rootUrls.add(line.strip())

with open('latestUrl.txt', 'r') as f:
	latestUrl = f.readline().strip()

finishUrls = set()

decodeErrorUrls = set()
with open('decodeErrorReading.txt', 'r') as f:
	for line in f.readlines():
		decodeErrorUrls.add(line.strip())

errorIDs = set()
with open('errorID.txt', 'r') as f:
	for line in f.readlines():
		errorIDs.add(int(line.strip()))

def addDate(date):
	dateTuple = datetime.datetime.strptime(date, '%Y%m%d')
	nextDateTuple = dateTuple + datetime.timedelta(days=1)
	nextDay = nextDateTuple.strftime('%Y%m%d')
	return nextDay

def sortUrl(urls):
	urlDict = dict()
	for url in urls:
		urlSplit = url.split('/')
		urlDict[int(urlSplit[-1][:-6])] = urlSplit[-2]
	return tuple([(k, urlDict[k]) for k in sorted(urlDict.keys())])

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
	time.sleep(randint(0,3))
	req = session.get(url, headers=headers, timeout=60)
	bsObj = BeautifulSoup(req.content.decode('gbk'), 'html5lib')
	return bsObj

def urlIsCorrect(bsObj, headType):
	if headType in (0, 3, 4, 5, 7, 8):
		if bsObj.find('span', {'class': 'sorry'}):
			return False
		else:
			return True
	elif headType in (1, 2):
		if bsObj.find('title', text='The resource cannot be found.'):
			return False
		else:
			return True
	elif headType in (6,):
		if bsObj.find('p', {'class': 'back_home'}):
			return False
		else:
			return True

def getTitle(bsObj, headType):
	if headType == 6:
		titleObj = bsObj.find('div', {'class': 'list_detail'}).find('h1') \
			or bsObj.find('div', {'class': 'details_title'}).find('h2')
	else:
		titleObj = bsObj.find('div', {'class': 'list_detail'}).find('h1')
	return titleObj.get_text().strip()

def getInfo(bsObj, headType):
	if headType == 6:
		copyObj = bsObj.find('div', {'class': 'list_copy'}) \
			or bsObj.find('p', {'class': 'article_pro'})
	else:
		copyObj = bsObj.find('div', {'class': 'list_copy'})
	copy = copyObj.get_text()
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
		elif re.match(r'^(\d+[\/-]\d+[\/-]\d+ \d+:\d+:\d+)$', info):
			editDatetime = info.split(' ')
			editDate = editDatetime[0]
			editTime = editDatetime[1]
	return source, author, editDate, editTime

def getContent(bsObj, headType):
	if headType == 6:
		contentList = bsObj.find('div', {'id': 'content'}).findAll('p') \
			or bsObj.find('div', {'class': 'details'}).findAll('p')
	else:
		contentList = bsObj.find('div', {'id': 'content'}).findAll('p')
	content = ''
	for para in contentList:
		content = content + para.get_text().strip() + '\n'
	return content

latestUrlSplit = latestUrl.split('/')
latestID = int(latestUrlSplit[-1][:-6])
latestDate = latestUrlSplit[-2]

sortedRootUrls = sortUrl(rootUrls)

print('正在加载已读内容......')
finishUrls = cache()
print('加载完毕')

num = 0
try:
	print('正在读取以下内容:')
	while num < 100:
		urlID = latestID + IDStep
		while urlID in errorIDs:
			urlID = urlID + IDStep
		print('此时ID为%d' % urlID)
		IDIsCorrect = False
		urlDate = latestDate
		upperLimitDate = datetime.date.today().strftime('%Y%m%d')
		for sortedRootUrl in sortedRootUrls:
			if urlID <= sortedRootUrl[0]:
				upperLimitDate = sortedRootUrl[1]
				break
		while urlDate <= upperLimitDate:
			dateIsCorrect = False
			for headType in range(0, len(urlHeads)):
				urlHead = urlHeads[headType]
				url = 'http://' + urlHead + urlDate + '/' + str(urlID) + '.shtml'
				if url in decodeErrorUrls:
					dateIsCorrect = True
					IDIsCorrect = True
					latestID = urlID
					latestDate = urlDate
					latestUrl = url
					print('因编码错误跳过%s' % url)
					break
				if url in finishUrls:
					dateIsCorrect = True
					IDIsCorrect = True
					latestID = urlID
					latestDate = urlDate
					latestUrl = url
					print('已存在%s' % url)
					break
				bsObj = crawl(url)
				if urlIsCorrect(bsObj, headType):
					title = getTitle(bsObj, headType)
					source, author, editDate, editTime = getInfo(bsObj, headType)
					content = getContent(bsObj, headType)
					urlPage = 1
					newBsObj = bsObj
					while newBsObj.find('a', {'title': '下一页'}):
						urlPage = urlPage + 1
						pageUrl = url[:-6] + '-%d' % urlPage + url[-6:]
						newBsObj = crawl(pageUrl)
						content = content + getContent(newBsObj, headType)
					store(url, title, source, author, editDate, editTime, content)
					finishUrls.add(url)
					dateIsCorrect = True
					IDIsCorrect = True
					latestID = urlID
					latestDate = urlDate
					latestUrl = url
					num = num + 1
					print(url + '\n' + title)
					break
			if dateIsCorrect:
				break
			else:
				print('\t\t%s' % urlDate)
				urlDate = addDate(urlDate)
		if not IDIsCorrect:
			print('ID%d读取错误' % urlID)
			print('日期区间为%s到%s' % (latestDate, upperLimitDate))
			errorIDs.add(urlID)
			with open('errorID.txt', 'a') as f:
				f.write(str(urlID) + '\n')
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
	print('最新已读取链接:')
	with open('latestUrl.txt', 'w') as f:
		f.write(latestUrl + '\n')
		print(latestUrl)