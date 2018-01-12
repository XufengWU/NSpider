# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re


class SpiderHKFP(common_news_spider.CommonNewsSpider):

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t = doc('meta[property="article:published_time"]').attr('content')
        if t:
            t_stamp = util.get_timestamp_from_string(t) + 8 * 3600
        else:
            t_stamp = 0
        cats = doc('#main .entry-header .meta-category a').items()
        category = ''
        for c in cats:
            category += c.text() + ', '
        category = category[:-2]
        author = doc('#main .meta-item.author').text()
        content = util.get_paragraphs_from_selector(doc, 'div.entry-content p:not(.wp-caption-text)')
        content = re.sub(r'Comments$', '', content)

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKFP'
        item.task_no = self.BATCH_NUMBER
        for img in doc('div.entry-content img').items():
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
        hkfp_seed = {'https://www.hongkongfp.com/'
                     'https://www.hongkongfp.com/hong-kong-news/',
                     'https://www.hongkongfp.com/china-news/',
                     'https://www.hongkongfp.com/comment-analysis/',
                     'https://www.hongkongfp.com/hkfp-voices/',
                     'https://www.hongkongfp.com/category/hkfp-lens/'}
        hkfp_reg = {ur'https://www.hongkongfp.com/'+util.get_day_string(interval_str='/', offset=offset)+u'/.+'}
        spider_hkfp = SpiderHKFP('SpiderHKFP',
                                 hkfp_seed,
                                 hkfp_reg,
                                 THREAD_NUM=10,
                                 MAX_DEPTH=1)
        spider_hkfp.BATCH_NUMBER = util.get_day_stamp() + 10720
        spider_hkfp.OFFSET = offset
        return spider_hkfp


if __name__ == '__main__':

    SpiderHKFP.PUT_IN_STORAGE = False
    SpiderHKFP.start_crawling()
