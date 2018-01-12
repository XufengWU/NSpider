# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import threading

prefix = 'http://www.metroradio.com.hk'
cat_pattern = re.compile(ur'(?<=- ).+新聞(?= -)')
complete_pattern = re.compile(ur'http://.+')
news_id_pattern = re.compile(r'(?<=NewsI)(D=\d+|d=\d+)')


class SpiderMetroFinance(common_news_spider.CommonNewsSpider):

    ids = set()
    id_lock = threading.RLock()

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        return u

    def normal_item_check(self, item, task, response):
        doc_url = task.url
        if item.id != '':
            with self.id_lock:
                if item.id in self.ids:
                    self.ids.add(item.id)
                    self.logger_con.warning('DUPLICATED NEWS: ' + doc_url)
                    self.logger_file.warning('DUPLICATED NEWS: ' + doc_url)
                    return False
                self.ids.add(item.id)
        if item.t == '':
            self.logger_con.warning('NO TIME: ' + doc_url)
            self.logger_file.warning('NO TIME: ' + doc_url)
            return False
        if item.title == '':
            self.logger_con.warning('NO TITLE: ' + doc_url)
            self.logger_file.warning('NO TITLE: ' + doc_url)
            return False
        if item.category == '':
            self.logger_con.warning('NO CAT: ' + doc_url)
            self.logger_file.warning('NO CAT: ' + doc_url)
        if item.content == '':
            self.logger_con.warning('NO CONTENT: ' + doc_url)
            self.logger_file.warning('NO CONTENT: ' + doc_url)
            return False
        return True

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = doc('h4').text()
        t = doc('#ContentPlaceHolder1_IndividualNewsList_lblTime_0').text()
        t_stamp = util.get_timestamp_from_string(t, time_format='%d/%m/%Y %H:%M')
        category = ''
        cat = doc('title').text()
        if cat_pattern.findall(cat):
            category = cat_pattern.findall(cat)[0]
        author = ''
        content = util.get_paragraphs_from_selector(doc, '#ContentPlaceHolder1_IndividualNewsList_lblContent_0')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'MetroFinance'
        item.task_no = self.BATCH_NUMBER

        item.id = ''
        if news_id_pattern.findall(task.url):
            item.id = (news_id_pattern.findall(task.url)[0])[2:]

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        metrofinance_seed = {'http://www.metroradio.com.hk/104/', 'http://www.metroradio.com.hk/news/live.aspx'}
        util.add_hrefs('http://www.metroradio.com.hk/104/', {'.toplink2 a'}, metrofinance_seed, prefix=prefix)
        day_str = util.get_day_string(offset=offset)
        spider_metrofinance = SpiderMetroFinance('SpiderMetroFinance',
                                                 metrofinance_seed,
                                                 {ur'http://www\.metroradio\.com\.hk/.+' + day_str + '.+'},
                                                 THREAD_NUM=10)
        spider_metrofinance.OFFSET = offset
        spider_metrofinance.BATCH_NUMBER = util.get_day_stamp() + 10410
        return spider_metrofinance


if __name__ == '__main__':
    SpiderMetroFinance.PUT_IN_STORAGE = False
    SpiderMetroFinance.start_crawling()
