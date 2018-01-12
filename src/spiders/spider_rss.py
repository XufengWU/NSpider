# -*- coding:utf-8 -*-
import common_news_spider
import util
import feedparser


class SpiderRSS(common_news_spider.CommonNewsSpider):

    outer_spider_module = None
    outer_spider_class = None

    def __init__(self, name='RSSNewsSpider', seed_urls=set(), regs=set(), MAX_DEPTH=1, THREAD_NUM=1, OFFSET=0):
        common_news_spider.CommonNewsSpider.__init__(self, name=name, seed_urls=seed_urls, regs=regs, MAX_DEPTH=MAX_DEPTH, THREAD_NUM=THREAD_NUM, OFFSET=OFFSET)
        self.rss_added_urls = set()

    def add_new_urls(self, task, response):
        pass

    def item_filter(self, task, response):
        return True

    def normal_solver(self, task, response):
        doc = feedparser.parse(response.text)
        if not self.outer_spider_module:
            for item in doc.entries:
                news_item = self.NewsItem()
                news_task = self.create_task(item.link)
                if not self.already_solved_task(news_task, item):
                    self.normal_item_solver(news_item, news_task, item, rss_doc=doc)
                    if self.normal_item_check(news_item, news_task, item):
                        self.normal_item_persistence(news_item, news_task, item)
                    with self.item_count_lock:
                        self.item_count += 1
                with self.visited_urls_lock:
                    self.visited_urls.add(item.link)
                    self.rss_added_urls.add(item.link)
        else:
            for item in doc.entries:
                with self.visited_urls_lock:
                    self.visited_urls.add(item.link)
                    self.rss_added_urls.add(item.link)

    def normal_item_solver(self, item, task, response, **kwargs):
        item.url = response.link
        item.title = response.title
        item.content = response.description
        if hasattr(response, 'published'):
            item.t = response.published
            item.t_stamp = util.get_timestamp_from_string(item.t)
        if hasattr(response, 'category'):
            item.category = response.category
        else:
            item.category = kwargs['rss_doc'].channel.title

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        # seed = {'http://feeds.initium.news/theinitium'}
        # outer_spider_class = 'spider_initium.SpiderInitium'
        # SpiderRSS.outer_spider_class = outer_spider_class
        rss_seed = set()
        spider_rss = SpiderRSS('SpiderRSS',
                               rss_seed,
                               {ur'.+'},
                               THREAD_NUM=5,
                               MAX_DEPTH=0)
        spider_rss.OFFSET = offset
        spider_rss.BATCH_NUMBER = util.get_day_stamp() + 10610
        return spider_rss
        # if SpiderRSS.outer_spider_class:
        #     spider_class = __import__(outer_spider_class)
        #     outer_spider = spider_class('OuterSpider',
        #                                 spider_rss.visited_urls,
        #                                 {ur'.+'},
        #                                 THREAD_NUM=5,
        #                                 MAX_DEPTH=1)
        #     outer_spider.start()

    @classmethod
    def start_crawling(cls, offset=0, **kwargs):
        _spider = cls.get_auto_configured_spider(offset=offset)
        for kw in kwargs:
            if hasattr(_spider, kw):
                _spider.__dict__[kw] = kwargs[kw]
            if kw == 'seed_urls':
                _spider.seeds = _spider.create_seed_tasks(kwargs[kw])
        _spider.start()
        if _spider.outer_spider_module:
            module_levels = _spider.outer_spider_module.split('.')
            _outer_spider_module = __import__(_spider.outer_spider_module)
            for _m in module_levels[1:]:
                _outer_spider_module = _outer_spider_module.__dict__[_m]
            _outer_spider_class = _outer_spider_module.__dict__[_spider.outer_spider_class]
            _spider.logger_con.info('turning to outer spider: ' + _spider.outer_spider_module + '.' + _spider.outer_spider_class)
            if 'seed_urls' in kwargs:
                kwargs.pop('seed_urls')
            return _outer_spider_class.start_crawling(offset=offset, seed_urls=_spider.rss_added_urls, **kwargs)
        return _spider


if __name__ == '__main__':
    SpiderRSS.PUT_IN_STORAGE = False
    _s = SpiderRSS.start_crawling(seed_urls={'http://www.hkgolden.com/RSS10.aspx'},
                                  outer_spider_module='spider_golden',
                                  outer_spider_class='SpiderGolden')
