# -*- coding:utf-8 -*-
import src.spiders.spider_hkej
import src.spiders.util as util


def main_task():
    src.spiders.spider_hkej.SpiderHKEJ.PUT_IN_STORAGE = True
    src.spiders.spider_hkej.SpiderHKEJ.ADD_MEDIA = True
    for i in range(util.get_offset_by_day_date('20161025'), util.get_offset_by_day_date('20160901')):
        src.spiders.spider_hkej.SpiderHKEJ.start_crawling(offset=i, THREAD_NUM=20)

if __name__ == '__main__':
    main_task()
