# -*- coding: utf-8 -*-
"""
@name:XXX
@Date: 2019/11/9 14:58
@Version: v.0.0
"""
import os
import sys
import time
from multiprocessing import Process, Manager, freeze_support

import xlwt
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, QDate
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, \
    QPushButton, QTextBrowser, QComboBox, QHBoxLayout, QVBoxLayout, QDateTimeEdit

from scrapy.crawler import CrawlerProcess

from scrapy.utils.project import get_project_settings

from toutiaopro.spiders.total import TotalSpider
import xlrd
from xlutils.copy import copy


class CrawlWindows(QWidget):
    def __init__(self):
        super(CrawlWindows, self).__init__()
        self.user_setting_path = os.getcwd()
        print(self.user_setting_path)

        try:
            #doc = Document(path+"\info.docx")  # 读取现有的word 建立文档对象
            wb = xlrd.open_workbook(self.user_setting_path + "\setting_user.xls", formatting_info=True)
            wb.release_resources()
        except Exception as e:
            print('创建文档异常：',e)
            xls = xlwt.Workbook()
            xls.add_sheet('sheet1')
            sheet = xls.get_sheet('sheet1')
            sheet.write(0,0,'重庆银行,中信银行')
            sheet.write(1,0,r'C:\Users\Admin')

        wb = xlrd.open_workbook(self.user_setting_path + "\setting_user.xls", formatting_info=True)

        sheet = wb.sheet_by_name('sheet1')

        keywords = sheet.cell_value(0,0)
        savepath = sheet.cell_value(1,0)
        wb.release_resources()
        self.resize(600, 300)
        self.setWindowIcon(QIcon(':icons/favicon.ico'))
        self.setWindowTitle('信息收集')

        self.keyword = QLineEdit(keywords,self)
        # self.crawlName = QComboBox(self)
        self.pageNum = QComboBox(self)
        self.startDate = QDateTimeEdit(QDate.currentDate(), self)
        self.startDate.setDisplayFormat("yyyy-MM-dd")
        self.endDate = QDateTimeEdit(QDate.currentDate(), self)
        self.endDate.setDisplayFormat("yyyy-MM-dd")

        # self.crawlName.addItems(['今日头条', '华龙网'])
        self.pageNum.addItems(['1','2','3','4','5','6','7','8','9','10'])
        self.save_location = QLineEdit(savepath,self)
        self.log_browser = QTextBrowser(self)
        self.crawl_button = QPushButton('Start crawl', self)
        self.crawl_button.clicked.connect(lambda: self.crawl_slot(self.crawl_button))

        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(QLabel('搜索关键字:'))
        self.v_layout.addWidget(self.keyword)
        self.v_layout.addWidget(QLabel('开始时间:'))
        self.v_layout.addWidget(self.startDate)
        self.v_layout.addWidget(QLabel('结束时间:'))
        self.v_layout.addWidget(self.endDate)
        self.v_layout.addWidget(QLabel('保存路径:'))
        self.v_layout.addWidget(self.save_location)
        # self.h_layout.addWidget(QLabel('选择网站:'))
        # self.h_layout.addWidget(self.crawlName)
        self.h_layout.addWidget(QLabel('选择爬取页数:'))
        self.h_layout.addWidget(self.pageNum)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(QLabel('日志:'))
        self.v_layout.addWidget(self.log_browser)
        self.v_layout.addWidget(self.crawl_button)
        self.setLayout(self.v_layout)

        self.p = None
        self.Q = Manager().Queue()
        self.log_thread = LogThread(self)

    def crawl_slot(self, button):
        if button.text() == 'Start crawl':
            self.log_browser.clear()
            self.crawl_button.setText('Stop crawl')
            keywords = self.keyword.text().strip()
            # crawl_name = self.crawlName.currentText()
            pageNum = int(self.pageNum.currentText())
            save_location = self.save_location.text().strip()
            temp=save_location.replace('\\', '/')
            startDate = self.startDate.text()
            endDate = self.endDate.text()

            wb = xlrd.open_workbook(self.user_setting_path + "\setting_user.xls", formatting_info=True)
            xls = copy(wb)
            sheet = xls.get_sheet('sheet1')
            sheet.write(0, 0, keywords)
            sheet.write(1, 0, save_location)
            xls.save(self.user_setting_path + "\setting_user.xls")
            self.p = Process(target=crawl_run, args=(self.Q, keywords, save_location,startDate,endDate,pageNum))
            self.log_browser.setText('The collection process is starting...')
            self.p.start()
            self.log_thread.keywords = keywords
            self.log_thread.start()
        else:
            self.crawl_button.setText('Start crawl')
            self.p.terminate()

            self.log_thread.terminate()


class LogThread(QThread):
    def __init__(self, gui):
        super(LogThread, self).__init__()
        self.gui = gui
        self.keywords =''

    def run(self) -> None:
        while True:
            if not self.gui.Q.empty():
                self.gui.log_browser.append(self.gui.Q.get())

                # 确保滑动条到底
                cursor = self.gui.log_browser.textCursor()
                pos = len(self.gui.log_browser.toPlainText())
                cursor.setPosition(pos)
                self.gui.log_browser.setTextCursor(cursor)

                if '采集结束' in self.gui.log_browser.toPlainText():
                    #
                    # times = time.time()
                    # localtime = time.localtime(times)
                    # dateStr = time.strftime('%Y%m%d', localtime)
                    # savePath =''
                    # path = os.getcwd()
                    # path = path.replace('\\', '/')
                    # wb = xlrd.open_workbook(path+"/Info+"+dateStr+".xls", formatting_info=True)
                    #
                    # sheet = wb.sheet_by_name('第一个sheet')
                    # length = sheet.nrows
                    # keywordList = self.keywords.replace('，', ',').split(',')
                    # content = ''
                    # html_body = '<body><div id="container" style=""><div id="header" class="header-wrap"><img src="./files/logo-touhang.png" alt="test"><h4><strong>信息聚合发布</strong></h4></div><div id="content" style=""><a class="current" id="date_announcement" style="text-align:left;">更新日期：{0}</a><div class="page-list" id="test">{1}</div></div><div style="background-color:#FFA500;clear:both;text-align:center;">技术支持 © </div></div></body></html>'
                    # html_head = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>发布信息聚合</title><style type="text/css">#container{margin-left:10%;margin-right:10%;text-align:center;}em{font-style:normal;color:#c00}li a:hover:not(.active) {    background-color: #555;    color: white;}li a {    display: block;    color: #000;    padding: 8px 16px;    text-decoration: none;}img {max-width:100%;}.page-list{ padding: 10px 0px; }.page-list-header{ width: 100%; table-layout: auto; /*fixed*/ background-color: #f7f7f7; color: #666666; }.page-list-header:hover{ background-color: #f1f6fa; }.page-list-header td{ height: 40px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.page-list-header tr td:first-child{ padding-left: 50px; text-align: left; }.page-list-header tr td.last-child{ padding-right: 50px; text-align: right; }.page-list-header .sub-title{ width: 250px; font-size: 18px; color: #333333; }.page-list-header .sub-name{ width: 150px; font-size: 18px; color: #333333; }.page-list-header .sub-code{ width: 80px; text-align: right; }.page-list-header .sub-info{ width: auto; text-align: center; }.page-list-header .sub-info a,.page-list-header .sub-info span{ display: inline-block; padding: 0px 5px; color: #333; }.page-list-header .sub-count{ width: 230px; text-align: right; }.page-list-list{ width: 100%;margin: 10px;table-layout: auto; /*fixed*/ color: #666666; }.page-list-list.page-list-list-auto{ table-layout: auto; }.page-list-list.page-list-list-color th{ background-color: #2fb5f4; color: #fff; font-weight: normal; }.page-list-list p{ margin: 2px 0px; }.page-list-list tr:hover{ background-color: #f1f6fa; color: #232323;}.page-list-list tr.sub-none-hover:hover{ background: none;height:10px }.page-list-list.page-list-listsummary tr:hover{ background: none;height:10px }.page-list-list td,.page-list-list th{ padding: 5px;height:10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;    box-sizing: content-box; position: relative; }.page-list-list tr th:first-child,.page-list-list tr td:first-child{ padding-left: 50px; text-align: left; }.page-list-list tr th.last-child,.page-list-list tr td.last-child{ padding-right: 50px; text-align: right; }.page-list-list th{ background-color: #f2f2f2;height:44px; }.page-list-list .sub-break{ overflow: visible; white-space: normal; padding: 8px 5px; line-height: 20px; }.page-list-list .sub-center{ text-align: center !important; }.page-list-list .sub-right{ text-align: right !important; }.page-list-list .sub-hidden{ display: none; }.page-list-list .sub-no{ width: 80px; }.page-list-list .sub-code{ width: 80px; }.page-list-list .sub-name{ width: 80px; }.page-list-list .sub-title,.page-list-list .sub-value{ width: auto; white-space: normal; line-height:22px;}.page-list-list .sub-title i{ margin: 0px 2px; font-size: 28px; line-height: 18px; vertical-align: bottom; }.page-list-list .sub-title img {margin-left: 4px; margin-right: 4px;}.page-list-list th.sub-title i{ font-size: 18px; color: #ff1100; }.page-list-list .sub-date{ width: 100px; text-align: right; }.page-list-list .sub-time{ width: 180px; text-align: right; }.page-list-list .sub-time-share{ display: none; line-height: 20px; }.page-list-list .sub-time-share a{ display: inline-block; margin: 0px 5px; }.page-list-list .sub-time-share a i{ margin-right: 3px; }.page-list-list .sub-time-share a.active,.page-list-list .sub-time-share a:hover{ color: #2fb5f4; }.page-list-list .sub-text{ width: auto; text-align: left !important; }.page-list-list .sub-content{ height: 1px; padding: 1px 1px; position: relative; overflow: auto; white-space: normal; word-break: normal; }.page-list-list .sub-content-empty{ padding-top: 10px; padding-bottom: 10px; }.page-list-list .sub-content .sub-time-share{ display: block; position: absolute; right: 50px; bottom: 20px; }.page-list-list .sub-info{ padding: 30px 0px; position: relative; }.page-list-list .sub-info .sub-time-share{ display: block; position: absolute; right: 50px; bottom: 10px; }.page-list-list .sub-link{ text-align: center; }.page-list-list .sub-link a{ color: #2fb5f4; }.page-list-list .sub-link a:hover{ color: #2d9cd5; }.page-list-list tr:hover .sub-time .sub-time-time{ display: none; }.page-list-list tr:hover .sub-time .sub-time-share{ display: block; }.page-list-list .sub-line{ border-bottom: 1px solid #f2f2f2; padding-top: 10px; padding-bottom: 10px; text-align: left !important; }.page-list-list .sub-line:first-child{ border-top: 1px solid #f2f2f2; }.page-list-list .sub-line-time{ float: right; color: #999; margin-left: 10px; }.page-list-list .sub-order-group{ position: relative; display: inline-block; vertical-align: middle; width: 20px; height: 20px; }.page-list-list .sub-order-up,.page-list-list .sub-order-down{ position: absolute; right: 2px; height: 10px; width: 20px; text-align: center; overflow: hidden; }.page-list-list .sub-order-up:hover,.page-list-list .sub-order-down:hover{ color: #9dcff4; cursor: pointer; }.page-list-list .sub-order-up.active,.page-list-list .sub-order-down.active{ color: #f90; }.page-list-list .sub-order-up{ top: 0px; }.page-list-list .sub-order-down{ top: 10px;}.page-list-list .sub-order-up:before,.page-list-list .sub-order-down:before{ font-family: "cnfont"; font-style: normal; font-size: 16px; display: block; }.page-list-list .sub-order-up:before{ content: "\e656"; margin-top: -5px; }.page-list-list .sub-order-down:before{ content: "\e655"; margin-top: -7px; }}</style></head>'
                    # html_keyword_head_model = '<table class="page-list-header"><tbody><tr><td class="sub-name">{0}</td></tr></tbody></table>'
                    # html_keyword_item_model = '<table class="page-list-list"><tbody><tr class="touch sub-notice-important"><td class="sub-title"><a target="_blank" href="{0}">{1}</a></td><td class="sub-code">{2} {3}</td></tr></tbody></table>'
                    # for keyword in keywordList:
                    #
                    #     html_keyword_head = html_keyword_head_model.format(keyword)
                    #     html_keyword_items = ''
                    #     for i in range(length):
                    #         title = sheet.cell_value(i, 0)
                    #         keyword_item = sheet.cell_value(i, 5)
                    #         if (keyword != keyword_item):
                    #             continue
                    #
                    #         source = sheet.cell_value(i, 4)
                    #         date = sheet.cell_value(i, 2)
                    #         url = sheet.cell_value(i, 3)
                    #         savePath = sheet.cell_value(i,6)
                    #         html_keyword_item = html_keyword_item_model.format(url, title, source, date)
                    #         html_keyword_items += html_keyword_item
                    #     content += html_keyword_head + html_keyword_items
                    # html_body = html_body.format(dateStr, content)
                    # html = html_head+html_body
                    # savePath =savePath.replace('\\', '/')
                    # f = open(savePath+'/info'+dateStr+'.html','w')
                    # f.write(html)
                    # print(html)
                    # f.close()
                    # wb.release_resources()
                    # os.remove(path+"/Info+"+dateStr+".xls")
                    self.gui.crawl_button.setText('Start crawl')
                    break
                # 睡眠10ms

                self.msleep(10)


def crawl_run(Q, keywords, save_location,startDate,endDate,pageNum):
    # CrawlerProcess
    settings = get_project_settings()


    process = CrawlerProcess(settings=settings)
    process.crawl(TotalSpider,Q=Q,data = keywords,savePath=save_location,startDate=startDate,endDate=endDate,num=pageNum)
    process.start()


    # process = CrawlerProcess(settings=settings)
    # process.crawl(ShangHaiZhengQuanSpider,Q=Q)
    # process.start()

    """
    # CrawlerRunner
    configure_logging(install_root_handler=False)
    logging.basicConfig(filename='output.log', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
    runner = CrawlerRunner(settings={
        'USER_AGENT': ua,
        'ROBOTSTXT_OBEY': is_obey,
        'SAVE_CONTENT': 'books.jl',
        'ITEM_PIPELINES': {
            'books.pipelines.ChanelPipeline': 300,
        },
    })
    d = runner.crawl(BookSpider, Q=Q)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    """


if __name__ == '__main__':
    freeze_support()
    app = QApplication(sys.argv)
    books = CrawlWindows()
    books.show()
    sys.exit(app.exec_())