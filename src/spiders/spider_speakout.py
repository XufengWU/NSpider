# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import threading


complete_pattern = re.compile(ur'http://.+')

relative_time_pattern = re.compile(ur'\d+小時\d分鐘|\d+小時|\d+分鐘')
prefix = 'http://speakout.hk'


class SpiderSpeakout(common_news_spider.CommonNewsSpider):

    url_time_dict = {}
    url_time_dict_lock = threading.RLock()

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        return u

    def get_filtered_urls(self, task, response):
        doc = self.get_doc(response)
        urls = set()
        for link in self.get_links(doc):
            u = self.get_url_of_link(link, doc, task.url)
            u = util.url_para_filter(u, self.AUTO_FILTER_URL_PARAS)
            with self.url_time_dict_lock:
                if not re.findall(u'日', link.parent().siblings().text()) and relative_time_pattern.findall(link.parent().siblings().text()):
                    t_str = relative_time_pattern.findall(link.parent().siblings().text())[0]
                    t_stamp = 0
                    if re.match(ur'\d+小時\d+分鐘', t_str):
                        h_m = re.split(ur'小時|分鐘', t_str)
                        t_stamp = util.get_now() - int(h_m[0]) * 3600 - int(h_m[1]) * 60
                    elif re.match(ur'\d+小時', t_str):
                        t_stamp = util.get_now() - int(t_str.split(u'小時')[0]) * 3600
                    elif re.match(ur'\d+分鐘', t_str):
                        t_stamp = util.get_now() - int(t_str.split(u'分鐘')[0]) * 60
                    self.url_time_dict[u] = t_stamp
                    if u and self.task_filter(doc, u, task.url):
                        urls.add(u)
        return urls

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                with self.url_time_dict_lock:
                    if url in self.url_time_dict:
                        t_stamp = self.url_time_dict[url]
                        if t_stamp >= util.get_day_stamp(self.OFFSET):
                            return True
                        return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                with self.url_time_dict_lock:
                    if url in self.url_time_dict:
                        t_stamp = self.url_time_dict[url]
                        if t_stamp >= util.get_day_stamp(self.OFFSET):
                            return True
                        return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, u'港人講地 SPEAKOUT.HK - ')
        with self.url_time_dict_lock:
            t_stamp = self.url_time_dict[task.url]
        t = doc('.published').text()
        category = doc('.category-name').text()
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'td p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'SpeakOut'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        speakout_seed = {'http://speakout.hk/'}
        spider_speakout = SpiderSpeakout('SpiderSpeakout',
                                         speakout_seed,
                                         {ur'http://.*\d\d\d\d-\d\d-\d\d.+'},
                                         THREAD_NUM=10)
        spider_speakout.BATCH_NUMBER = util.get_day_stamp() + 10520
        spider_speakout.OFFSET = offset
        return spider_speakout

if __name__ == '__main__':

    SpiderSpeakout.PUT_IN_STORAGE = False
    SpiderSpeakout.start_crawling()
