import scrapy
from selenium import webdriver
from toutiaopro.items import ToutiaoproItem
import re
from scrapy.http import HtmlResponse
from time import sleep

class JuchaoSpider(scrapy.Spider):
    name = 'xinhua'
    data = '重庆银行'
    number = 3  # 控制爬取数量
    address = 'http://so.news.cn/#search/0/'+data+'/1/'
    start_urls = [address]
    urls = []
    num = 0 #控制浏览器下滑循环次数
    index = 0 #控制收集连接条数
    path = r'D:\PyCharm\workplace\toutiaopro\venv\Scripts\chromedriver.exe'

    #初始化浏览器
    def __init__(self):
        #根据自己的chrome驱动路径设置

        self.bro1 = webdriver.Chrome(executable_path=self.path)
        self.bro2 = webdriver.Chrome(executable_path=self.path)



    #获取到关键字的文章列表
    def parse(self, response):
        # 获取到列表属性
        bro3 = webdriver.Chrome(executable_path=self.path)
        bro3.get(response.request.url)
        sleep(2)
        bro3.find_element("xpath",'//*[@id="radioAll"]').click()
        sleep(2)
        page_text = bro3.page_source
        new_response = HtmlResponse(url=response.request.url, body=page_text, encoding='utf-8',request=response.request)
        divs_list = new_response.xpath('//*[@id="newsCon"]/div[2]/div')
        div_list = []
        for div in divs_list:
            div_list.append(div)
        while self.index <self.number:
            temp = new_response.xpath('//*[@id="pagination"]/a')
            bro3.find_element("xpath", '//*[@id="pagination"]/a[10]').click()
            # bro3.execute_script('''document.getElementById('//*[@id="pagination"]/a[11]').click()''')
            sleep(2)
            self.index+=1
            page_text = bro3.page_source
            new_response = HtmlResponse(url=response.request.url, body=page_text, encoding='utf-8',request=response.request)
            divs_list = new_response.xpath('//*[@id="newsCon"]/div[2]/div')
            for div in divs_list:
                div_list.append(div)
        for div in div_list:
            temp_url = div.xpath('./h2//@href').extract_first()
            if temp_url is None:
                continue
            yield scrapy.Request(temp_url, callback=self.parse_model)





    #文章解析
    def parse_model(self,response):
        # 获取到列表属性
        title = response.xpath('/html/body/div[5]/div[1]/div[1]/text()').extract_first()
        url = response.request.url
        time = response.xpath('/html/body/div[5]/div[1]/div[2]/div[1]/text()').extract_first()
        contentList = response.xpath('//*[@id="content"]/p/text()').extract()
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



