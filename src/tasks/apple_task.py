# -*- coding:utf-8 -*-
import src.spiders.spider_apple
import src.spiders.util as util


def main_task():
    src.spiders.spider_apple.SpiderApple.PUT_IN_STORAGE = True
    for i in range(util.get_offset_by_day_date('20070227'), util.get_offset_by_day_date('20020101')):
        day_str = util.get_day_string(offset=i)
        apple_seed = {'http://hk.apple.nextmedia.com/archive/index/' + day_str + '/index/'}
        spider_apple = src.spiders.spider_apple.SpiderApple('SpiderApple',
                                                            apple_seed,
                                                            {ur'http://hk\.apple\.nextmedia\.com/.*' + day_str + '/.*'},
                                                            THREAD_NUM=5)
        spider_apple.BATCH_NUMBER = util.get_day_stamp(offset=i) + 10590
        spider_apple.OFFSET = i
        spider_apple.logger_file = spider_apple.get_file_logger('apple_task_log', 'logs/apple_task.log')
        spider_apple.start()

if __name__ == '__main__':
    main_task()
