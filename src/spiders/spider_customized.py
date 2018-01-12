# -*- coding:utf-8 -*-
import sys
import getopt
from pyquery import PyQuery as pq
import json
import common_news_spider
import codecs
import util
import requests

opts, args = getopt.getopt(sys.argv[1:],
                           '',
                           [
                               'seed_url=',
                               'reg_ex=',
                               'thread_num=',
                               'max_depth=',
                               'res_encoding=',
                               'css_content_sele=',
                               'fetch_delay=',
                               'timeout_value='
                           ])
customized_seed = set()
customized_reg = set()
thread_num = 1
max_depth = 1
res_encoding = None
css_content_sele = None
fetch_delay = 0
timeout_value = 30

for op, arg in opts:
    if op == '--seed_url':
        customized_seed.add(arg)
    elif op == '--reg_ex':
        customized_reg.add(arg)
    elif op == '--thread_num':
        thread_num = int(arg)
    elif op == '--max_depth':
        max_depth = int(arg)
    elif op == '--res_encoding':
        res_encoding = arg
    elif op == '--css_content_sele':
        css_content_sele = arg
    elif op == '--fetch_delay':
        fetch_delay = int(arg)
    elif op == '--timeout_value':
        timeout_value = int(arg)


class SpiderCustomized(common_news_spider.CommonNewsSpider):

    def send_request(self, task):
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        if res_encoding:
            r.encoding = res_encoding
        return r

    def normal_solver(self, task, response):
        doc = pq(response.text)
        file_path = self.OUTPUT_FILE_PATH
        if self.OUTPUT_FILE_PATH is None:
            file_path = 'news_data.json'
        item_list = []
        with self.output_file_lock:
            try:
                with codecs.open(file_path, 'r', encoding='utf-8') as fr:
                    item_list = json.load(fr)
                    fr.close()
            except Exception:
                with codecs.open(file_path, 'w', encoding='utf-8') as fw:
                    fw.close()
            with codecs.open(file_path, 'w', encoding='utf-8') as fw:
                if css_content_sele and doc(css_content_sele):
                    content = doc(css_content_sele).text()
                else:
                    content = doc('p').text()
                item_dict = [content]
                item_list.append(item_dict)
                json.dump(item_list, fw)
                fw.close()

    @classmethod
    def get_auto_configured_spider(cls, offset=0):

        spider_customized = SpiderCustomized('SpiderCustomized', customized_seed, customized_reg, THREAD_NUM=thread_num,
                                             MAX_DEPTH=max_depth)
        spider_customized.BATCH_NUMBER = util.get_day_stamp()
        spider_customized.OFFSET = offset
        spider_customized.FETCH_DELAY = fetch_delay
        spider_customized.RESPONSE_TIMEOUT_VALUE = timeout_value
        return spider_customized


if __name__ == '__main__':
    SpiderCustomized.PUT_IN_STORAGE = False
    SpiderCustomized.start_crawling()
