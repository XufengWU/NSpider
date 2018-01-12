# -*- coding:utf-8 -*-
import common_news_spider
import util
import re

news_prefix = 'http://www.news.cn/gangao/'


class SpiderXinhua(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):

        response.encoding = 'utf-8'
        doc = self.get_doc(response)

        title = doc('h1').text()
        t = doc('span.time').text()
        if t == '':
            t = doc('#pubtime').text()
        t_stamp = util.get_timestamp_from_string(t)
        category = '港澳'
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.article p')
        if content == '':
            content = util.get_paragraphs_from_selector(doc, '#content p')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'Xinhua'
        item.task_no = self.BATCH_NUMBER
        for img in doc('.article img').items():
            if img.attr('src') != '':
                media_u = re.sub(r'/[^/]+\.htm', '/', task.url) + img.attr('src')
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
        xinhua_seed = {'http://www.news.cn/gangao/index.htm', 'http://www.news.cn/gangao/jsxw.htm'}
        util.add_hrefs('http://www.news.cn/gangao/index.htm', {'.nav.domPC a'}, xinhua_seed, news_prefix)
        day_str = util.get_day_string('-', offset=offset)
        day_str = day_str[:-3] + '/' + day_str[-2:]
        spider_xinhua = SpiderXinhua('SpiderXinhua',
                                     xinhua_seed,
                                     {ur'http://news\.xinhuanet\.com/gangao/' + day_str + '.+'},
                                     THREAD_NUM=5)
        spider_xinhua.OFFSET = offset
        spider_xinhua.BATCH_NUMBER = util.get_day_stamp() + 10430
        return spider_xinhua


if __name__ == '__main__':
    SpiderXinhua.PUT_IN_STORAGE = False
    SpiderXinhua.start_crawling()
