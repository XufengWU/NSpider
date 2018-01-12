# -*- coding:utf-8 -*-
import src.spiders.spider_cablenews as cable_news
import src.spiders.util as util
import requests
from pyquery import PyQuery as pq
import re

total_page_pattern = re.compile(ur'(?<=\(共有 )\d+?(?=\))')


def get_news_page_url(day_str, page_no):
    portal_url = 'http://cablenews.i-cable.com/webapps/news_video/search_result.php?' + \
                 'fromYear=' + day_str[0:4] + \
                 '&fromMonth=' + day_str[4:6] + \
                 '&fromDay=' + day_str[6:8] + \
                 '&toYear=' + day_str[0:4] + \
                 '&toMonth=' + day_str[4:6] + \
                 '&toDay=' + day_str[6:8] + \
                 '&page=' + str(page_no / 10 + 1) + \
                 '&inTitle=&topic1=1&channel_id=2&topic=5&utf8_convert_flag=F&f_o_g_c=T'
    return portal_url


def main_task():
    cable_news.SpiderCableNews.PUT_IN_STORAGE = True
    for i in range(util.get_offset_by_day_date('20160724'), util.get_offset_by_day_date('20131231')):
        day_str = util.get_day_string(offset=i)
        first_url = get_news_page_url(day_str, 1)
        r = requests.get(first_url)
        d = pq(r.text)
        if total_page_pattern.findall(d('#1').text()):
            total_page = int(total_page_pattern.findall(d('#1').text())[0])
            cablenews_seed = set()
            for j in range(total_page):
                cablenews_seed.add(get_news_page_url(day_str, j+1))
            cablenews_reg = {ur'http://.+?\.i-cable\.com/.*videopage.*\d+/.*',
                             ur'http://.+?\.i-cable\.com/.*VideoPage.*\d+/.*'}
            spider_cablenews = cable_news.SpiderCableNews('SpiderCableNews',
                                                          cablenews_seed,
                                                          cablenews_reg,
                                                          THREAD_NUM=10)
            spider_cablenews.BATCH_NUMBER = util.get_day_stamp(offset=i) + 10220
            spider_cablenews.OFFSET = i
            spider_cablenews.logger_file = spider_cablenews.get_file_logger('cablenews_task_log', 'logs/cablenews_task.log')
            spider_cablenews.start()


if __name__ == '__main__':
    main_task()
