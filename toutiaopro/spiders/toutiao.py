from datetime import datetime

import scrapy
from selenium import webdriver
from toutiaopro.items import ToutiaoproItem
from time import sleep
from scrapy.http import HtmlResponse
import re

class ToutiaoSpider(scrapy.Spider):
    name = 'toutiao'
    data = '重庆银行'
    number = 2  # 控制爬取数量
    address = 'https://so.toutiao.com/search?dvpf=pc&source=search_subtab_switch&keyword='
    address1 = '&pd=information&action_type=search_subtab_switch&page_num=0&search_id=&from=news&cur_tab_title=news'

    start_urls = [address]
    urls = []
    num = 0 #控制浏览器下滑循环次数
    index = 0 #控制收集连接条数
    path = r'D:\PyCharm\workplace\toutiaopro\venv\Scripts\chromedriver.exe'

    #初始化浏览器
    #初始化浏览器
    def __init__(self,Q,data,savePath,startDate,endDate,num):
        #根据自己的chrome驱动路径设置
        self.Q = Q
        self.data = data
        self.savePath = savePath
        self.startDate = startDate
        self.endDate = endDate
        self.number = num
        self.start_urls = [self.address+data+self.address1]
        self.bro1 = webdriver.Chrome(executable_path=self.path)
        self.bro2 = webdriver.Chrome(executable_path=self.path)
    def start_requests(self):

        for url in self.start_urls:
            self.Q.put('开始采集今日头条信息,采集：'+url)
            yield scrapy.Request(url,callback=self.parse)

    #获取到关键字的文章列表
    def parse(self, response):
        #获取到列表属性
        div_list = response.xpath("/html/body/div[2]/div[2]/div[@class='result-content']")
        ########
        #获取每篇文章
        # for div in div_list:
        #     url_temp = div.xpath('./div/div/div/div/div//@href').extract_first()
        #     url = 'https://www.toutiao.com/a'+url_temp.split('/',3)[2]
        #     self.urls.append(url)
        # for href in self.urls:
        #     yield scrapy.Request(href,callback=self.parse_model)
        ##############

        for div in div_list:
            url_temp = div.xpath('./div/div/div/div//@href').extract_first()
            #链接拼接
            if url_temp is None:
                continue
            url = 'https://so.toutiao.com'+url_temp
            self.urls.append(url)
            print("--------")
            print(url)
            print("---------")

        #控制爬取数量
        while self.index<self.number:
            # for href in self.urls:
            #     yield scrapy.Request(href, callback=self.parse_model)
            index = self.index
            yield scrapy.Request(self.urls[index], callback=self.parse_model)

            #获取10篇文章后刷新文章列表
            #有些关键字一页若没有这个数，则需调低阈值
            if self.num == 5:
                #滑动滚动条
                self.bro1.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                sleep(5)
                page_text = self.bro1.page_source
                print("if里面")
                #print(page_text)

                new_response = HtmlResponse(url='',body=page_text,encoding='utf-8', request='')
                # self.artical_list(page_text)
                self.artical_list(new_response)
                self.num = 0
                self.index = self.index + 1
                print("if中的index", self.index)
            else:
                print("else里面",self.num)
                self.index = self.index + 1
                print("else中的index",self.index)
                self.num = self.num + 1
    #文章解析
    def parse_model(self,response):

        title = response.xpath('//*[@id="root"]/div[2]/div[2]/div[1]/div/div/div/div/h1/text()').extract_first()
        contentList = response.xpath('//*[@id="root"]/div[2]/div[2]/div[1]/div/div/div/div/article/p').extract()
        content = ''
        regex = re.compile(r"<[^>]+>|</[^<]+>")
        for p in contentList:
            str=  regex.sub('',p)
            content=content+str+'\r\n'
        times = response.xpath('//*[@id="root"]/div[2]/div[2]/div[1]/div/div/div/div/div/span').extract()
        time=''
        for str in times:
            time+=str
        mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", time)
        issued_time = mat.group(0)
        issued_date = datetime.strptime(issued_time, '%Y-%m-%d')
        startDate = datetime.strptime(self.startDate, '%Y-%m-%d')
        endDate = datetime.strptime(self.endDate, '%Y-%m-%d')
        url = response.request.url
        # if len(span) == 2:
        #     author = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[1]/text()').extract_first()
        #     time = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[2]/text()').extract_first()
        # else:
        #     author = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[2]/text()').extract_first()
        #     time = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[3]/text()').extract_first()

        #提交管道
        #self.bro1.excute_script('window.scrollTo(0, document.body.scrollHeight)')
        item = ToutiaoproItem()
        item['title'] = title
        item['content'] = content
        item['time'] = issued_time
        item['url'] = url
        item['savePath'] = self.savePath
        if (issued_date <= endDate and issued_date >= startDate):
            yield item


    #列表解析
    def artical_list(self,new_response):
        # 获取到列表属性
        div_list = new_response.xpath('/html/body/div/div[4]/div[2]/div[3]/div/div/div')
        num_urls = len(self.urls)
        num_div = len(div_list)
        for div in range(num_urls,num_div):
            href_temp = div_list[div].xpath('./div/div/div/div/div//@href').extract_first()
            href_temp = 'https://www.toutiao.com/a'+href_temp.split('/',3)[2]
            self.urls.append(href_temp)
            print("!!!!!!!!!!!!!")
            print(href_temp)
            print("!!!!!!!!!!!!")
    def close(spider, reason):
        spider.Q.put('采集结束')
        pass