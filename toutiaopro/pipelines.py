# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

import xlrd
import xlwt
from xlutils.copy import copy
import time



class ToutiaoproPipeline:
    def process_item(self, item, spider):
        # path = r"D:\PyCharm\workplace\toutiaopro"
        times =time.time()
        localtime = time.localtime(times)
        dateStr = time.strftime('%Y%m%d',localtime)
        path = os.getcwd()
        path = path.replace('\\', '/')

        title = item['title']
        print(title)
        content = item['content']
        print(content)
        xls = None
        try:
            #doc = Document(path+"\info.docx")  # 读取现有的word 建立文档对象
            wb = xlrd.open_workbook(path+"\Info+"+dateStr+".xls", formatting_info=True)
            xls = copy(wb)
        except Exception as e:
            print('创建文档异常：',e)
            xls = xlwt.Workbook()
            xls.add_sheet('第一个sheet')

        # doc.add_heading(title)
        # doc.add_paragraph(content)
        sheet = xls.get_sheet('第一个sheet')
        rows = sheet.get_rows()
        length = len(rows)

        sheet.write(length, 0, title)
        sheet.write(length, 1, content)
        sheet.write(length, 2, item['time'])
        sheet.write(length, 3, item['url'])
        sheet.write(length, 4, item['source'])
        sheet.write(length,5,item['keyword'])
        sheet.write(length,6,item['savePath'])


        # doc.save(path+"\info.docx")
        xls.save(path+"/Info+"+dateStr+".xls")

        return item

class mysqlPipeLine(object):
    # conn = None
    # cursor = None
    # def open_spider(self,spider):
    #     self.conn = pymysql.Connect(host='MYSQL地址',port=3306,user='账号',password='密码',db='python',charset='utf8')
    # def process_item(self,item,spider):

    #     self.cursor = self.conn.cursor()
    #     try:
    #         tiele = item['title']
    #         print(tiele)
    #         self.cursor.execute('insert into toutiao (title,content,time,author) values("%s","%s","%s","%s")'%(item["title"],item["content"],item["time"],item["author"]))
    #         self.conn.commit()
    #     except Exception as e:
    #         print(e)
    #         self.conn.rollback()
    #     return item

    def close_spider(self,spider):

        times = time.time()
        localtime = time.localtime(times)
        dateStr = time.strftime('%Y%m%d', localtime)
        savePath = ''
        path = os.getcwd()
        path = path.replace('\\', '/')

        wb1 = xlrd.open_workbook(path +'/setting_user.xls', formatting_info=True)
        sheet1 = wb1.sheet_by_name('sheet1')
        savePath = sheet1.cell_value(1,0)
        keywords = sheet1.cell_value(0,0)
        wb1.release_resources()
        wb = xlrd.open_workbook(path + "/Info+" + dateStr + ".xls", formatting_info=True)
        sheet = wb.sheet_by_name('第一个sheet')
        length = sheet.nrows
        keywordList = keywords.replace('，', ',').split(',')
        content = ''
        html_body = '<body><div id="container" style=""><div id="header" class="header-wrap"><img src="./files/logo-touhang.png" alt="test"><h4><strong>信息聚合发布</strong></h4></div><div id="content" style=""><a class="current" id="date_announcement" style="text-align:left;">更新日期：{0}</a><div class="page-list" id="test">{1}</div></div><div style="background-color:#FFA500;clear:both;text-align:center;">技术支持 © </div></div></body></html>'
        html_head = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>发布信息聚合</title><style type="text/css">#container{margin-left:10%;margin-right:10%;text-align:center;}em{font-style:normal;color:#c00}li a:hover:not(.active) {    background-color: #555;    color: white;}li a {    display: block;    color: #000;    padding: 8px 16px;    text-decoration: none;}img {max-width:100%;}.page-list{ padding: 10px 0px; }.page-list-header{ width: 100%; table-layout: auto; /*fixed*/ background-color: #f7f7f7; color: #666666; }.page-list-header:hover{ background-color: #f1f6fa; }.page-list-header td{ height: 40px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.page-list-header tr td:first-child{ padding-left: 50px; text-align: left; }.page-list-header tr td.last-child{ padding-right: 50px; text-align: right; }.page-list-header .sub-title{ width: 250px; font-size: 18px; color: #333333; }.page-list-header .sub-name{ width: 150px; font-size: 18px; color: #333333; }.page-list-header .sub-code{ width: 80px; text-align: right; }.page-list-header .sub-info{ width: auto; text-align: center; }.page-list-header .sub-info a,.page-list-header .sub-info span{ display: inline-block; padding: 0px 5px; color: #333; }.page-list-header .sub-count{ width: 230px; text-align: right; }.page-list-list{ width: 100%;margin: 10px;table-layout: auto; /*fixed*/ color: #666666; }.page-list-list.page-list-list-auto{ table-layout: auto; }.page-list-list.page-list-list-color th{ background-color: #2fb5f4; color: #fff; font-weight: normal; }.page-list-list p{ margin: 2px 0px; }.page-list-list tr:hover{ background-color: #f1f6fa; color: #232323;}.page-list-list tr.sub-none-hover:hover{ background: none;height:10px }.page-list-list.page-list-listsummary tr:hover{ background: none;height:10px }.page-list-list td,.page-list-list th{ padding: 5px;height:10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;    box-sizing: content-box; position: relative; }.page-list-list tr th:first-child,.page-list-list tr td:first-child{ padding-left: 50px; text-align: left; }.page-list-list tr th.last-child,.page-list-list tr td.last-child{ padding-right: 50px; text-align: right; }.page-list-list th{ background-color: #f2f2f2;height:44px; }.page-list-list .sub-break{ overflow: visible; white-space: normal; padding: 8px 5px; line-height: 20px; }.page-list-list .sub-center{ text-align: center !important; }.page-list-list .sub-right{ text-align: right !important; }.page-list-list .sub-hidden{ display: none; }.page-list-list .sub-no{ width: 80px; }.page-list-list .sub-code{ width: 80px; }.page-list-list .sub-name{ width: 80px; }.page-list-list .sub-title,.page-list-list .sub-value{ width: auto; white-space: normal; line-height:22px;}.page-list-list .sub-title i{ margin: 0px 2px; font-size: 28px; line-height: 18px; vertical-align: bottom; }.page-list-list .sub-title img {margin-left: 4px; margin-right: 4px;}.page-list-list th.sub-title i{ font-size: 18px; color: #ff1100; }.page-list-list .sub-date{ width: 100px; text-align: right; }.page-list-list .sub-time{ width: 180px; text-align: right; }.page-list-list .sub-time-share{ display: none; line-height: 20px; }.page-list-list .sub-time-share a{ display: inline-block; margin: 0px 5px; }.page-list-list .sub-time-share a i{ margin-right: 3px; }.page-list-list .sub-time-share a.active,.page-list-list .sub-time-share a:hover{ color: #2fb5f4; }.page-list-list .sub-text{ width: auto; text-align: left !important; }.page-list-list .sub-content{ height: 1px; padding: 1px 1px; position: relative; overflow: auto; white-space: normal; word-break: normal; }.page-list-list .sub-content-empty{ padding-top: 10px; padding-bottom: 10px; }.page-list-list .sub-content .sub-time-share{ display: block; position: absolute; right: 50px; bottom: 20px; }.page-list-list .sub-info{ padding: 30px 0px; position: relative; }.page-list-list .sub-info .sub-time-share{ display: block; position: absolute; right: 50px; bottom: 10px; }.page-list-list .sub-link{ text-align: center; }.page-list-list .sub-link a{ color: #2fb5f4; }.page-list-list .sub-link a:hover{ color: #2d9cd5; }.page-list-list tr:hover .sub-time .sub-time-time{ display: none; }.page-list-list tr:hover .sub-time .sub-time-share{ display: block; }.page-list-list .sub-line{ border-bottom: 1px solid #f2f2f2; padding-top: 10px; padding-bottom: 10px; text-align: left !important; }.page-list-list .sub-line:first-child{ border-top: 1px solid #f2f2f2; }.page-list-list .sub-line-time{ float: right; color: #999; margin-left: 10px; }.page-list-list .sub-order-group{ position: relative; display: inline-block; vertical-align: middle; width: 20px; height: 20px; }.page-list-list .sub-order-up,.page-list-list .sub-order-down{ position: absolute; right: 2px; height: 10px; width: 20px; text-align: center; overflow: hidden; }.page-list-list .sub-order-up:hover,.page-list-list .sub-order-down:hover{ color: #9dcff4; cursor: pointer; }.page-list-list .sub-order-up.active,.page-list-list .sub-order-down.active{ color: #f90; }.page-list-list .sub-order-up{ top: 0px; }.page-list-list .sub-order-down{ top: 10px;}.page-list-list .sub-order-up:before,.page-list-list .sub-order-down:before{ font-family: "cnfont"; font-style: normal; font-size: 16px; display: block; }.page-list-list .sub-order-up:before{ content: "\e656"; margin-top: -5px; }.page-list-list .sub-order-down:before{ content: "\e655"; margin-top: -7px; }}</style></head>'
        html_keyword_head_model = '<table class="page-list-header"><tbody><tr><td class="sub-name">{0}</td></tr></tbody></table>'
        html_keyword_item_model = '<table class="page-list-list"><tbody><tr class="touch sub-notice-important"><td class="sub-title"><a target="_blank" href="{0}">{1}</a></td><td class="sub-code">{2} {3}</td></tr></tbody></table>'
        for keyword in keywordList:

            html_keyword_head = html_keyword_head_model.format(keyword)
            html_keyword_items = ''
            for i in range(length):
                title = sheet.cell_value(i, 0)
                keyword_item = sheet.cell_value(i, 5)
                if (keyword != keyword_item):
                    continue

                source = sheet.cell_value(i, 4)
                date = sheet.cell_value(i, 2)
                url = sheet.cell_value(i, 3)
                savePath = sheet.cell_value(i, 6)
                html_keyword_item = html_keyword_item_model.format(url, title, source, date)
                html_keyword_items += html_keyword_item
            content += html_keyword_head + html_keyword_items
        html_body = html_body.format(dateStr, content)
        html = html_head + html_body
        savePath = savePath.replace('\\', '/')
        f = open(savePath + '/info' + dateStr + '.html', 'w',encoding='utf-8')
        f.write(html)
        print(html)
        f.close()
        wb.release_resources()
        os.remove(path + "/Info+" + dateStr + ".xls")
        print('end')
        # self.cursor.close()
        # self.conn.close()
