# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re

url_stamp_pattern = re.compile(r'(?<=/)\d{10}(?=_.+)')


class SpiderHKSilicon(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t_stamp = 0
        t_stamp_url = doc('meta[property="og:image:url"]').attr('content')
        if t_stamp_url:
            f_res = url_stamp_pattern.findall(t_stamp_url)
            if f_res:
                t_stamp = int(f_res[0])
        t = ''
        if t_stamp:
            t = time.ctime(t_stamp)
        else:
            t = doc('ul.blog-info i.fa-calendar').parent('li').text()
            t_stamp = self.get_stamp_from_relative_timestr(t)
        category = doc('ul.blog-info i.fa-tags').siblings('a').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.blog-content')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKSilicon'
        item.task_no = self.BATCH_NUMBER

    def get_stamp_from_relative_timestr(self, t_str):
        cur_stamp = int(time.time())
        number_tm = re.findall(r'\d+', t_str)
        if number_tm:
            number_tm = int(number_tm[0])
            if re.findall(ur'分鐘', t_str):
                return cur_stamp - number_tm * 60
            elif re.findall(ur'小時', t_str):
                return cur_stamp - number_tm * 3600
            elif re.findall(ur'天', t_str):
                return cur_stamp - number_tm * 24 * 3600
            elif re.findall(ur'星期', t_str):
                return cur_stamp - number_tm * 7 * 24 *3600
            elif re.findall(ur'月', t_str):
                return cur_stamp - number_tm * 30 * 7 * 24 * 3600
        return 0

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        day_str = util.get_day_string(offset=offset)
        apple_seed = {'http://www.hksilicon.com/?page=1'}
        spider_hksilicon = SpiderHKSilicon('SpiderHKSilicon',
                                   apple_seed,
                                   {ur'http\://www\.hksilicon\.com/articles/\d+'},
                                   THREAD_NUM=15)
        spider_hksilicon.BATCH_NUMBER = util.get_day_stamp() + 10690
        spider_hksilicon.OFFSET = offset
        return spider_hksilicon


if __name__ == '__main__':

    SpiderHKSilicon.PUT_IN_STORAGE = False
    SpiderHKSilicon.DEFAULT_PUT_IN_FILE = True
    # SpiderHKSilicon.OUTPUT_FILE_PATH = 'Apple_' + str(i) + '.json'
    _urls = set()
    for i in range(201, 251):
        _urls.add('http://www.hksilicon.com/?page=' + str(i))
        SpiderHKSilicon.start_crawling(offset=100, seed_urls=_urls, OUTPUT_FILE_PATH='HKSilicon_'+str(i)+'.json')
