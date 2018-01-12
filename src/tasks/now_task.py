# -*- coding:utf-8 -*-
import src.spiders.spider_now as now_news
import src.spiders.util as util


def main_task():
    now_news.SpiderNow.PUT_IN_STORAGE = True
    for i in range(util.get_offset_by_day_date('20151111'), util.get_offset_by_day_date('20110430')):
        day_str = util.get_day_string(interval_str='-', offset=i)
        now_seed = {'https://news.now.com/home/past?date=' + day_str}
        now_reg = {ur'https://news\.now\.com/.+newsId=\d+.+'}
        spider_now = now_news.SpiderNow('SpiderCableNews',
                                        now_seed,
                                        now_reg,
                                        THREAD_NUM=10)
        spider_now.BATCH_NUMBER = util.get_day_stamp(offset=i) + 10280
        spider_now.OFFSET = i
        spider_now.logger_file = spider_now.get_file_logger('nownews_task_log', 'logs/now_task.log')
        spider_now.start()


if __name__ == '__main__':
    main_task()
