# -*- coding:utf-8 -*-
from spiders import *
import spiders.source as source
import sys
import time
import threading
import config
import spiders.util as util
import spiders.storage as storage
import json

logger_con = config.LOGGER_CON
logger_file = config.LOGGER_FILE

RSS_MODULE = config.RSS_MODULE
RSS_SPIDER_CLASS = config.RSS_SPIDER_CLASS
MAX_TASK_QUEUE_SIZE = config.MAX_TASK_QUEUE_SIZE

SOURCE_EXTRA_CONFIG = config.SOURCE_EXTRA_CONFIG
THREAD_NUM_OF_TYPE = config.THREAD_NUM_OF_TYPE

'''
** raw info format on server **
{
    u'next_at': 1477479953,
    u'description': u'Initium media article news feed.',
    u'title': u'\u7aef\u50b3\u5a92 | Initium Media',
    u'url': u'http://feeds.initium.news/theinitium',
    u'created_at': 1477288832,
    u'map_to': u'Initium',
    u'type': 1,
    u'id': 1
}

** source_info format **
_source_info = {
    'rss': {
        1: {'source': 'Initium', 'delayed_sec': 10,
                'spider_kwargs': {'seed_urls': ['http://feeds.initium.news/theinitium']}},
        2: {'source': 'RTHK',
                'spider_kwargs': {'seed_urls': ['http://rthk.hk/rthk/news/rss/c_expressnews_clocal.xml']}}
    }
}

** task_structure format **
{'id': 1, 'type': 'rss', 'source': 'Initium', (other parameters: ...}
'''


def get_source_info():
    login_res = source.login('wuxufeng', 'diao')
    _data = source.source_home(login_res['session'])['data']
    _source_info = {}
    for _entry in _data:
        _type = ''
        if _entry['type'] == 1:
            _type = 'rss'
        if _type not in _source_info:
            _source_info[_type] = {}
        _id = _entry['id']
        _source_info[_type][_id] = _entry
        if 'map_to' in _entry:
            _source_info[_type][_id]['source'] = _entry['map_to']
        if _id in SOURCE_EXTRA_CONFIG:
            for _attr in SOURCE_EXTRA_CONFIG[_id]:
                _source_info[_type][_id][_attr] = SOURCE_EXTRA_CONFIG[_id][_attr]
        if _type == 'rss':
            if 'spider_kwargs' not in _source_info[_type][_id]:
                _source_info[_type][_id]['spider_kwargs'] = {}
            _source_info[_type][_id]['spider_kwargs']['seed_urls'] = {_entry['url']}
    return _source_info

# load source information
source_info = get_source_info()

scheduler_queues_and_locks = {}
for _type in source_info:
    scheduler_queues_and_locks[_type] = {}
    scheduler_queues_and_locks[_type]['lock'] = threading.RLock()
    scheduler_queues_and_locks[_type]['queue'] = []
active_source_lock = threading.Lock()
active_source = []


class RunnerThread(threading.Thread):

    def __init__(self, thread_id, source_type):
        threading.Thread.__init__(self)
        self.id = thread_id
        self.source_type = source_type

    def run(self):
        logger_con.info('start running: ' + self.name)
        logger_file.info('start running: ' + self.name)
        while True:
            _new_running_task = None
            _spider_class = None
            with scheduler_queues_and_locks[self.source_type]['lock']:
                _queue = scheduler_queues_and_locks[self.source_type]['queue']
                if len(_queue) > 0:
                    _new_running_task = _queue[0]
                    if self.source_type == 'rss':
                        _module = sys.modules['spiders.'+RSS_MODULE]
                        _spider_class = _module.__dict__[RSS_SPIDER_CLASS]
                    else:
                        _module = sys.modules['spiders.'+_new_running_task['module']]
                        _spider_class = _module.__dict__[_new_running_task['spider_class']]
                    _queue.pop(0)
            if _new_running_task:
                _source_id = _new_running_task['id']
                source.source_start(_source_id)
                try:
                    logger_con.info('running source ' + str(_source_id) + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                    logger_file.info('running source ' + str(_source_id) + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                    if 'spider_kwargs' in _new_running_task:
                        _spider = _spider_class.start_crawling(**_new_running_task['spider_kwargs'])
                    else:
                        _spider = _spider_class.start_crawling()
                    _count = _spider.item_count
                    if str(_spider.__class__) == 'spiders.spider_rss.SpiderRSS':
                        if _count-len(_spider.seeds) > 0:
                            _count -= len(_spider.seeds)
                        else:
                            _count = 0
                    source.source_success(_source_id, _count)
                    logger_con.info('source success: ' + str(_source_id) + ', source: ' + _new_running_task['source'] + ', fetched_count: ' + str(_count) + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                    logger_file.info('source success: ' + str(_source_id) + ', source: ' + _new_running_task['source'] + ', fetched_count: ' + str(_count) + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                except (KeyboardInterrupt, SystemExit):
                    source.source_fail(_source_id)
                    logger_con.error('source fail:' + str(_source_id) + ', source: ' + _new_running_task['source'] + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                    logger_file.error('source fail:' + str(_source_id) + ', source: ' + _new_running_task['source'] + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                    raise
                except Exception, e:
                    source.source_fail(_source_id)
                    logger_con.error('source fail:' + str(_source_id) + ', source: ' + _new_running_task['source'] + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                    logger_file.error('source fail:' + str(_source_id) + ', source: ' + _new_running_task['source'] + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                    logger_con.error(str(e))
                    logger_file.error(str(e))
                    logger_con.info('Task failure. Wait 5 seconds and continue.')
                    logger_file.info('Task failure. Wait 5 seconds and continue.')
                    time.sleep(5)
                finally:
                    with active_source_lock:
                        if _source_id in active_source:
                            logger_con.info('done source: ' + str(_source_id) + ', source: ' + _new_running_task['source'] + ', task_stamp: ' + str(_new_running_task['task_stamp']))
                            active_source.remove(_source_id)


def main(source_info):

    spider_rss.SpiderRSS.PUT_IN_STORAGE = True

    for _t in source_info:
        for i in range(THREAD_NUM_OF_TYPE[_t]):
            _thread = RunnerThread(i, _t)
            _thread.name = 'Thread-' + _t + '-' + str(i)
            _thread.start()
    while True:
        _round_done = False
        while True:
            source_info = get_source_info()
            if util.within_active_interval(48, 15 * 60):
                if not _round_done:
                    print 'start round ' + str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)

                    # collecting round
                    for _t in source_info:
                        _round_count = 0
                        print len(source_info[_t])
                        while _round_count < len(source_info[_t]):
                            with active_source_lock:
                                _next_task = source.source_next(_t)['data']
                                _id = _next_task['id']
                                if _id not in active_source:
                                    with scheduler_queues_and_locks[_t]['lock']:
                                        if len(scheduler_queues_and_locks[_t]['queue']) < MAX_TASK_QUEUE_SIZE:
                                            _round_count += 1
                                            # construct a new task
                                            for attr in source_info[_t][_id]:
                                                if attr not in _next_task:
                                                    _next_task[attr] = source_info[_t][_id][attr]
                                            _next_task['task_stamp'] = int(time.time())
                                            active_source.append(_id)
                                            logger_con.info(
                                                'schedule source: ' + str(_id) + ', source: ' + _next_task['source'])
                                            _queue = scheduler_queues_and_locks[_t]['queue']
                                            _queue.append(_next_task)

                    print 'round done ' + str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
                    _round_done = True
            else:
                _round_done = False
            print 'waiting ' + str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
            time.sleep(600)


if __name__ == '__main__':
    main(source_info)
