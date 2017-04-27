# bjxcrawler
## introduction
This is a crawler of news in the website of BEIJIXING POWER (bjx.com.cn). A MySQL database is created and used for storing the information of web pages. Based on the huge amount of text information about electrical power and energy in China and foriegn countries, one can explore the relationship between social concerns and actual industry data, by NLP and data minning.

## 介绍
这是一个收集北极星电力网 (bjx.com.cn) 上的新闻信息的爬虫程序。利用自己搭建的MySQL数据库存储网页信息。基于这些有关中国和外国的电力与能源行业的海量文本信息，可以采用自然语言处理和数据挖掘的方法，探究反映社会关注的信息与实际行业发展数据之间的关系。

## MySQL安装及创建数据库
[MySQL](https://www.mysql.com/)是一种开源的关系型数据库管理系统。采用默认步骤进行安装MySQL服务器。安装完成后，创建数据库。

利用bjxSql.sql中的语句，创建bjx_crawler数据库，并在其中创建表pages。读取内容包括url、标题、来源、作者、日期、时间、新闻内容等
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

新闻页面包括标题、新闻日期、新闻时间、新闻内容等，可能包括新闻来源和作者。当新闻内容较长时，进行分页，url也变为如`http://huanbao.bjx.com.cn/news/20170427/822697-2.shtml`所示表示第二页。

## Version1
这一版采用传统的爬虫思想，没有利用url蕴含的信息。这一版只对以`http://news.bjx.com.cn/html/`开头的新闻页面进行爬取。爬取某一新闻页面后，从中寻找符合要求的url加入待爬取的url集合中。将已爬取的url也组成一个集合，防止重复爬取。

该方法存在一个致命缺陷。由于新闻页面为动态页面，从中获取的新的url主要为今日/本周/本月排行榜内容，因此只能爬取最近的新闻，无法爬取更早的内容。另外，该方法无法控制爬取规模，若将80多万条新闻全部爬取，将会消耗大量的时间和流量。

## Version2
这一版没有采用爬虫的思想，而是充分利用了url中蕴含的信息。

### 参考文献
[1] R. Mitchell, 著. 陶俊杰, 陈小莉, 译. Python网络数据采集. 北京: 人民邮电出版社, 2016.