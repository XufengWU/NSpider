# -*- coding: utf-8 -*-
from src.spiders.common_news_spider import CommonNewsSpider
import re
import time
import src.spiders.util
import requests
from pyquery import PyQuery as pq

prices = {}
vegs = [u'白蘿蔔',
        u'菠菜', u'菜芯', u'豆苗', u'番茄', u'紅蘿蔔', u'節瓜', u'芥蘭', u'青白菜', u'青瓜', u'青椰菜', u'生菜', u'薯仔', u'茼蒿', u'王菜', u'西蘭花',
        u'西生菜', u'西洋菜', u'油麥菜', u'芋頭']


class PriceSpider(CommonNewsSpider):
    veg_id = 0

    def normal_solver(self, task, response):
        doc = self.get_doc(response)
        tb = doc('table.threadlist')
        tb.remove('thead')
        for tr in tb('tr').items():
            dt = tr('td.author').text()
            dt_stamp = src.spiders.util.get_timestamp_from_string(dt)
            p = tr('td:nth-last-child(0)').text()
            if dt_stamp not in prices:
                print 'DATE OUT SCOPE!!'
            else:
                prices[dt_stamp][self.veg_id + 1] = p


if __name__ == '__main__':
    for date in range(src.spiders.util.get_timestamp_from_string('2012-01-01'),
                      src.spiders.util.get_timestamp_from_string('2017-05-21') + 1, 24 * 3600):
        prices[date] = [str(date)]
        prices[date] += [''] * len(vegs)
    for vid in range(len(vegs)):
        veg = vegs[vid]
        r = requests.get('http://www.price007.com/xgsc.aspx?ledianid=' + veg)
        d = pq(r.text)
        page_num = int(d('div.pages em').text().split(' / ')[-1])
        seeds = set()
        for i in range(1, page_num + 1):
            seeds.add('http://www.price007.com/xgsc.aspx?ledianid=' + veg + '&page=' + str(i))
        p_spider = PriceSpider(seed_urls=seeds, regs=[r'http://www\.price007\.com/xgsc\.aspx\?ledianid=.+'],
                               THREAD_NUM=10)
        p_spider.veg_id = vid
        p_spider.start()
        time.sleep(3)
    for p in prices:
        pline = ';'.join(prices[p])
        if pline[1:] != [''] * len(vegs):
            print pline
