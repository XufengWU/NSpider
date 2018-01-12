# -*- coding:utf-8 -*-
import src.spiders.spider_oriental
import src.spiders.util as util


def main_task():
    src.spiders.spider_oriental.SpiderOriental.PUT_IN_STORAGE = True
    for i in range(src.spiders.util.get_offset_by_day_date('20020602'), src.spiders.util.get_offset_by_day_date('20020531')):
        oriental_seed = {'http://orientaldaily.on.cc/cnt/sitemap/' +
                         util.get_day_string(offset=i) +
                         '/index.html'}
        oriental_reg = {ur'http://orientaldaily\.on\.cc/cnt/.+' +
                        util.get_day_string(offset=i) +
                        r'/[\d_]+.html',
                        ur'http://orientaldaily\.on\.cc/archive/' +
                        util.get_day_string(offset=i) +
                        '.+\.html'}
        spider_o = src.spiders.spider_oriental.SpiderOriental('SpiderOriental', oriental_seed, oriental_reg, THREAD_NUM=5)
        spider_o.OFFSET = i
        # spider_o.FETCH_DELAY = 10
        spider_o.BATCH_NUMBER = util.get_day_stamp(i) + 10310
        spider_o.start()

if __name__ == '__main__':
    main_task()
