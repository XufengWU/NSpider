# -*- coding:utf-8 -*-
import src.spiders.spider_commercialradio as commercialradio
import src.spiders.util as util
from pyquery import PyQuery as pq
import re
from selenium import webdriver

total_page_pattern = re.compile(ur'(?<=共)\d+')
page_num_pattern = re.compile(r'\d+')
complete_url_pattern = re.compile(r'http://.+')
prefix = 'http://www.881903.com/Page/ZH-TW/'


def add_hrefs(seed, reg_pattern, page_source):
    d = pq(page_source)
    for a in d('a').items():
        if a.attr('href'):
            u = a.attr('href')
            if not complete_url_pattern.match(u):
                u = prefix + u
            if reg_pattern.match(u):
                u = re.sub(r'&csid=.+', '', u)
                seed.add(u)


def main_task():
    commercialradio.SpiderCommercialRadio.PUT_IN_STORAGE = True
    commercialradio.SpiderCommercialRadio.CRAWL_NEXT = False
    commercial_reg = {ur'http://www\.881903\.com/.+detail.*'}
    reg_pattern = re.compile(ur'http://www\.881903\.com/.+detail.*')
    for i in range(util.get_offset_by_day_date('20110605'), util.get_offset_by_day_date('20080101')):
        day_str = util.get_day_string(interval_str='-', style='american', offset=i)
        portal_url = 'http://www.881903.com/Page/ZH-TW/newssearch.aspx?sdate=' + day_str + '&edate=' + day_str + '&csid=261_0'
        commercial_seed = set()
        try:
            ie_driver = webdriver.Ie('C://Users/benwu/Desktop/IEDriverServer.exe')
            ie_driver.get(portal_url)
            d = pq(ie_driver.page_source)
            add_hrefs(commercial_seed, reg_pattern, ie_driver.page_source)
            if total_page_pattern.findall(d('td.Font_Article_CH').text()):
                total_page = int(total_page_pattern.findall(d('td.Font_Article_CH').text())[0])
                for j in range(2, total_page + 1):
                    # print 'page: ' + str(j)
                    ie_driver.execute_script('StockSearchCallBack(' + str(j) + ');')
                    load_done = False
                    dd = pq(ie_driver.page_source)
                    while not load_done:
                        dd = pq(ie_driver.page_source)
                        if dd('.Font_Article_CH span'):
                            num = page_num_pattern.findall(dd('.Font_Article_CH span').text())[0]
                            if num == str(j):
                                load_done = True
                    add_hrefs(commercial_seed, reg_pattern, ie_driver.page_source)
                    # print len(commercial_seed)
        finally:
            ie_driver.close()
        spider_commercial = commercialradio.SpiderCommercialRadio('SpiderCommercialRadio',
                                                                  commercial_seed,
                                                                  commercial_reg,
                                                                  THREAD_NUM=10)
        spider_commercial.BATCH_NUMBER = util.get_day_stamp(offset=i) + 10260
        spider_commercial.OFFSET = i
        spider_commercial.logger_file = spider_commercial.get_file_logger('commercial_task_log', 'logs/commercial_task.log')
        spider_commercial.start()


if __name__ == '__main__':
    main_task()
