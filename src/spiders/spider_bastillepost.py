# -*- coding:utf-8 -*-
import common_news_spider
import util
import requests
from pyquery import PyQuery as pq
import re
import time


prefix = u'http://www.bastillepost.com'
complete_pattern = re.compile(ur'(http|https)://.+')


class SpiderBastillePost(common_news_spider.CommonNewsSpider):

    def get_links(self, doc, url=''):
        return doc('a, div').items()

    def get_url_of_link(self, link, doc, doc_url):
        u = ''
        if link.attr('href'):
            u = link.attr('href')
        elif link.attr('data-href'):
            u = link.attr('data-href')
        if u is not '' and not complete_pattern.match(u):
            u = prefix + u
        return u

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('p.dateFormat'):
                    t = util.get_time_string_from_selectors(doc, {'p.dateFormat'})
                    t_stamp = util.get_timestamp_from_string(t)
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        return True
        return wanted

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('p.dateFormat'):
                    t = util.get_time_string_from_selectors(doc, {'p.dateFormat'})
                    t_stamp = util.get_timestamp_from_string(t)
                    if t_stamp >= util.get_day_stamp(self.OFFSET):
                        return True
                    return False
                return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'title'}, ur' \| .*')
        t = util.get_time_string_from_selectors(doc, {'p.dateFormat'})
        t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
        category = ''
        if re.findall(ur'(?<=hongkong/)\d+-.+?(?=/\d+.*)', task.url):
            cat_part = re.findall(ur'(?<=hongkong/)\d+-.+?(?=/\d+.*)', task.url)[0]
            category = re.findall(ur'(?<=-).*', cat_part)[0]
        if re.findall(ur'(?<= \| ).+?(?= \| 巴士的報)', doc('title').text()):
            category = re.findall(ur'(?<= \| ).+?(?= \| 巴士的報)', doc('title').text())[0]
        author = doc('.articleauthor-name').text()
        content = util.get_paragraphs_from_selector(doc, '#boxArticleContent p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '#articleContent p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'BastillePost'
        item.task_no = self.BATCH_NUMBER
        if util.within_active_interval(6, 1200):
            _comments = util.get_filtered_facebook_comments_data('617988554913649',
                                                                 doc('#fbComments').attr('href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        bastille_seed = {'http://www.bastillepost.com/hongkong/'}
        r = requests.get('http://www.bastillepost.com/hongkong/')
        d = pq(r.text)
        for cat in d('#headerMenuWrap div').items():
            if cat.attr('onclick'):
                onclick = cat.attr('onclick')
                if re.findall(r'(?<=\').+?(?=\')', onclick):
                    href = prefix + re.findall(r'(?<=\').+?(?=\')', onclick)[0]
                    bastille_seed.add(href)
        bastille_reg = {ur'http://www\.bastillepost\.com/.+/\d{4,}-.*'}
        spider_bastille = SpiderBastillePost('SpiderBastillePost',
                                             bastille_seed,
                                             bastille_reg,
                                             THREAD_NUM=5)
        spider_bastille.BATCH_NUMBER = util.get_day_stamp() + 10210
        spider_bastille.OFFSET = offset
        return spider_bastille


if __name__ == '__main__':

    SpiderBastillePost.PUT_IN_STORAGE = False
    SpiderBastillePost.DEFAULT_PUT_IN_FILE = True
    SpiderBastillePost.start_crawling(offset=100, MAX_DEPTH=3)
