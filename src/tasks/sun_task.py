# -*- coding:utf-8 -*-
import src.spiders.spider_sun
import src.spiders.util


def main_task():
    src.spiders.spider_sun.SpiderSun.PUT_IN_STORAGE = True
    for i in range(src.spiders.util.get_offset_by_day_date('20160331'), src.spiders.util.get_offset_by_day_date('20020601')):
        src.spiders.spider_sun.start_crawling(i)

if __name__ == '__main__':
    main_task()
