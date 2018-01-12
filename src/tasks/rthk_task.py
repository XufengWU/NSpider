# -*- coding:utf-8 -*-
import src.spiders.spider_rthk as rthk
import src.spiders.util as util


def main_task():
    rthk.SpiderRTHK.PUT_IN_STORAGE = True
    for i in range(util.get_offset_by_day_date('20160717'), util.get_offset_by_day_date('20150927')):
        current_day_string = util.get_day_string(offset=i)
        day_string = 'archive_year=' + current_day_string[0:4] + '&archive_month=' + current_day_string[
                                                                                     4:6] + '&archive_day=' + current_day_string[
                                                                                                              6:8]
        instant_news_page_url = 'http://news.rthk.hk/rthk/ch/news-archive.htm?' + day_string + '&archive_cat=all'
        rthk_seed = {instant_news_page_url}
        rthk_reg = {ur'http://news\.rthk\.hk/rthk/ch/component/.*' +
                    util.get_day_string(offset=i) +
                    '.*'}
        spider_rthk = rthk.SpiderRTHK('SpiderRTHK', rthk_seed, rthk_reg, THREAD_NUM=5)
        spider_rthk.BATCH_NUMBER = util.get_day_stamp() + 10130
        spider_rthk.OFFSET = i
        spider_rthk.logger_file = spider_rthk.get_file_logger('rthk_task_log', 'logs/rthk_task.log')
        spider_rthk.start()


if __name__ == '__main__':
    main_task()
