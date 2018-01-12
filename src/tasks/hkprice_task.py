# -*- coding: utf-8 -*-
from src.spiders.common_news_spider import CommonNewsSpider
import re
import time
import src.spiders.util

prices = {}


class PriceSpider(CommonNewsSpider):

    def normal_solver(self, task, response):
        doc = self.get_doc(response)
        tb = doc('table.threadlist')
        pid = re.findall(r'\d+$', task.url)[0]
        price = []
        dt = doc('h1').text()
        dt = re.sub(ur'.+ - ', '', dt)
        price.append(str(src.spiders.util.get_timestamp_from_string(dt)))
        for tr in tb('tr').items():
            p = tr('td:nth-last-child(1)').text()
            arr_p = re.split(ur'\s+(?=港元)', p)
            if len(arr_p) > 1:
                price.append(arr_p[0])
                price.append(arr_p[1])
            elif len(arr_p) == 1:
                price.append('')
                price.append(arr_p[0])
        prices[pid] = price

if __name__ == '__main__':
    seeds = set()
    for i in range(3, 191):
        seeds.add('http://www.price007.com/xgjc.aspx?ttype='+str(i))
    p_spider = PriceSpider(seed_urls=seeds, regs=[r'http://www\.price007\.com/xgjc\.aspx\?ttype=\d+'], THREAD_NUM=15)
    p_spider.start()
    time.sleep(3)
    for pid in prices:
        print ';'.join(prices[pid])