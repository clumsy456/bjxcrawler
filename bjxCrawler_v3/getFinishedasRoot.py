import pymysql


conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='passwd', db='mysql', charset='utf8')
cur = conn.cursor()
cur.execute('USE bjx_crawler')
print('已连接数据库')


def cache():
    cur.execute('SELECT url FROM pages')
    results = cur.fetchall()
    cache = set()
    for result in results:
        cache.add(result[0])
    return cache


def sortUrl(urls):
    urlDict = dict()
    for url in urls:
        urlSplit = url.split('/')
        urlDict[int(urlSplit[-1][:-6])] = url
    return [urlDict[k] for k in sorted(urlDict.keys())]

try:
	finishUrls = set()
	print('正在加载已读内容........')
	finishUrls = cache()
	print('加载完毕')
	sortedFinishUrls = sortUrl(finishUrls)
	num = 0
	with open('finishRootUrls.txt', 'w') as f:
		for finishRootUrl in sortedFinishUrls:
			f.write(finishRootUrl + '\n')
			num += 1
	print('共生成%d条根链接' % num)
finally:
	cur.close()
	conn.close()
	print('已断开数据库')