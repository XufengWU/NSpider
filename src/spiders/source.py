# -*- coding:utf-8 -*-
import requests
from threading import BoundedSemaphore
import storage

db_sem = BoundedSemaphore()


class RestClient:

    def __init__(self, prefix):
        self.prefix = prefix

    def get(self, func_name, params):
        try:
            r = requests.get(self.prefix + func_name, params)
        except Exception, a:
            raise a
        else:
            if r.status_code == 200:
                return r.json()
            else:
                return False

    def set(self, func_name, params):
        try:
            r = requests.post(self.prefix + func_name, params)
        except Exception, a:
            raise a
        else:
            if r.status_code == 200:
                return r.json()
            else:
                return False

conn = RestClient('http://192.168.66.168/news-api/1/')


def source_url_exists(url):
    try:
        db_sem.acquire()
        res = conn.get('source/url-exists', {'url': url})
    except Exception, e:
        raise e
    else:
        return res and (res['code'] == True or str(res['code']) == '1')
    finally:
        db_sem.release()


def url_to_id(url):
    try:
        db_sem.acquire()
        res = conn.get('source/url-to-id', {'url': url})
    except Exception, e:
        raise e
    else:
        if res['code'] == True or str(res['code']) == '1':
            return res['data']
        else:
            return False
    finally:
        db_sem.release()


def source_start(source_id):
    try:
        db_sem.acquire()
        res = conn.set('source/start', {'id': source_id})
    except Exception, e:
        raise e
    else:
        if res['code'] == True or str(res['code']) == '1':
            return True
        else:
            return False
    finally:
        db_sem.release()


def source_success(source_id, fetched_count):
    try:
        db_sem.acquire()
        res = conn.set('source/success', {'id': source_id, 'fetched_count': fetched_count})
    except Exception, e:
        raise e
    else:
        if res['code'] == True or str(res['code']) == '1':
            return True
        else:
            return False
    finally:
        db_sem.release()


def source_fail(source_id):
    try:
        db_sem.acquire()
        res = conn.set('source/fail', {'id': source_id})
    except Exception, e:
        raise e
    else:
        if res['code'] == True or str(res['code']) == '1':
            return True
        else:
            return False
    finally:
        db_sem.release()


def source_next(source_type):
    try:
        db_sem.acquire()
        res = conn.get('source/next', {'type': source_type})
    except Exception, e:
        raise e
    else:
        if res['code'] == True or str(res['code']) == '1':
            return res
        else:
            return False
    finally:
        db_sem.release()


def change_schedule(source_id, at):
    try:
        db_sem.acquire()
        res = conn.set('source/change-schedule', {'id': source_id, 'at': at})
    except Exception, e:
        raise e
    else:
        if res['code'] == True or str(res['code']) == '1':
            return True
        else:
            return False
    finally:
        db_sem.release()


def add_source(type, map_to, url='', title='', description=''):
    try:
        db_sem.acquire()
        res = conn.set('source/add', {'type': type, 'url': url, 'title': title, 'description': description, 'map_to': map_to})
    except Exception, e:
        raise e
    else:
        if res['code'] == True or str(res['code']) == '1':
            return res
        else:
            print res['msg']
            return res
    finally:
        db_sem.release()


def history(source_id):
    try:
        db_sem.acquire()
        res = conn.get('source/history', {'id': source_id})
    except Exception, e:
        raise e
    else:
        if res['code'] == True or str(res['code']) == '1':
            return res
        else:
            return False
    finally:
        db_sem.release()


def source_home(session):
    try:
        db_sem.acquire()
        res = conn.get('source/home', {'session': session})
    except Exception, e:
        raise e
    else:
        if res["code"] == True or str(res["code"]) == '1':
            return res
        else:
            return False
    finally:
        db_sem.release()


def login(username, psw):
    try:
        db_sem.acquire()
        res = conn.set('login', {'username': username, 'password': psw})
    except Exception, e:
        raise e
    else:
        if res["code"] == True or str(res["code"]) == '1':
            return res
        else:
            return False
    finally:
        db_sem.release()

if __name__ == '__main__':
    res = login('wuxufeng', 'diao')
    print res
    _data = source_home(res['session'])['data']
    print _data
