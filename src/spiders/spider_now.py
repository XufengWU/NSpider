# -*- coding:utf-8 -*-
import common_news_spider
import util
import re


complete_pattern = re.compile(ur'http://.+')
date_pattern = re.compile(ur'\d{4}-\d\d-\d\d')
cat_pattern_in_url = re.compile(ur'(?<=home/).+?(?=/)')
id_string_pattern = re.compile(ur'newsId=\d+')
prefix = 'https://news.now.com'


class SpiderNow(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        if u is not None:
            if not complete_pattern.match(u):
                u = prefix + u
        else:
            u = ''
        if id_string_pattern.findall(u):
            id_string = id_string_pattern.findall(u)[0]
            u = re.sub(ur'newsId=\d+.*', id_string, u)
        return u

    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                # t = doc('time.published').text()
                t_stamp = util.get_timestamp_from_string(doc('time.published').attr('datetime'), '%Y-%m-%d %H:%M:%S+0800')
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if not reg_pattern.match(doc_url):
                    return True
                # t = doc('time.published').text()
                t_stamp = util.get_timestamp_from_string(doc('time.published').attr('datetime'), '%Y-%m-%d %H:%M:%S+0800')
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
                return False
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('time.published').text()
        t_stamp = util.get_timestamp_from_string(doc('time.published').attr('datetime'), '%Y-%m-%d %H:%M:%S+0800')
        category = doc('#navBar li.active').text()
        if category == '' and cat_pattern_in_url.findall(task.url):
            category = cat_pattern_in_url.findall(task.url)[0]
        author = ''
        content = util.get_paragraphs_from_selector(doc, 'div.newsLeading p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, 'div.newsLeading')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'NowNews'
        item.task_no = self.BATCH_NUMBER
        if util.within_active_interval(6, 1200):
            _comments = util.get_filtered_facebook_comments_data('515076798590105',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        now_seed = {'https://news.now.com/home'}
        util.add_hrefs('https://news.now.com/home', {'#navBar a'}, now_seed, seed_patterns={re.compile(r'/home/.+')}, prefix=prefix)
        spider_now = SpiderNow('SpiderNow',
                               now_seed,
                               {ur'https://news\.now\.com/.+newsId=\d+.+'},
                               THREAD_NUM=10)
        spider_now.BATCH_NUMBER = util.get_day_stamp() + 10280
        spider_now.OFFSET = offset
        return spider_now


if __name__ == '__main__':

    SpiderNow.PUT_IN_STORAGE = False
    SpiderNow.start_crawling()
