# -*- coding:utf-8 -*-
import src.spiders.spider_govinfo as govinfo
import src.spiders.util as util


def main_task():
    govinfo.SpiderGovInfoNews.PUT_IN_STORAGE = True
    for i in range(util.get_offset_by_day_date('20160929'), util.get_offset_by_day_date('19980331')):
        day_str = util.get_day_string(offset=i)
        day_str = day_str[:-2] + '/' + day_str[-2:]
        govinfo_seed = {'http://www.info.gov.hk/gia/general/' + day_str + 'c.htm'}
        govinfo_reg = {ur'http://www\.info\.gov\.hk/gia/general/' + day_str + '.+'}
        spider_govinfo = govinfo.SpiderGovInfoNews('SpiderGovInfoNews', govinfo_seed, govinfo_reg, THREAD_NUM=10)
        spider_govinfo.OFFSET = i
        spider_govinfo.logger_file = spider_govinfo.get_file_logger('govinfo_task_log', 'logs/govinfo_task.log')
        spider_govinfo.BATCH_NUMBER = util.get_day_stamp(i) + 10600
        spider_govinfo.start()

if __name__ == '__main__':
    main_task()
