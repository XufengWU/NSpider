# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re
from pyquery import PyQuery as pq

complete_pattern = re.compile(r'http\://.+')
amb_pattern = re.compile(r'\.\./.+')
news_prefix = 'http://www.chinadailyasia.com/hknews/'


class SpiderChinaDaily(common_news_spider.CommonNewsSpider):

    def get_links(self, doc, url=''):
        links = []
        for r in re.findall(r'<a href.+?</a>', str(doc)):
            links.append(pq(r))
        return links

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not amb_pattern.match(u):
                if not complete_pattern.match(u):
                    u = news_prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1.conttit'})
        t = util.get_time_string_from_selectors(doc, {'div.pubtime'})
        t_stamp = util.get_timestamp_from_string(t)
        category = 'hk'
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.contentbox p')
        content = re.sub(r'READMORE\: .+\n', '', content)

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'ChinaDaily'
        item.task_no = self.BATCH_NUMBER
        for img in doc('div.contentbox img').items():
            if img.attr('src') != '':
                media_u = 'http://www.chinadailyasia.com/' + re.sub(r'.+(?=attachement)', '', img.attr('src'))
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                elif img.siblings('p'):
                    des = img.siblings('p').text()
                media = self.NewsItem.MediaItem(media_url=media_u, type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        chinadaily_seed = {'http://www.chinadailyasia.com/hknews/'}
        chinadaily_reg = {ur'http\://www\.chinadailyasia\.com/hknews/.+/content.+'}
        spider_chinadaily = SpiderChinaDaily('SpiderChinaDaily',
                                             chinadaily_seed,
                                             chinadaily_reg,
                                             THREAD_NUM=10,
                                             MAX_DEPTH=1)
        spider_chinadaily.BATCH_NUMBER = util.get_day_stamp() + 10710
        spider_chinadaily.OFFSET = offset
        return spider_chinadaily


if __name__ == '__main__':

    SpiderChinaDaily.PUT_IN_STORAGE = False
    SpiderChinaDaily.start_crawling()
