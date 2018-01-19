import requests
from bs4 import BeautifulSoup
import re
import pymysql
import time
import datetime
from random import choice, randint
from userAgents import agents

urlHeads = ['news.bjx.com.cn/html/',
            'shupeidian.bjx.com.cn/html/',
            'shupeidian.bjx.com.cn/news/',
            'shoudian.bjx.com.cn/html/',
            'shoudian.bjx.com.cn/news/',
            'guangfu.bjx.com.cn/news/',
            'huanbao.bjx.com.cn/news/',
            'xinxihua.bjx.com.cn/news/',
            'www.chinasmartgrid.com.cn/news/']

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='passwd', db='mysql', charset='utf8')

cur = conn.cursor()
cur.execute('USE bjx_crawler')
print('已连接数据库')

rootUrls = list()
with open('finishRootUrls.txt', 'r') as f:
    for line in f.readlines():
        rootUrls.append(line.strip())


with open('latestInfo.txt', 'r') as f:
    latestIDLeft = int(f.readline().strip())
    latestDateLeft = f.readline().strip()
    emptyStepLeft = int(f.readline().strip())
    latestIDRight = int(f.readline().strip())
    latestDateRight = f.readline().strip()
    emptyStepRight = int(f.readline().strip())
    latestRangeID = int(f.readline().strip())


decodeErrorUrls = set()
with open('../decodeErrorReading.txt', 'r') as f:
    for line in f.readlines():
        decodeErrorUrls.add(line.strip())


errorIDs = set()
with open('../errorID.txt', 'r') as f:
    for line in f.readlines():
        errorIDs.add(int(line.strip()))


def rangeGen(rootUrls, latestRangeID):
    leftInfo = rootUrls[latestRangeID].split('/')
    leftID = int(leftInfo[-1][:-6])
    leftDate = leftInfo[-2]
    rightInfo = rootUrls[latestRangeID+1].split('/')
    rightID = int(rightInfo[-1][:-6])
    rightDate = rightInfo[-2]
    return leftID, leftDate, rightID, rightDate


def addDate(date):
    dateTuple = datetime.datetime.strptime(date, '%Y%m%d')
    nextDateTuple = dateTuple + datetime.timedelta(days=1)
    nextDay = nextDateTuple.strftime('%Y%m%d')
    return nextDay


def minusDate(date):
    dateTuple = datetime.datetime.strptime(date, '%Y%m%d')
    formerDateTuple = dateTuple - datetime.timedelta(days=1)
    formerDay = formerDateTuple.strftime('%Y%m%d')
    return formerDay


def store(url, title, source, author, editDate, editTime, content):
    cur.execute('INSERT INTO pages (url, title, source, author, edit_date, edit_time, content) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (url, title, source, author, editDate, editTime, content))
    conn.commit()


def crawl(url):
    session = requests.Session()
    agent = choice(agents)
    headers = {'User-Agent': agent}
    time.sleep(randint(0, 3))
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
        if bsObj.find('div', {'class': 'list_detail'}):
            titleObj = bsObj.find('div', {'class': 'list_detail'}).find('h1')
        elif bsObj.find('div', {'class': 'hdm_left_content'}):
            titleObj = bsObj.find(
                'div', {'class': 'hdm_left_content'}).find('h1')
        elif bsObj.find('div', {'class': 'details_title'}):
            titleObj = bsObj.find('div', {'class': 'details_title'}).find('h2')
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
        contentListObj = bsObj.find('div', {'id': 'content'}) \
            or bsObj.find('div', {'class': 'hdm_left_content'}) \
            or bsObj.find('div', {'class': 'details'})
        contentList = contentListObj.findAll('p')
    else:
        contentList = bsObj.find('div', {'id': 'content'}).findAll('p')
    content = ''
    for para in contentList:
        content = content + para.get_text().strip() + '\n'
    return content


def IDIsCorrect(urlID, lowerDate, upperDate, direction):
    print('此时ID为%d' % urlID)
    if urlID in errorIDs:
        print('此ID已在errorID内')
        return False
    if direction == 0:
        urlDate = lowerDate
    else:
        urlDate = upperDate
    while urlDate <= upperDate and urlDate >= lowerDate:
        for headType in range(len(urlHeads)):
            urlHead = urlHeads[headType]
            url = 'http://' + urlHead + urlDate + '/' + str(urlID) + '.shtml'
            urlState[0] = url
            if url in decodeErrorUrls:
                print('因编码错误跳过%s' % url)
                return urlDate
            bsObj = crawl(url)
            if urlIsCorrect(bsObj, headType):
                title = getTitle(bsObj, headType)
                source, author, editDate, editTime = getInfo(bsObj, headType)
                content = getContent(bsObj, headType)
                urlPage = 1
                newBsObj = bsObj
                while newBsObj.find('a', {'title': '下一页'}):
                    urlPage += 1
                    pageUrl = url[:-6] + '-%d' % urlPage + url[-6:]
                    newBsObj = crawl(pageUrl)
                    content += getContent(newBsObj, headType)
                if len(content) >= 21000:
                    content = content[0:21000]
                store(url, title, source, author, editDate, editTime, content)
                print(url + '\n' + title)
                return urlDate
        print('\t\t%s' % urlDate)
        if direction == 0:
            urlDate = addDate(urlDate)
        else:
            urlDate = minusDate(urlDate)
    print('ID%d读取错误' % urlID)
    print('日期区间为%s到%s' % (lowerDate, upperDate))
    with open('../errorID.txt', 'a') as f:
        f.write(str(urlID) + '\n')
    return False


num = 0
urlState = [':(']
'''
因为把读取内容封装到了IDIsCorrect函数中，导致url是该函数的局部变量，
导致无法实现错误处理。
所以定义一个urlState的list，只包含一个元素，即当前url。
list数据类型可以在函数内进行改变。
'''
try:
    print('正在读取以下内容:')
    while True:
        while emptyStepLeft < 10:
            testIDLeft = latestIDLeft + emptyStepLeft + 1
            if testIDLeft < latestIDRight - emptyStepRight:
                urlDate = IDIsCorrect(testIDLeft, latestDateLeft, latestDateRight, 0)
                if urlDate:
                    latestIDLeft = testIDLeft
                    latestDateLeft = urlDate
                    emptyStepLeft = 0
                    num += 1
                else:
                    emptyStepLeft += 1
            else:
                latestRangeID += 1
                latestIDLeft, latestDateLeft, latestIDRight, latestDateRight = rangeGen(rootUrls, latestRangeID)
                emptyStepLeft = 0
                emptyStepRight = 0
                print('更新url区间为:%s/%d-%s/%d' % (latestDateLeft, latestIDLeft, latestDateRight, latestIDRight))
        while emptyStepRight < 10:
            testIDRight = latestIDRight - emptyStepRight - 1
            if testIDRight > latestIDLeft + emptyStepLeft:
                urlDate = IDIsCorrect(testIDRight, latestDateLeft, latestDateRight, 1)
                if urlDate:
                    latestIDRight = testIDRight
                    latestDateRight = urlDate
                    emptyStepRight = 0
                    num += 1
                else:
                    emptyStepRight -= 1
            else:
                latestRangeID += 1
                latestIDLeft, latestDateLeft, latestIDRight, latestDateRight = rangeGen(rootUrls, latestRangeID)
                emptyStepLeft = 0
                emptyStepRight = 0
                print('更新url区间为:%s/%d-%s/%d' % (latestDateLeft, latestIDLeft, latestDateRight, latestIDRight))

except UnicodeDecodeError as e:
    with open('../decodeErrorReading.txt', 'a') as f:
        f.write(urlState[0] + '\n')
    print('编码错误' + urlState[0])
    print('Error:', e)
except Exception as e:
    print('读取错误' + urlState[0])
    print('Error:', e)
finally:
    cur.close()
    conn.close()
    print('已断开数据库')
    print('本次共读取%d条' % num)
    print('最新已读ID及日期:')
    print(latestDateLeft + '/' + str(latestIDLeft) + '---' + latestDateRight + '/' + str(latestIDRight))
    print('最新范围:')
    print(rootUrls[latestRangeID] + '\n' + rootUrls[latestRangeID+1])
    with open('latestInfo.txt', 'w') as f:
        f.write(str(latestIDLeft) + '\n')
        f.write(latestDateLeft + '\n')
        f.write(str(emptyStepLeft) + '\n')
        f.write(str(latestIDRight) + '\n')
        f.write(latestDateRight + '\n')
        f.write(str(emptyStepRight) + '\n')
        f.write(str(latestRangeID) + '\n')