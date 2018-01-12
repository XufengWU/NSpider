# -*- coding:utf-8 -*-
import base_news_spider
import pyquery
import requests
import re
import storage
import util
import breadth_spider
import config
import codecs
import json
import threading
import logging


class CommonNewsSpider(base_news_spider.BaseNewsSpider):

    PUT_IN_STORAGE = False
    DEFAULT_PUT_IN_FILE = False
    ADD_MEDIA = False

    output_file_lock = threading.Lock()

    def __init__(self, name='CommonNewSpider', seed_urls=set(), regs=set(), MAX_DEPTH=1, THREAD_NUM=1, OFFSET=0):
        base_news_spider.BaseNewsSpider.__init__(self, seed_urls=seed_urls, MAX_DEPTH=MAX_DEPTH, THREAD_NUM=THREAD_NUM)
        self.name = name
        self.regs = regs
        self.reg_patterns = self.compile_patterns(regs)
        self.AUTO_FILTER_URL_PARAS = False
        self.OFFSET = OFFSET
        self.BATCH_NUMBER = 0
        self.logger_con = self.get_console_logger(config.COMMON_NEWS_SPIDER_CONSOLE_LOG_NAME)
        self.logger_file = self.get_file_logger(config.COMMON_NEWS_SPIDER_FILE_LOG_NAME, config.COMMON_NEWS_SPIDER_LOG_FILE_PATH)
        self.PUT_IN_FILE = self.DEFAULT_PUT_IN_FILE
        self.OUTPUT_FILE_PATH = None

    class NewsItem:

        def __init__(self):
            self.raw = ''
            self.title = ''
            self.t = ''
            self.category = ''
            self.fetched_at = 0
            self.t_stamp = 0
            self.author = ''
            self.content = ''
            self.url = ''
            self.source = ''
            self.task_no = 0
            self.media_list = []

        class MediaItem:

            def __init__(self, media_url='', type='', description='', created_at=0):
                self.media_url = media_url
                self.type = type
                self.description = description
                self.created_at = created_at

    def start(self):
        self.logger_con.info('batch number: ' + str(self.BATCH_NUMBER))
        self.logger_file.info('batch number: ' + str(self.BATCH_NUMBER))
        breadth_spider.BreadthSpider.start(self)

    def compile_patterns(self, regs):
        patterns = set()
        for reg in regs:
            patterns.add(re.compile(reg))
        return patterns

    # define the patterns of different tasks
    def define_task_types(self, types):
        for key, value in types.iteritems():
            try:
                pattern = re.compile(key)
            except Exception, e:
                self.logger_con.exception(e)
                self.logger_file.exception(e)
                self.logger_con.exception('Please give correct regular expressions of task types keys.')
                self.logger_file.exception('Please give correct regular expressions of task types keys.')
            else:
                self.task_types_dict[pattern] = value

    def auto_task_type(self, url):
        if self.task_types_dict == {}:
            return self.DEFAULT_TASK_TYPE
        else:
            for task_pattern, task_type in self.task_types_dict.iteritems():
                if task_pattern.match(url):
                    return task_type
            return 'unknown'

    def send_request(self, task):
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        task.fetched_at = util.get_now()
        return r

    # get parsed document from the response
    def get_doc(self, response):
        return pyquery.PyQuery(response.text)

    # extract link elements from the parsed document
    def get_links(self, doc, url=''):
        return doc('a').items()

    # get url from the link element
    def get_url_of_link(self, link, doc, doc_url):
        if link.attr('href'):
            return link.attr('href')
        return ''

    # determine whether the url is a wanted task
    def task_filter(self, doc, url, doc_url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                return True
        return False

    # get filtered urls for next round fetching
    def get_filtered_urls(self, task, response):
        doc = self.get_doc(response)
        urls = set()
        for link in self.get_links(doc):
            u = self.get_url_of_link(link, doc, task.url)
            u = util.url_para_filter(u, self.AUTO_FILTER_URL_PARAS)
            if u and self.task_filter(doc, u, task.url):
                urls.add(u)
        return urls

    # filter out wanted page as wanted items to solve
    def page_filter(self, doc, url):
        for reg_pattern in self.reg_patterns:
            if reg_pattern.match(url):
                return True
        return False

    # filter out wanted items to solve
    def item_filter(self, task, response):
        doc = self.get_doc(response)
        return self.page_filter(doc, task.url)

    # check whether the task was solved
    def already_solved_task(self, task, response):
        if not self.PUT_IN_STORAGE:
            if task.url == task.redirected_url or not self.already_visited_url(task.redirected_url, response):
                return False
            else:
                self.logger_con.debug('already fetched before: ' + task.url)
                return True
        else:
            if self.ADD_MEDIA:
                return False
        if storage.url_exists(task.url) or (task.url != task.redirected_url and self.already_visited_url(task.redirected_url, response)):
                self.logger_con.debug('already exists: ' + task.url)
                return True
        return False

    # solve the item of 'normal' type task
    def normal_item_solver(self, item, task, response):
        self.logger_con.info("Please define your own method of 'normal_solve_item'")
        self.logger_file.info("Please define your own method of 'normal_solve_item'")

    # persist the item of 'normal' type task
    def normal_item_persistence(self, item, task, response):
        doc_url = task.url
        if self.PUT_IN_STORAGE:
            if not storage.url_exists(item.url):
                storage.add_page(raw=item.raw, title=item.title, category=item.category, crawled_at=item.fetched_at,
                                 created_at=item.t_stamp,
                                 author=item.author, text=item.content, url=item.url, source=item.source, task_no=item.task_no)
                self.logger_con.debug("put in storage: " + doc_url)
            if self.ADD_MEDIA:
                for media in item.media_list:
                    if not storage.media_exists(page_url=item.url, media_url=media.media_url):
                        try:
                            storage.add_media(page_url=item.url, media_url=media.media_url, description=media.description,
                                              media_type=media.type, created_at=media.created_at, source=item.source)
                            self.logger_con.debug("media put in storage: " + media.media_url + ' of ' + doc_url)
                        except Exception, e:
                            self.logger_con.error('add media error: ' + e.message + " : " + media.media_url + ' of ' + doc_url)
                            self.logger_file.error('add media error: ' + e.message + " : " + media.media_url + ' of ' + doc_url)
                    else:
                        self.logger_con.debug('media already exists: ' + media.media_url + ' : ' + item.url)
        self.logger_con.debug(item.url)
        for media in item.media_list:
            self.logger_con.debug('media: ' + media.media_url + ' of ' + doc_url)
            self.logger_con.debug('type: ' + media.type + ' description: ' + media.description)
        self.logger_con.debug(item.title)
        self.logger_con.debug(item.t)
        self.logger_con.debug(item.t_stamp)
        if item.author is not '':
            self.logger_con.debug(item.author)
        self.logger_con.debug(item.category)
        self.logger_con.debug(item.content)

    # check whether the item is qualified to be stored
    def normal_item_check(self, item, task, response):
        doc_url = task.url
        if item.t == '':
            self.logger_con.warning('NO TIME: ' + doc_url)
            self.logger_file.warning('NO TIME: ' + doc_url)
            return False
        if item.title == '':
            self.logger_con.warning('NO TITLE: ' + doc_url)
            self.logger_file.warning('NO TITLE: ' + doc_url)
            return False
        if item.category == '':
            self.logger_con.warning('NO CAT: ' + doc_url)
            self.logger_file.warning('NO CAT: ' + doc_url)
        if item.content == '':
            self.logger_con.warning('NO CONTENT: ' + doc_url)
            self.logger_file.warning('NO CONTENT: ' + doc_url)
            return False
        return True

    # output the item as file
    def normal_item_file_output(self, item, task, response):
        if self.PUT_IN_FILE:
            if not self.OUTPUT_FILE_PATH:
                file_path = self.__class__.__name__ + '_' + util.get_day_string() + '.json'
            else:
                file_path = self.OUTPUT_FILE_PATH
            with self.output_file_lock:
                item_list = []
                try:
                    with codecs.open(file_path, 'r', encoding='utf-8') as fr:
                        item_list = json.load(fr)
                except Exception:
                    print 'ERROR IN READING FILE'
                    with codecs.open(file_path, 'w', encoding='utf-8') as fw:
                        fw.close()
                try:
                    with codecs.open(file_path, 'w', encoding='utf-8') as fw:
                        item_dict = item.__dict__
                        _item_exists = False
                        for _item in item_list:
                            if _item['title'] == item.title:
                                _item_exists = True
                                break
                        if not _item_exists:
                            item_list.append({'title': item.title, 'source': item.source, 'category': item.category, 'content': item.content})
                            json.dump(item_list, fw)
                        fw.close()
                except Exception:
                    raise

    # the solver for 'normal' type tasks
    def normal_solver(self, task, response):
        news_item = self.NewsItem()
        # solve the item here
        self.normal_item_solver(news_item, task, response)
        # ensure the item is qualified
        if self.normal_item_check(news_item, task, response):
            # persist the item here
            self.normal_item_persistence(news_item, task, response)
            # output the item as file if necessary
            self.normal_item_file_output(news_item, task, response)
        else:
            with self.item_count_lock:
                self.item_count -= 1

    def mark_solved(self, task):
        try:
            self.visited_urls_lock.acquire()
            self.visited_urls.add(task.redirected_url)
        finally:
            self.visited_urls_lock.release()

    @classmethod
    def get_auto_configured_spider(cls, offset=0):
        raise Exception("Umimplemented method 'get_auto_configured_spider'")

    @classmethod
    def start_crawling(cls, offset=0, **kwargs):
        _spider = cls.get_auto_configured_spider(offset=offset)
        for kw in kwargs:
            if hasattr(_spider, kw):
                _spider.__dict__[kw] = kwargs[kw]
            if kw == 'seed_urls':
                _spider.seeds = _spider.create_seed_tasks(kwargs[kw])
        _spider.start()
        return _spider

if __name__ == '__main__':

    seed_urls = {'http://xufeiwu.com'}
    spider = CommonNewsSpider(seed_urls=seed_urls, regs={r'.*Me.*'})
    spider.start()

