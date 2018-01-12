# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import copy
import requests
from pyquery import PyQuery as pq

complete_pattern = re.compile(ur'http://.+')
cat_page_pattern = re.compile(ur'http://www\.inmediahk\.net/taxonomy/term/\d+')
ymd = util.get_current_ymd_string_list()
today_date_pattern = re.compile(ymd[0] + '-' + ymd[1] + '-' + ymd[2])
date_pattern = re.compile(ur'\d{4}-\d\d-\d\d')
prefix = 'http://www.inmediahk.net'


class SpiderInMedia(common_news_spider.CommonNewsSpider):
    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = util.get_time_string_from_selectors(doc, {'span.date'}, {date_pattern})
                t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d')
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                t = util.get_time_string_from_selectors(doc, {'span.date'}, {date_pattern})
                t_stamp = util.get_timestamp_from_string(t, '%Y-%m-%d')
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = util.get_time_string_from_selectors(doc, {'span.date'}, {date_pattern})
        t_stamp = util.get_timestamp_from_string(t)
        category = doc('.post-cat').text()
        author = doc('.post-meta .author').text()
        content = util.get_paragraphs_from_selector(doc, 'div.post-desc p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, 'div.post-desc')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'InMedia'
        item.task_no = self.BATCH_NUMBER
        if util.within_active_interval(6, 1200):
            _comments = util.get_filtered_facebook_comments_data('408250695928069',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        print 'Initiating spider'
        inmedia_seed = {
            'http://www.inmediahk.net/',
            'http://www.inmediahk.net/taxonomy/term/5034',
            'http://www.inmediahk.net/taxonomy/term/510975',
            'http://www.inmediahk.net/taxonomy/term/5043',
            'http://www.inmediahk.net/taxonomy/term/513024',
            'http://www.inmediahk.net/taxonomy/term/513025',
            'http://www.inmediahk.net/taxonomy/term/5018',
            'http://www.inmediahk.net/taxonomy/term/5030',
            'http://www.inmediahk.net/taxonomy/term/5027'
        }
        # util.add_hrefs('http://www.inmediahk.net/', {'#nav-item a'}, inmedia_seed)
        # _seed = copy.deepcopy(inmedia_seed)
        # for seed in _seed:
        #     if cat_page_pattern.match(seed):
        #         i = 0
        #         _s = seed + '?page=' + str(i)
        #         r = requests.get(_s)
        #         d = pq(r.text)
        #         dates = d('article p.date').text()
        #         print dates
        #         if re.findall(today_date_pattern, dates):
        #             inmedia_seed.add(_s)
        #             i += 1
        #         else:
        #             break

        spider_inmedia = SpiderInMedia('SpiderInMedia', inmedia_seed,
                                       {ur'http://www\.inmediahk\.net/node/\d+'},
                                       THREAD_NUM=5)
        spider_inmedia.BATCH_NUMBER = util.get_day_stamp() + 10270
        spider_inmedia.OFFSET = offset
        print 'Initiating done'
        return spider_inmedia


if __name__ == '__main__':
    SpiderInMedia.PUT_IN_STORAGE = False
    SpiderInMedia.start_crawling()
