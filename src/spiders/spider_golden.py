# -*- coding:utf-8 -*-
import common_news_spider
import util
import time
import re


class SpiderGolden(common_news_spider.CommonNewsSpider):

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = ''
                t_stamp = 0
                for _div in doc('h1').siblings('div').items():
                    if _div.css('color') == 'rgb(128, 128, 128)':
                        t = _div.text()
                        t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
                        break
                if t_stamp >= util.get_day_stamp(self.OFFSET):
                    return True
        return wanted

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                t = ''
                t_stamp = 0
                for _div in doc('h1').siblings('div').items():
                    if _div.css('color') == 'rgb(128, 128, 128)':
                        t = _div.text()
                        t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
                        if t_stamp >= util.get_day_stamp(self.OFFSET):
                            return True
                        return False
                return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        title = util.get_filtered_title(doc, {'h1'})
        t_divs = doc('h1').siblings('div').items()
        t = ''
        t_stamp = 0
        for _div in t_divs:
            if _div.css('color') == 'rgb(128, 128, 128)':
                t = _div.text()
                t_stamp = util.get_timestamp_from_string(t) + int(time.localtime().tm_sec)
                break
        category = u'电子'
        author = ''
        content = util.get_paragraphs_from_selector(doc, '.href_txt_blog2')

        item.raw = doc.text()
        item.title = title
        item.t = t
        item.t_stamp = t_stamp
        item.fetched_at = task.fetched_at
        item.category = category
        item.author = author
        item.content = content
        item.url = task.url
        item.source = 'HKGolden'
        item.task_no = self.BATCH_NUMBER
        # if util.within_active_interval(6, 1200):
        #     _comments = util.get_filtered_facebook_comments_data('482092838576644',
        #                                                          doc('div.fb-comments').attr('data-href'), task.url)
        #     if _comments:
        #         for _comment in _comments:
        #             item.media_list.append(
        #                 self.NewsItem.MediaItem(media_url=_comment['json_string'], type='comments',
        #                                         description='comments', created_at=item.fetched_at)
        #             )

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        golden_seed = {'http://www.hkgolden.com/'}
        golden_reg = {ur'http://www\.hkgolden\.com/articles/.+'}
        spider_golden = SpiderGolden('SpiderGolden',
                                     golden_seed,
                                     golden_reg,
                                     THREAD_NUM=5)
        spider_golden.BATCH_NUMBER = util.get_day_stamp() + 10620
        spider_golden.OFFSET = offset
        return spider_golden


if __name__ == '__main__':

    SpiderGolden.PUT_IN_STORAGE = False
    SpiderGolden.start_crawling()
