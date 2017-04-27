# bjxcrawler
## introduction
This is a crawler of news in the website of BEIJIXING POWER (bjx.com.cn). A MySQL database is created and used for storing the information of web pages. Based on the huge amount of text information about electrical power and energy in China and foriegn countries, one can explore the relationship between social concerns and actual industry data, by NLP and data minning.
## 介绍
这是一个收集北极星电力网 (bjx.com.cn) 上的新闻信息的爬虫程序。利用自己搭建的MySQL数据库存储网页信息。基于这些有关中国和外国的电力与能源行业的海量文本信息，可以采用自然语言处理和数据挖掘的方法，探究反映社会关注的信息与实际行业发展数据之间的关系。
## MySQL安装及创建数据库
[MySQL](https://www.mysql.com/)是一种开源的关系型数据库管理系统。采用默认步骤进行安装MySQL服务器。安装完成后，创建数据库。
利用bjxSql.sql中的语句，创建bjx_crawler数据库，并在其中创建表pages。读取内容包括url、标题、来源、作者、日期、时间、新闻内容等。
## 北极星电力网简介
[北极星电力网](www.bjx.com.cn)是中国电力行业成立最早、影响力最大的垂直门户网站。旗下包括火力发电、风力发电、太阳能光伏、电网、核电、水力发电、电力环保、电力建设、电力信息化等行业，以及电力招聘和电力论坛等。
### 参考文献
[1] R. Mitchell著. 陶俊杰, 陈小莉, 译. Python网络数据采集. 北京: 人民邮电出版社, 2016.