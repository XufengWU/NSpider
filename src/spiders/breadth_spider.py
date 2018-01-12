# -*- coding:utf-8 -*-
import threading
import time
import traceback
import sys
import logging


class BreadthSpider:

    tasks_lock = threading.RLock()
    new_tasks_lock = threading.RLock()
    visited_urls_lock = threading.RLock()
    item_count_lock = threading.RLock()
    logger_con = None
    logger_file = None

    def __init__(self):
        self.name = 'BaseBreadthSpider'
        self.seeds = set()
        self.tasks = set()
        self.new_tasks = set()
        self.visited_urls = set()
        self.item_count = 0
        self.MAX_DEPTH = 1
        self.THREAD_NUM = 1

    class Task:

        def __init__(self):
            self.url = ''
            raise Exception("Not complete definition of class 'Task'. Please extend it.")

    class Fetcher(threading.Thread):

        exception = None
        execute_code = 0
        exception_traceback = None

        def __init__(self, thread_id, caller_instance):
            threading.Thread.__init__(self)
            self.thread_id = thread_id
            self.caller_instance = caller_instance

        def run(self):
            try:
                self.caller_instance.logger_con.info('Starting ' + self.name)
                self.caller_instance.fetch()
                self.caller_instance.logger_con.info(self.name + ' ends.')
            except Exception, e:
                self.exception = e
                self.exception_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
                self.execute_code = -1
                if e.__class__ == KeyboardInterrupt or e.__class__ == SystemExit:
                    raise e

    def get_console_logger(self, console_log_name):
        logger_con = logging.getLogger(console_log_name)
        logger_con.handlers = []
        logger_con.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - " + self.name + ", %(message)s")
        formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        console_handler.setFormatter(formatter)
        logger_con.addHandler(console_handler)
        return logger_con

    def get_file_logger(self, file_log_name, log_file_path):
        logger_file = logging.getLogger(file_log_name)
        logger_file.handlers = []
        logger_file.setLevel(logging.INFO)
        file_handler = logging.FileHandler(filename=log_file_path)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - " + self.name + ", %(message)s")
        formatter.datefmt = '%Y-%m-%d %H:%M:%S'
        file_handler.setFormatter(formatter)
        logger_file.addHandler(file_handler)
        return logger_file

    def solve(self, task, response):
        raise Exception("Unimplemented method 'solve'")

    def fetch(self):
        while True:
            task = self.get_a_task()
            if not task:
                break
            response = self.get_response(task)
            if response:
                self.add_new_urls(task, response)
                if self.item_filter(task, response) and not self.already_solved_task(task, response):
                    try:
                        self.solve(task, response)
                        self.mark_solved(task)
                    except Exception, e:
                        self.logger_con.exception('Error in solving the task of ' + task.url)
                        self.logger_file.exception('Error in solving the task of ' + task.url)
                        raise e
                    else:
                        try:
                            self.item_count_lock.acquire()
                            self.item_count += 1
                        finally:
                            self.item_count_lock.release()

    def get_a_task(self):
        try:
            self.tasks_lock.acquire()
            # if no task to do, return None
            if len(self.tasks) == 0:
                return None
            # else, get a task to do
            task = self.tasks.pop()
            return task
        finally:
            self.tasks_lock.release()

    def create_task(self, url):
        raise Exception("Unimplemented method 'create_task'")

    def get_response(self, task):
        raise Exception("Unimplemented method 'get_response'")

    def add_new_urls(self, task, response):
        urls = self.get_filtered_urls(task, response)
        for url in urls:
            try:
                self.visited_urls_lock.acquire()
                # url not visited before
                if not self.already_visited_url(url, response):
                    # update visited urls
                    self.visited_urls.add(url)
                    new_task = self.create_task(url)
                    # add new task
                    try:
                        self.new_tasks_lock.acquire()
                        self.new_tasks.add(new_task)
                    finally:
                        self.new_tasks_lock.release()
            finally:
                self.visited_urls_lock.release()

    def already_visited_url(self, url, response):
        try:
            self.visited_urls_lock.acquire()
            if url in self.visited_urls:
                return True
            return False
        finally:
            self.visited_urls_lock.release()

    def already_solved_task(self, task, response):
        raise Exception("Unimplemented method 'already_solved_task'")

    def mark_solved(self, task):
        raise Exception("Unimplemented method 'mark_solved'")

    def item_filter(self, task, response):
        raise Exception("Unimplemented method 'item_filter'")

    def get_filtered_urls(self, task, response):
        raise Exception("Unimplemented method 'get_filtered_links'")

    def inject_seed_tasks(self):
        for seed_task in self.seeds:
            self.tasks.add(seed_task)
            self.visited_urls.add(seed_task.url)

    def start(self):
        start_time = time.time()
        self.logger_con.info("start running")
        self.logger_file.info("start running")
        if len(self.seeds) == 0:
            self.logger_con.info("nothing to crawl")
            self.logger_file.info("nothing to crawl")
        depth = 0
        # inject seed tasks
        self.inject_seed_tasks()
        while len(self.tasks) > 0 and depth <= self.MAX_DEPTH:
            self.logger_con.info("start crawling depth: " + str(depth))
            self.logger_file.info("start crawling depth: " + str(depth))
            url_count = len(self.visited_urls)
            item_count_before = self.item_count
            fetcher_threads = []
            # run the fetcher threads
            for i in range(self.THREAD_NUM):
                fetcher_thread = self.Fetcher(thread_id=i, caller_instance=self)
                fetcher_thread.name = 'Fetcher-' + str(i)
                fetcher_threads.append(fetcher_thread)
                fetcher_thread.start()
            for t in fetcher_threads:
                t.join()
                if t.execute_code == -1:
                    self.logger_con.exception("exception occurred in " + t.name)
                    self.logger_file.exception("exception occurred in " + t.name)
                    self.logger_con.exception(t.exception_traceback)
                    self.logger_file.exception(t.exception_traceback)
                    if t.exception.__class__ is KeyboardInterrupt:  # or SystemExit:
                        raise t.exception
            self.logger_con.info(
                "completed depth: " + str(depth) + ", crawled items: " + str(self.item_count - item_count_before) +
                ", added urls: " + str(len(self.visited_urls) - url_count) + ", to-visit urls: " + str(
                    len(self.new_tasks)))
            self.logger_file.info(
                "completed depth: " + str(depth) + ", crawled items: " + str(self.item_count - item_count_before) +
                ", added urls: " + str(len(self.visited_urls) - url_count) + ", to-visit urls: " + str(
                    len(self.new_tasks)))
            self.tasks = self.new_tasks
            self.new_tasks = set()
            depth += 1
        self.logger_con.info("end running")
        self.logger_file.info("end running")
        self.logger_con.info("total crawled items: " + str(self.item_count) +
                             ", total scanned urls: " + str(len(self.visited_urls)) +
                             ", total running time: " + str(time.time() - start_time) + " seconds")
        self.logger_file.info("total crawled items: " + str(self.item_count) +
                              ", total scanned urls: " + str(len(self.visited_urls)) +
                              ", total running time: " + str(time.time() - start_time) + " seconds")


class MySpider(BreadthSpider):

    class Task(BreadthSpider.Task):
        def __init__(self):
            self.url = 'a'
            self.task_type = 'nothing'
        pass


if __name__ == '__main__':
    spider = MySpider()
    spider.seeds = {spider.Task()}
    spider.start()
