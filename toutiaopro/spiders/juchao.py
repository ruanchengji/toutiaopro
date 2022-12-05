import scrapy
from selenium import webdriver
from toutiaopro.items import ToutiaoproItem
import re
from scrapy.http import HtmlResponse
from time import sleep

class JuchaoSpider(scrapy.Spider):
    name = 'juchao'
    data = '重庆银行'
    number = 3  # 控制爬取数量
    address = 'http://www.cninfo.com.cn/new/fulltextSearch?notautosubmit=&keyWord='+data
    start_urls = [address]
    div_list = []
    urls = []
    num = 0 #控制浏览器下滑循环次数
    index = 0 #控制收集连接条数


    #初始化浏览器
    def __init__(self):
        #根据自己的chrome驱动路径设置
        path = r'D:\PyCharm\workplace\toutiaopro\venv\Scripts\chromedriver.exe'
        self.bro1 = webdriver.Chrome(executable_path=path)
        self.bro2 = webdriver.Chrome(executable_path=path)


    #获取到关键字的文章列表
    def parse(self, response):
        # 获取到列表属性
        div_list1 = response.xpath('//*[@id="fulltext-search"]/div/div[1]/div[2]/div[4]/div[1]/div/div[3]/table/tbody/tr')
        for div in div_list1:
            self.div_list.append(div)
        response_list = []
        response_list.append(response)
        ########
        # 获取每篇文章
        # for div in div_list:
        #     url_temp = div.xpath('./div/div/div/div/div//@href').extract_first()
        #     url = 'https://www.toutiao.com/a'+url_temp.split('/',3)[2]
        #     self.urls.append(url)
        # for href in self.urls:
        #     yield scrapy.Request(href,callback=self.parse_model)
        ##############
        # 控制爬取数量
        while self.index < self.number:
            # for href in self.urls:
            #     yield scrapy.Request(href, callback=self.parse_model)
            index = self.index
            self.bro1.find_element("xpath",'//*[@id="fulltext-search"]/div/div[1]/div[2]/div[4]/div[2]/div/button[2]').click()
            sleep(2)
            page_text = self.bro1.page_source
            new_response = HtmlResponse(url=response.request.url, body=page_text, encoding='utf-8', request=response.request)
            # div_list1 =  self.bro1.find_element("xpath",'//*[@id="fulltext-search"]/div/div[1]/div[2]/div[4]/div[1]/div/div[3]/table/tbody/tr')
            self.index += 1
            div_list1 = new_response.xpath('//*[@id="fulltext-search"]/div/div[1]/div[2]/div[4]/div[1]/div/div[3]/table/tbody/tr')
            for div in div_list1:
                self.div_list.append(div)
        for div in self.div_list:
            url = div.xpath('./td[2]/div/a//@href').extract_first()
            title = div.xpath('./td[2]/div/a/span[1]/text()').extract_first()
            time = div.xpath('./td[3]/div/span/text()').extract_first()
            content = ''
            item = ToutiaoproItem()
            item['title'] = title
            item['content'] = content
            item['time'] = time
            item['url'] = 'http://www.cninfo.com.cn' + url
            print("--------")
            print(url)
            print("---------")
            yield item




    #文章解析
    def parse_model(self,response):
        # 获取到列表属性
        div_list = response.xpath('//*[@id="fulltext-search"]/div/div[1]/div[2]/div[4]/div[1]/div/div[3]/table/tbody/tr')
        ########
        # 获取每篇文章
        # for div in div_list:
        #     url_temp = div.xpath('./div/div/div/div/div//@href').extract_first()
        #     url = 'https://www.toutiao.com/a'+url_temp.split('/',3)[2]
        #     self.urls.append(url)
        # for href in self.urls:
        #     yield scrapy.Request(href,callback=self.parse_model)
        ##############

        for div in div_list:
            url = div.xpath('./td[2]/div/a//@href').extract_first()
            title = div.xpath('./td[2]/div/a/span[1]/text()').extract_first()
            time = div.xpath('./td[3]/div/span/text()').extract_first()
            content = ''
            item = ToutiaoproItem()
            item['title'] = title
            item['content'] = content
            item['time'] = time
            item['url'] = 'http://www.cninfo.com.cn' + url
            print("--------")
            print(url)
            print("---------")
            yield item


