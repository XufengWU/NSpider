# -*- coding: utf-8 -*-
from src.spiders.common_news_spider import CommonNewsSpider
import re
import time
import src.spiders.util
import requests
from pyquery import PyQuery as pq
import json

prices = {}
fishes = {
    1: u'木棉',
    2: u'黑鯧',
    3: u'狗肚',
    5: u'鷹鯧',
    7: u'沙鯭',
    8: u'牛鰍',
    9: u'紅衫',
    10: u'青門鱔',
    11: u'烏頭',
    12: u'牙帶',
    13: u'青根',
    14: u'白飯魚',
    15: u'鮫魚',
    16: u'鰦魚',
    17: u'瓜衫',
    18: u'瓜核',
    19: u'泥斑',
    20: u'泥鯭',
    21: u'沙鑽',
    22: u'鱸魚',
    23: u'龍脷',
    24: u'馬友',
    25: u'丁公',
    26: u'白鯧',
    27: u'白立',
    28: u'黃花',
    29: u'黃腳立',
    61: u'老虎斑',
    62: u'芝麻斑',
    63: u'杉斑',
    64: u'金絲立',
    65: u'青斑',
    66: u'頭鱸',
    67: u'東星斑',
    68: u'紅魚',
    69: u'紅鮪',
    70: u'細鱗',
    71: u'黃立鯧',
    72: u'泥鯭',
    73: u'紅斑',
    74: u'火點',
    75: u'黃腳立',
    76: u'沙巴躉',
}


class PriceSpider(CommonNewsSpider):
    fid = 0

    def normal_solver(self, task, response):
        doc = self.get_doc(response)
        script = doc('script:nth-last-child(1)').text()
        dtxt = re.findall(r'(?<="data":)\[.+?\]', script)[0]
        j = json.loads(dtxt)
        i = 0
        print j
        for stamp in prices:
            prices[stamp][self.fid] = j[i]
            i += 1


if __name__ == '__main__':
    for date in range(src.spiders.util.get_timestamp_from_string('2010-01-01'),
                      src.spiders.util.get_timestamp_from_string('2017-05-22') + 1, 24 * 3600):
        prices[date] = {0: str(date)}
        for fid in fishes:
            prices[date][fid] = 0
    for fid in fishes:
        seeds = {
            'http://www.fmo.org.hk/fish-price?path=12_43_56&id=8&start=2010-01-01&end=2017-05-22&items%5B%5D=' + str(
                fid)}
        p_spider = PriceSpider(seed_urls=seeds, regs=[r'http://www.fmo.org.hk/fish\-price\?path=.+'],
                               THREAD_NUM=1)
        p_spider.fid = fid
        p_spider.start()
    for p in prices:
        pline = ''
        for fid in prices[p]:
            if fid != 0:
                pline += str(prices[p][fid]) + ';'
        print pline
