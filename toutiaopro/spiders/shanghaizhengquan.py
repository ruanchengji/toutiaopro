
import scrapy
from selenium import webdriver
from toutiaopro.items import ToutiaoproItem
import re
from scrapy.http import HtmlResponse
from time import sleep
from datetime import datetime

class ShangHaiZhengQuanSpider(scrapy.Spider):
    name = 'shanghaizhengquan'
    data = '重庆银行'
    number = 3  # 控制爬取数量
    address = 'http://www.sse.com.cn/home/search/?webswd='
    start_urls = [address]
    urls = []
    num = 0 #控制浏览器下滑循环次数
    index = 0 #控制收集连接条数
    path = r'D:\PyCharm\workplace\toutiaopro\venv\Scripts\chromedriver.exe'
    Q = None

    #初始化浏览器
    def __init__(self,Q,data,savePath,startDate,endDate,num):
        #根据自己的chrome驱动路径设置
        self.Q = Q
        self.data = data
        self.savePath = savePath
        self.startDate = startDate
        self.endDate = endDate
        self.number = num
        self.start_urls = [self.address+data]
        self.bro1 = webdriver.Chrome(executable_path=self.path)
        self.bro2 = webdriver.Chrome(executable_path=self.path)


    def start_requests(self):

        for url in self.start_urls:
            self.Q.put('开始采集上海证券交易所信息,采集：'+url)
            yield scrapy.Request(url,callback=self.parse)
    #获取到关键字的文章列表
    def parse(self, response):
        # 获取到列表属性
        self.bro1.find_element('xpath','//*[@id="tab-main0"]/div[1]/div[1]/div/div/div/div/div/div[1]/div[2]/span').click()
        sleep(2)
        page_text = self.bro1.page_source
        response = HtmlResponse(url=response.request.url, body=page_text, encoding='utf-8',request=response.request)
        divs_list = response.xpath('//*[@id="tab-main0"]/div[1]/div[4]/ul/li')


        div_list = []
        for div in divs_list:
            div_list.append(div)
        while self.index <self.number:

            js = response.xpath('//*[@id="tab-main0"]/div[1]/div[4]/div/ul/li[7]/a//@href').extract_first()
            temp = self.bro1.find_element('xpath','//*[@id="tab-main0"]/div[1]/div[4]/div/ul/li[7]/a')

            self.bro1.execute_script("arguments[0].click();",temp)

            sleep(2)
            self.index+=1
            page_text = self.bro1.page_source
            new_response = HtmlResponse(url=response.request.url, body=page_text, encoding='utf-8',request=response.request)
            divs_list = new_response.xpath('//*[@id="tab-main0"]/div[1]/div[4]/ul/li')
            for div in divs_list:
                div_list.append(div)
        for div in div_list:
            url = div.xpath('./div[1]/a//@href').extract_first()
            titlelist = div.xpath('./div/a/text()').extract()
            time = div.xpath('./span/text()').extract_first()
            mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", time)
            issued_time = mat.group(0)
            issued_date = datetime.strptime(issued_time,'%Y-%m-%d')
            startDate = datetime.strptime(self.startDate, '%Y-%m-%d')
            endDate = datetime.strptime(self.endDate, '%Y-%m-%d')
            content = div.xpath('./div[2]/text()').extract_first()
            title = ''
            for str in titlelist:
                title += str

            item = ToutiaoproItem()
            item['title'] = title
            item['content'] = content
            item['time'] = issued_time
            item['url'] = url
            item['savePath'] = self.savePath
            if(issued_date<=endDate and issued_date>= startDate):
                yield item





    #文章解析
    def parse_model(self,response):
        # 获取到列表属性
        title = response.xpath('/html/body/div[11]/div[2]/h1/text()').extract_first()
        url = response.request.url
        time = response.xpath('/html/body/div[11]/div[2]/div[1]/span[1]/text()').extract_first()
        contentList = response.xpath('//*[@id="main_text"]/div[1]/p/text()').extract()
        content = ''
        # regex = re.compile(r"<[^>]+>|</[^<]+>")
        for p in contentList:
            # str=  regex.sub('',p)
            content=content+p+'\r\n'
        item = ToutiaoproItem()
        item['title'] = title
        item['content'] = content
        item['time'] = time
        item['url'] = url

        yield item

    def close(spider, reason):
        spider.Q.put('采集结束')
        pass

