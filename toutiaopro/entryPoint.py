from scrapy import  cmdline
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from toutiaopro.spiders.shanghaizhengquan import ShangHaiZhengQuanSpider

# cmdline.execute(['scrapy','crawl','shanghaizhengquan'])
settings = get_project_settings()


process = CrawlerProcess(settings=settings)
process.crawl(ShangHaiZhengQuanSpider)
process.start()