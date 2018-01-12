# -*- coding:utf-8 -*-
import common_news_spider
import util
import re
import time


complete_pattern = re.compile(ur'http://sina\.com\.hk/.*')
cat_pattern = re.compile(ur'(?<=unikeyword=\').*?(?=\')')


class SpiderVJMedia(common_news_spider.CommonNewsSpider):

    def get_url_of_link(self, link, doc, doc_url):
        u = link.attr('href')
        u = re.sub(ur'#facebook-comments', u'', u)
        return u

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1 a'})
        t = util.get_time_string_from_selectors(doc, {'span.postdate'})
        t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
        category = doc('span.postcat a').text()
        author = doc('span.postauthor a').text()
        content = util.get_paragraphs_from_selector(doc, 'div p')
        content = re.sub(ur'投稿:[.\n\r\t]*.*', u'', content, re.M | re.U | re.I)
        content = re.sub(ur'則留言[.\n\r\t]*', u'', content, re.M | re.U | re.I)
        content = re.sub(ur'大道之行也，天下為公，選賢與能，講信修睦。－－－《禮運．大同》[.\n\r\t]*', u'', content, re.M | re.U | re.I)

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'VJMedia'
        item.task_no = self.BATCH_NUMBER
        for img in doc('#container img.size-full, #container img.size-large').items():
            if img.attr('src') != '':
                des = ''
                if img.attr('alt'):
                    des = img.attr('alt')
                elif img.siblings('p'):
                    des = img.siblings('p').text()
                media = self.NewsItem.MediaItem(media_url=img.attr('src'), type='image', description=des,
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        for iframe in doc('iframe').items():
            if iframe.attr('src') and re.match(r'.*youtube\.com.+', iframe.attr('src')):
                media = self.NewsItem.MediaItem(media_url=iframe.attr('src'), type='youtube', description='youtube',
                                                created_at=item.fetched_at)
                item.media_list.append(media)
        if util.within_active_interval(6, 1200):
            _comments = util.get_filtered_facebook_comments_data('214585295294555',
                                                                 doc('div.fb-comments').attr('data-href'), task.url)
            if _comments:
                for _comment in _comments:
                    item.media_list.append(
                        self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
                                                description='comments', created_at=item.fetched_at)
                    )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        vj_seed = {'http://www.vjmedia.com.hk/'}
        util.add_hrefs(url='http://www.vjmedia.com.hk/',
                       selectors={'ul.mainnav.dropdown li a'},
                       seeds=vj_seed)
        vj_reg = {ur'http://www.vjmedia.com.hk/articles/' +
                  util.get_day_string(interval_str='/', offset=offset) +
                  '/.+'}
        spider_vj = SpiderVJMedia('SpiderVJMedia',
                                  vj_seed,
                                  vj_reg,
                                  THREAD_NUM=10)
        spider_vj.OFFSET = offset
        spider_vj.BATCH_NUMBER = util.get_day_stamp() + 10180
        return spider_vj


if __name__ == '__main__':

    SpiderVJMedia.PUT_IN_STORAGE = False
    SpiderVJMedia.start_crawling()
