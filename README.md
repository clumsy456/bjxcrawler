# bjxcrawler
## Introduction
This is a crawler of news in the website of BEIJIXING POWER (bjx.com.cn). A MySQL database is created and used for storing the information of web pages. Based on the huge amount of text information about electrical power and energy in China and foriegn countries, one can explore the relationship between social concerns and actual industry data, by NLP and data minning.

## 介绍
这是一个收集北极星电力网 (bjx.com.cn) 上的新闻信息的爬虫程序。利用自己搭建的MySQL数据库存储网页信息。基于这些有关中国和外国的电力与能源行业的海量文本信息，可以采用自然语言处理和数据挖掘的方法，探究反映社会关注的信息与实际行业发展数据之间的关系。

## MySQL安装及创建数据库
[MySQL](https://www.mysql.com/)是一种开源的关系型数据库管理系统。采用默认步骤进行安装MySQL服务器。安装完成后，创建数据库。

利用[bjxSql.sql](/bjxSql.sql/)中的语句，创建bjx_crawler数据库，并在其中创建表pages。读取内容包括url、标题、来源、作者、日期、时间、新闻内容等
。
## 北极星电力网简介
[北极星电力网](www.bjx.com.cn)是中国电力行业成立最早、影响力最大的垂直门户网站。旗下包括火力发电、风力发电、太阳能光伏、电网、核电、水力发电、电力环保、电力建设、电力信息化等行业，以及电力招聘和电力论坛等。本爬虫只爬取网站上的新闻信息，不包括招聘信息以及论坛等。

举例说明北极星电力网中新闻页面的url结构。
```http://news.bjx.com.cn/html/20170427/822730.shtml```
其中`20170427`表示新闻日期，`822730`表示新闻编号。经过试验发现，对于大部分新闻，该编号与时间相关，时间越近编号越大。不妨推测所有新闻从旧到新依次编号。但是并非所有新闻页面的url前半部分均为`http://news.bjx.com.cn/html/`。经过试验发现，新闻页面的url前半部分包括以下9种：
```
http://news.bjx.com.cn/html/
http://shupeidian.bjx.com.cn/html/
http://shupeidian.bjx.com.cn/news/
http://shoudian.bjx.com.cn/html/
http://shoudian.bjx.com.cn/news/
http://guangfu.bjx.com.cn/news/
http://huanbao.bjx.com.cn/news/
http://xinxihua.bjx.com.cn/news/
http://www.chinasmartgrid.com.cn/news/
```
对于其他类型url，通常不是新闻页面，且其编号明显与以上新闻页面的编号属于不同的序列。

值得注意的是，这一编号序列可上溯到`http://news.bjx.com.cn/html/20070110/10200.shtml`，更早的新闻编号反而比此编号大，如`http://news.bjx.com.cn/20041022/48949.shtml`。这是网站建立早期管理混乱所致。

绝大部分新闻页面采用`gb2312`编码，少部分需要用`gbk`解码，极少部分编码混乱。新闻页面包括标题、新闻日期、新闻时间、新闻内容等，可能包括新闻来源和作者。当新闻内容较长时，进行分页，url也变为如`http://huanbao.bjx.com.cn/news/20170427/822697-2.shtml`所示表示第二页。

## Version1
这一版采用传统的爬虫思想，没有利用url蕴含的信息。这一版只对以`http://news.bjx.com.cn/html/`开头的新闻页面进行爬取。

采用[rootUrls.txt](/bjxCrawler_v1/rootUrls.txt/)中内容作为起始url。爬取某一新闻页面后，从中寻找符合要求的url加入待爬取的url集合中。将已爬取的url也组成一个集合，防止重复爬取。程序结束后，从待爬取的url中随机取出一部分放入[rootUrls.txt](/bjxCrawler_v1/rootUrls.txt/)中，作为下一次爬虫的起始url。

对于无法用`gbk`解码的新闻页面，将其url存入[decodeErrorReading.txt](/bjxCrawler_v1/decodeErrorReading.txt/)中，下次爬虫时进行跳过。

该方法存在一个致命缺陷。由于新闻页面为动态页面，从中获取的新的url主要为今日/本周/本月排行榜内容，因此只能爬取最近的新闻，无法爬取更早的内容。另外，该方法无法控制爬取规模，若将80多万条新闻全部爬取，将会消耗大量的时间、流量和存储空间。

## Version2
这一版没有采用爬虫的思想，而是充分利用了url中蕴含的信息。从`http://news.bjx.com.cn/html/20070110/10200.shtml`开始，采用分层抽样的思想，按照一定的步长增加编号。对于某一编号，对时间进行逐渐增加，并遍历所有的url"头"，从中得到正确的url。这一方法的好处在于可以获得早年的新闻内容，且可以通过设定步长控制爬取规模，缺点在于需要进行不断试错，效率很低。

将最新的已爬取的编号和日期存入[latestInfo.txt](/bjxCrawler_v2/latestInfo.txt/)中，作为下一次爬取的起点。第一行表示编号，第二行表示日期。

可以利用一些已知的正确url设定日期区间，提高效率。这部分内容存入[rootUrls.txt](/bjxCrawler_v2/rootUrls.txt/)中。利用新闻列表页面`http://news.bjx.com.cn/zt.asp?topic=XXXX&page=XX`。`topic`后内容为话题的`gb2312`编码，`page`表示新闻列表的页码。不利用该列表进行内容爬取的原因在于：页码存在上限，对于热门话题存在大量新闻时，无法获得早期的新闻内容；所得新闻与话题相关，不具有广泛性，也不具有随机性。

由于网站早期管理混乱，一些更早的新闻具有更大的编号，导致“日期区间”内不存在该编号。此外也存在某些新闻被删除的情况，其编号也不存在。这些错误编号放入[errorID.txt](/bjxCrawler_v2/errorID.txt/)中，下次爬虫时进行跳过。

对于无法用`gbk`解码的新闻页面，将其url存入[decodeErrorReading.txt](/bjxCrawler_v2/decodeErrorReading.txt/)中，下次爬虫时进行跳过。

## Version3
这一版基于[Version2](/bjxCrawler_v2/)，利用Version2里已读的记录作为根链接，即通过[getFinishedasRoot.py](/bjxCrawler_v3/getFinishedasRoot.py/)将已读记录存入[finishRootUrls.txt](/bjxCrawler_v3/finishRootUrls.txt/)中。对于根链接之间形成的区间，从左节点向右爬取，若连续10个ID均错误，则从右节点向左爬取，直到连续10个ID均错误或爬完整个区间。

将最新的已爬取的左ID、日期、空步，右ID、日期、空步，以及第几个区间存入[latestInfo.txt](/bjxCrawler_v3/latestInfo.txt/)中，作为下一次爬取的起点。

另外，可以对已读取的根链接进行分割，从而方便地实现多进程爬虫。

### 参考文献
[1] R. Mitchell, 著. 陶俊杰, 陈小莉, 译. Python网络数据采集. 北京: 人民邮电出版社, 2016.