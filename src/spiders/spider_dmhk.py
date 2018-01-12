# -*- coding:utf-8 -*-
import common_news_spider
import util


class SpiderDMHK(common_news_spider.CommonNewsSpider):

    def page_filter(self, doc, url):
        wanted = False
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('div.post_time'):
                    t = util.get_time_string_from_selectors(doc, {'div.post_time'})
                    t_stamp = util.get_timestamp_from_string(t)
                    if t_stamp >= util.get_day_stamp():
                        return True
        return wanted

    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                if doc('div.post_time'):
                    t = util.get_time_string_from_selectors(doc, {'div.post_time'})
                    t_stamp = util.get_timestamp_from_string(t)
                    if t_stamp >= util.get_day_stamp():
                        return True
                    return False
                return True
        return False

    def normal_item_solver(self, item, task, response):

        doc = self.get_doc(response)

        item.raw = doc.text()
        item.title = util.get_filtered_title(doc, {'h1'})
        item.t = util.get_time_string_from_selectors(doc, {'div.post_time'})
        item.t_stamp = util.get_now()
        item.fetched_at = task.feteched_at
        item.category = doc('div.post_cats a:last-child').text()
        item.author = doc('.single_author a').text()
        item.content = util.get_paragraphs_from_selector(doc, 'div.single_text p')
        item.url = task.url
        item.source = 'DMHK'
        item.task_no = self.BATCH_NUMBER

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        dmhk_seed = {'http://news.dmhk.net/'}
        util.add_hrefs('http://news.dmhk.net/', {'#mega_main_menu_ul a'}, dmhk_seed)
        dmhk_reg = {ur'http://news\.dmhk\.net/?p=\d+'}
        spider_dmhk = SpiderDMHK('SpiderDMHK', dmhk_seed, dmhk_reg, THREAD_NUM=5)
        spider_dmhk.BATCH_NUMBER = util.get_day_stamp() + 10230
        return spider_dmhk


if __name__ == '__main__':

    SpiderDMHK.PUT_IN_STORAGE = False
    SpiderDMHK.start_crawling()
