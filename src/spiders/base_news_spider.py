# -*- coding:utf-8 -*-
import breadth_spider
import requests
import time


class BaseNewsSpider(breadth_spider.BreadthSpider):

    def __init__(self, name='BaseNewSpider', seed_urls=set(), MAX_DEPTH=1, THREAD_NUM=1):
        breadth_spider.BreadthSpider.__init__(self)
        self.name = name
        self.MAX_DEPTH = MAX_DEPTH
        self.THREAD_NUM = THREAD_NUM
        self.task_types_dict = {}
        self.DEFAULT_TASK_TYPE = 'normal'
        self.Task.default_task_type = self.DEFAULT_TASK_TYPE
        self.RESPONSE_TIMEOUT_VALUE = 20
        self.FETCH_DELAY = 0
        self.RETRY_TIMES = 3
        self.seeds = self.create_seed_tasks(seed_urls)

    class Task(breadth_spider.BreadthSpider.Task):

        default_task_type = None

        def __init__(self, **kwargs):
            self.url = kwargs['url']
            self.redirected_url = kwargs['url']
            if 'task_type' in kwargs:
                self.task_type = kwargs['task_type']
            else:
                self.task_type = self.default_task_type

        def set_task_type(self, task_type):
            self.task_type = task_type

    # define the patterns of different tasks
    def define_task_types_dict(self, types):
        raise Exception("Unimplemented method 'define_task_types_dict'")

    # automatically determine the task type from url
    def auto_task_type(self, url):
        raise Exception("Unimplemented method 'auto_task_type'")

    def create_task(self, url, task_type=None):
        if not task_type:
            return self.Task(url=url, task_type=self.auto_task_type(url))
        return self.Task(url=url, task_type=task_type)

    def create_seed_tasks(self, urls):
        seed_tasks = set()
        for seed_url in urls:
            seed_tasks.add(self.create_task(seed_url))
        return seed_tasks

    # request with specific parameters
    def send_request(self, task):
        return requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)

    def get_response(self, task):
        retry = 1
        response = None
        while (not response or response.status_code != 200) and retry <= self.RETRY_TIMES:
            time.sleep(self.FETCH_DELAY)
            try:
                self.logger_con.info('Fetching ' + task.url)
                response = self.send_request(task)
            # no response
            except Exception, e:
                self.logger_con.error(e)
                self.logger_file.error(e)
                if e.__class__ == requests.ConnectionError:
                    self.logger_con.error('connection error:' + task.url + ', retry times: ' + str(retry))
                    self.logger_file.error('connection error:' + task.url + ', retry times: ' + str(retry))
                elif e.__class__ == requests.exceptions.ChunkedEncodingError:
                    self.logger_con.error('chunked encoding error: ' + task.url + ', retry times: ' + str(retry))
                    self.logger_file.error('chunked encoding error: ' + task.url + ', retry times: ' + str(retry))
                retry += 1
            else:
                if not response:
                    self.logger_con.exception(
                        'None response error: ' + task.url + ', retry times: ' + str(retry))
                    self.logger_file.exception(
                        'None response error: ' + task.url + ', retry times: ' + str(retry))
                    retry += 1
                else:
                    if response.url != task.url:
                        self.logger_con.info(task.url + ' was redirected to ' + response.url)
                        self.logger_file.info(task.url + ' was redirected to ' + response.url)
                        task.redirected_url = response.url
                    if response.status_code != 200:
                        self.logger_con.exception(
                            'HTTP error: ' + str(response.status_code) + ', retry times: ' + str(retry))
                        self.logger_file.exception(
                            'HTTP error: ' + str(response.status_code) + ', retry times: ' + str(retry))
                        # adjust the task if necessary
                        self.adjust_task(task)
                        retry += 1
        # the request failed
        if retry > self.RETRY_TIMES:
            self.logger_con.info('task failure, max retry times of ' + str(self.RETRY_TIMES) + ' exceeded: ' + task.url)
            self.logger_file.info('task failure, max retry times of ' + str(self.RETRY_TIMES) + ' exceeded: ' + task.url)
        # the request succeeded
        elif response:
            '''
            # the url was redirected
            if response.url != task.url:
                # add new url to visited urls
                try:
                    self.visited_urls_lock.acquire()
                    self.visited_urls.add(response.url)
                finally:
                    self.visited_urls_lock.release()
            '''
            self.logger_con.info('task success: ' + response.url)
        return response

    # adjust task after getting the feedback information from server
    def adjust_task(self, task):
        pass

    # default solver for default task type
    def normal_solver(self, task, response):
        self.logger_con.info("Please define your own method 'normal_solver'")
        self.logger_con.info("Please define your own method 'normal_solver'")

    def solve(self, task, response):
        if task.task_type == self.DEFAULT_TASK_TYPE:
            self.normal_solver(task, response)
        else:
            if task.task_type + '_solver' in self.__class__.__dict__:
                self.__class__.__dict__[task.task_type + '_solver'](self, task, response)
            else:
                self.logger_con.exception("Please define method '" + task.task_type + '_solver' + "'for tasks of type '" + task.task_type + "'")
                self.logger_file.exception("Please define method " + task.task_type + '_solver' + "for tasks of type '" + task.task_type + "'")


if __name__ == '__main__':
    spider = BaseNewsSpider(seed_urls={'http://www.google.com'})
    print BaseNewsSpider.__dict__
    spider.start()

