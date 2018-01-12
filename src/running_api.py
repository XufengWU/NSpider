# -*- coding:utf-8 -*-
import spiders.config
from spiders import *
import logging
import time

logger_con = logging.getLogger(spiders.config.COMMON_NEWS_SPIDER_CONSOLE_LOG_NAME)
logger_file = logging.getLogger(spiders.config.COMMON_NEWS_SPIDER_FILE_LOG_NAME)


def run_spider_module(crawling_function=None, offset=0, **kwargs):
    try:
        # run spider
        crawling_function(offset=offset, **kwargs)
        return True
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, e:
        logger_con.error(str(e))
        logger_file.error(str(e))
        logger_con.info('Task failure. Wait 5 seconds and continue.')
        logger_file.info('Task failure. Wait 5 seconds and continue.')
        time.sleep(5)
        return False
