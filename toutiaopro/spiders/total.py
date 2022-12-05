from datetime import datetime

import scrapy
from selenium import webdriver
from toutiaopro.items import ToutiaoproItem
from time import sleep
from scrapy.http import HtmlResponse
import re

class TotalSpider(scrapy.Spider):
    name = 'total'
    data = '重庆银行'
    number = 2  # 控制爬取数量
    toutiaoAddress = 'https://so.toutiao.com/search?dvpf=pc&source=search_subtab_switch&keyword='
    toutiaoAddress1 = '&pd=information&action_type=search_subtab_switch&page_num=0&search_id=&from=news&cur_tab_title=news'
    hualongAddress = 'https://search.cqnews.net/search?page=1&size=10&fuzzyWord='

    start_urls = []
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
        # keywordList = self.data.replace('，', ',').split(',')
        # for keyword in keywordList:
        #     self.start_urls.append(self.toutiaoAddress+keyword+self.toutiaoAddress1)
        #     self.start_urls.append(self.hualongAddress+keyword+'&appId=1')
        self.start_urls.append('https://search.cqnews.net/search')
        self.start_urls.append('https://www.toutiao.com/')
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.bro1 = webdriver.Chrome()
        self.bro2 = webdriver.Chrome()
        self.bro3 = webdriver.Chrome()
    def start_requests(self):

        for url in self.start_urls:
            self.Q.put('开始采集信息,采集：'+url)
            yield scrapy.Request(url,callback=self.parse)

    #获取到关键字的文章列表
    def parse(self, response):
        keywordList = self.data.replace('，', ',').split(',')
        # for keyword in keywordList:
        #     self.start_urls.append(self.toutiaoAddress+keyword+self.toutiaoAddress1)
        #     self.start_urls.append(self.hualongAddress+keyword+'&appId=1')
        if(str(response.request.url).__contains__('toutiao.com')):

            for keyword in keywordList:
                tempUrl=self.toutiaoAddress + keyword + self.toutiaoAddress1
                self.bro2.get(tempUrl)
                sleep(2)
                #滑动滚动条
                self.bro2.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                sleep(2)
                temp_text = self.bro2.page_source
                temp_response = HtmlResponse(url=response.request.url, body=temp_text, encoding='utf-8',
                                            request=response.request)
                pages = temp_response.xpath('/html/body/div[2]/div[2]/div[11]/div/div/div/a//@href').extract()

                count = 1

                for page_url in pages:
                    if count>self.number:
                        break
                    count+=1
                    self.bro2.get(page_url)
                    sleep(2)
                    page_text = self.bro2.page_source
                    new_response = HtmlResponse(url=response.request.url, body=page_text, encoding='utf-8',
                                                request=response.request)
                    # 获取到列表属性
                    div_list = new_response.xpath("/html/body/div[2]/div[2]/div[@class='result-content']")
                    for div in div_list:
                        url_temp = div.xpath('./div/div/div/div//@href').extract_first()
                        #链接拼接
                        if url_temp is None:
                            continue
                        url = 'https://so.toutiao.com'+url_temp
                        yield scrapy.Request(url, callback=self.toutiao_parse_model,meta={"keyword":keyword})

        elif (str(response.request.url).__contains__('cqnews.net')):

            for keyword in keywordList:
                tempUrl=self.hualongAddress+keyword+'&appId=1'
                self.bro3.get(tempUrl)
                sleep(2)
                #滑动滚动条
                self.bro3.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                sleep(2)
                temp_text = self.bro3.page_source
                temp_response = HtmlResponse(url=response.request.url, body=temp_text, encoding='utf-8',
                                            request=response.request)

                divs_list = temp_response.xpath('//*[@id="search"]/section[2]/div')
                index = 0
                div_list = []
                for div in divs_list:
                    div_list.append(div)
                while index < self.number:
                    self.bro3.find_element("xpath", '//*[@id="search"]/div/div/button[2]').click()
                    sleep(1)
                    index += 1
                    page_text = self.bro3.page_source
                    new_response = HtmlResponse(url=temp_response.request.url, body=page_text, encoding='utf-8',
                                                request=temp_response.request)
                    divs_list = new_response.xpath('//*[@id="search"]/section[2]/div')
                    for div in divs_list:
                        div_list.append(div)
                for div in div_list:
                    temp_url = div.xpath('./a//@href').extract_first()
                    if temp_url is None:
                        continue
                    yield scrapy.Request(temp_url, callback=self.hualong_parse_model,meta={"keyword":keyword})


    #文章解析
    def toutiao_parse_model(self,response):

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
        item['source'] = '今日头条'
        item['keyword'] = response.meta['keyword']
        if (issued_date <= endDate and issued_date >= startDate):
            yield item

    def hualong_parse_model(self, response):
        # 获取到列表属性
        title = response.xpath('/html/body/div[11]/div[2]/h1/text()').extract_first()
        url = response.request.url
        time = response.xpath('/html/body/div[11]/div[2]/div[1]/span[1]/text()').extract_first()
        issued_time = ''
        try:
            mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", time)
            issued_time = mat.group(0)
        except Exception as e:
            print('解析日期异常：')
            mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", response.text)
            issued_time = mat.group(0)
            title =  response.xpath('/html/head/meta[9]//@content').extract_first()
            print('日期：'+issued_time+'title:'+title)
        issued_date = datetime.strptime(issued_time, '%Y-%m-%d')
        startDate = datetime.strptime(self.startDate, '%Y-%m-%d')
        endDate = datetime.strptime(self.endDate, '%Y-%m-%d')
        contentList = response.xpath('//*[@id="main_text"]/div[1]/p/text()').extract()
        content = ''
        # regex = re.compile(r"<[^>]+>|</[^<]+>")
        for p in contentList:
            # str=  regex.sub('',p)
            content = content + p + '\r\n'
        item = ToutiaoproItem()
        item['title'] = title
        item['content'] = content
        item['time'] = issued_time
        item['url'] = url
        item['savePath'] = self.savePath

        item['source'] = '华龙网'
        item['keyword'] = response.meta['keyword']
        if (issued_date <= endDate and issued_date >= startDate):
            yield item
    def close(spider, reason):
        spider.Q.put('采集结束')
        pass