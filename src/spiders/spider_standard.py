# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re

complete_pattern = re.compile(r'http://.+')
news_prefix = 'http://www.thestandard.com.hk/'


class SpiderStandard(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = news_prefix + u
        else:
            u = ''
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'}, r' The Standard$')
        pl = doc('.heading .pull-left')
        pl.remove('span')
        t = pl.text().split(' | ')[1]
        if t:
            t_stamp = util.get_timestamp_from_string(t)
        else:
            t_stamp = 0
        category = pl.text().split(' | ')[0]
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.content p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, 'div.content')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Standard'
        item.task_no = self.BATCH_NUMBER
        for img in doc('div.content img').items():
            if img.attr('src') != '':
                media_u = img.attr('src')
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
        standard_seed = {'http://www.thestandard.com.hk/',
                         'http://www.thestandard.com.hk/breaking_news_list.php?cid=1',
                         'http://www.thestandard.com.hk/breaking_news_list.php?cid=2',
                         'http://www.thestandard.com.hk/breaking_news_list.php?cid=3',
                         'http://www.thestandard.com.hk/breaking_news_list.php?cid=4',
                         'http://www.thestandard.com.hk/breaking_news_list.php?cid=5'}
        standard_reg = {ur'http\://.+breaking-news\.php\?id=\d+$',
                        ur'http\://.+section-news\.php\?id=\d+$'}
        spider_standard = SpiderStandard('SpiderStandard',
                                         standard_seed,
                                         standard_reg,
                                         THREAD_NUM=10,
                                         MAX_DEPTH=2)
        spider_standard.BATCH_NUMBER = util.get_day_stamp() + 10750
        spider_standard.OFFSET = offset
        return spider_standard


if __name__ == '__main__':
    SpiderStandard.PUT_IN_STORAGE = False
    SpiderStandard.start_crawling()
