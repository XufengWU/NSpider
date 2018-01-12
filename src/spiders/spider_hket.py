# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re
import threading


# date patterns:
'<div id="news-date">2016年7月14日 16:39 星期四</div>'
'<td id="main-left"><div style="font-weight:bold; color:#000; margin:25px 10px">2016年7月14日 星期四 16:40 </div></td>'
'<div class="date">2016/07/14 星期四 16:39</div>'
'<div style="float:left; font-size:15px">2016年07月14日 16:36 星期四</div>'

selectors = ['#eti-article-functions div', 'div#news-date', '#main-left div', '.content div.date']
date_patterns = [re.compile(ur'\d{4}年\d+月\d+日.*?\d\d:\d\d'), re.compile(ur'\d{4}/\d+/\d+.*?\d\d:\d\d'), re.compile(ur'\d{4}年\d+月\d+日')]
bold_style_pattern = re.compile(ur'font-weight:bold;')
prefix_pattern = re.compile(ur'(?<=http://)\w+')
invest_page_pattern = re.compile(ur'http://invest\.hket\.com/article/\d+.*')
min_sec_pattern = re.compile(ur'\d\d:\d\d')
youtube_pattern = re.compile(ur'.*youtube\.com.+')
no_http_pattern = re.compile(r'//.+')


class SpiderHKET(common_news_spider.CommonNewsSpider):

    _doc = None
    _doc_wanted = False
    _doc_lock = threading.RLock()
    # _url_time_dict = dict()
    # _url_time_dict_lock = threading.RLock()

    # def get_links(self, doc, url=''):
    #     return doc('#eti-inews-list a').items()

    # def get_filtered_urls(self, task, response):
    #     doc = self.get_doc(response)
    #     urls = set()
    #     for link in self.get_links(doc):
    #         if min_sec_pattern.match(link.siblings('span').text()):
    #             u = self.get_url_of_link(link, doc, task.url)
    #             u = util.url_para_filter(u, self.AUTO_FILTER_URL_PARAS)
    #             with self._url_time_dict_lock:
    #                 self._url_time_dict[u] = util.get_day_string(interval_str='/', offset=self.OFFSET) + \
    #                                          ' ' + \
    #                                          link.siblings('span').text()
    #                 if u and self.task_filter(doc, u, task.url):
    #                     urls.add(u)
    #     return urls

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t_stamp = util.get_timestamp_from_selectors(doc=doc, selectors=selectors, date_patterns=date_patterns)
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    wanted = True
        return wanted

    def task_filter(self, doc, url, doc_url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                try:
                    self._doc_lock.acquire()
                    wanted = self._time_filter(doc, url)
                    self._doc = doc
                finally:
                    self._doc_lock.release()
        return wanted

    def _time_filter(self, doc, url):
        if doc is self._doc:
            return self._doc_wanted
        else:
            t_stamp = util.get_timestamp_from_selectors(doc=doc, selectors=selectors, date_patterns=date_patterns)
            if t_stamp >= util.get_day_stamp(self.OFFSET) or t_stamp == 0:
                self._doc_wanted = True
                return True
            self._doc_wanted = False
            return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = ''
        t = ''
        t_stamp = 0
        category = ''
        author = ''
        content = ''

        if invest_page_pattern.match(task.url):
            title = util.get_filtered_title(doc, {'#headline'})
        else:
            title = util.get_filtered_title(doc, {'title'}, ur' - 香港經濟日報.*')
        # if re.findall(ur'（短片）', title):
        #     return
        t = util.get_time_string_from_selectors(doc=doc, selectors=selectors, date_patterns=date_patterns)
        t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
        # with self._url_time_dict_lock:
        #     if task.url in self._url_time_dict:
        #         t = self._url_time_dict[task.url]
        #         t_stamp = util.get_timestamp_from_string(t)
        if doc('div.active'):
            category = doc('div.active').text()
        elif doc('div.selected'):
            category = doc('div.selected').text()
        else:
            for a in doc('a').items():
                if a.attr('style') and bold_style_pattern.findall(a.attr('style')):
                    category = a.text()
                    break
        if category == '':
            if prefix_pattern.findall(task.url):
                category = prefix_pattern.findall(task.url)[0]
        content = util.get_paragraphs_from_selector(doc, 'p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKET'
        item.task_no = self.BATCH_NUMBER
        for img in doc('#content img, .content img').items():
            if img.attr('src') != '':
                media = self.NewsItem.MediaItem(media_url=img.attr('src'), type='image', description='',
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        for a in doc('iframe').items():
            if a.attr('src') and youtube_pattern.match(a.attr('src')):
                media_u = a.attr('src')
                if no_http_pattern.match(media_u):
                    media_u = 'http:' + media_u
                media = self.NewsItem.MediaItem(media_url=media_u, type='youtube', description='youtube',
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        day_str = util.get_day_string(offset=offset)
        hket_seed = {'http://inews.hket.com/sran001/%E5%85%A8%E9%83%A8?dis=' + day_str}
        spider_hket = SpiderHKET('SpiderHKET', hket_seed, {ur'http://.+\.hket\.com/article/\d+/.*'}, THREAD_NUM=5)
        spider_hket.BATCH_NUMBER = util.get_day_stamp(offset=offset) + 10110
        spider_hket.OFFSET = offset
        return spider_hket


if __name__ == '__main__':

    SpiderHKET.PUT_IN_STORAGE = False
    SpiderHKET.start_crawling()
