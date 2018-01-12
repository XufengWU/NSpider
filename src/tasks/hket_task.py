# -*- coding:utf-8 -*-
import src.spiders.spider_hket as hket
import src.spiders.util as util


def main_task():
    hket.SpiderHKET.PUT_IN_STORAGE = True
    hket_reg = {ur'http://.+\.hket\.com/article/\d+/.*'}
    for i in range(util.get_offset_by_day_date('20161010'), util.get_offset_by_day_date('20161006')):
        day_str = util.get_day_string(offset=i)
        portal_url = 'http://paper.hket.com/srap017/%E6%98%94%E6%97%A5%E6%96%B0%E8%81%9E?dis=' + day_str
        hket_seed = {portal_url}
        spider_hket = hket.SpiderHKET('SpiderHKET',
                                      hket_seed,
                                      hket_reg,
                                      THREAD_NUM=5,
                                      MAX_DEPTH=1)
        spider_hket.BATCH_NUMBER = util.get_day_stamp() + 10110
        spider_hket.OFFSET = i
        spider_hket.logger_file = spider_hket.get_file_logger('hket_task_log',
                                                              'logs/hket_task.log')
        spider_hket.start()


if __name__ == '__main__':
    main_task()
