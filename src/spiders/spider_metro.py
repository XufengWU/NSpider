# -*- coding:utf-8 -*-
import common_news_spider
import util
import re


class SpiderMetro(common_news_spider.CommonNewsSpider):

    def get_links(self, doc, url=''):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                return doc('#news-rpdropdown option').items()
        return doc('a').items()

    def get_url_of_link(self, link, doc, doc_url):
        if link.attr('value'):
            return link.attr('value')
        return link.attr('href')

    def page_filter(self, doc, url):
        return self.task_filter(doc, url, url)

    def task_filter(self, doc, url, doc_url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('.main-content .date p').text():
                    t = doc('.main-content .date p').text()
                    t = re.sub(ur'\(.+?\)', '', t)
                    t = re.sub(ur'上午', 'AM', t)
                    t = re.sub(ur'下午', 'PM', t)
                    t_stamp = util.get_timestamp_from_string(t)
                    if t_stamp >= util.get_day_stamp(offset=self.OFFSET):
                        wanted = True
                else:
                    wanted = True
        return wanted

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur' – 都市日報')
        author = ''
        category = doc('.mobile-page-name span').text()
        # tags = doc('meta[name=keywords]').attr('content')
        content = util.get_paragraphs_from_selector(doc, '.main-content .content p')
        t = doc('.main-content .date p').text()
        t = re.sub(ur'\(.+?\)', '', t)
        t = re.sub(ur'上午', 'AM', t)
        t = re.sub(ur'下午', 'PM', t)
        t_stamp = util.get_timestamp_from_string(t)

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'MetroHK'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        mt_seed = set()
        mt_seed.add('http://www.metrodaily.hk/')
        # for i in range(9):
        #     for j in range(offset + 1):
        #         d = time.localtime().tm_mday - j
        #         if d <= 0:
        #             d = 1
        #         mt_seed.add(
        #             'http://www.metrohk.com.hk/index.php?cmd=detail&categoryID=' + str(i) + "&publishDate=" + str(
        #                 time.localtime().tm_year) + "-" + str(time.localtime().tm_mon) + "-" + str(d))
        # spider_mt = SpiderMetro('SpiderMetro', mt_seed, {ur'http://www\.metrohk\.com\.hk/index\.php\?cmd=detail.*'},
        #                         THREAD_NUM=10)
        spider_mt = SpiderMetro('SpiderMetro', mt_seed, {ur'http://www\.metrodaily\.hk/metro_news/.+'},
                                THREAD_NUM=10)
        spider_mt.OFFSET = offset
        spider_mt.BATCH_NUMBER = util.get_day_stamp() + 10003
        return spider_mt


if __name__ == '__main__':
    SpiderMetro.PUT_IN_STORAGE = False
    SpiderMetro.start_crawling()
