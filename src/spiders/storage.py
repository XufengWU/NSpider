# -*- coding: utf-8 -*-
import requests
import config
from threading import BoundedSemaphore


db_sem = BoundedSemaphore()

server_url = config.SERVERS_DICT[config.CHOSEN_SERVER]
print 'CHOSEN SERVER: ' + server_url


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
                if r.status_code:
                    print 'http error: ' + str(r.status_code)
                raise

    def set(self, func_name, params):
        try:
            r = requests.post(self.prefix + func_name, params)
        except Exception, a:
            raise a
        else:
            if r.status_code == 200:
                return r.json()
            else:
                if r.status_code:
                    print 'http error: ' + str(r.status_code)
                raise

# conn = RestClient('http://192.168.66.168/storage-api/')
# conn = RestClient('http://192.168.66.168/egarots-wen-tset/')
conn = RestClient(server_url)


def url_exists(url):
    try:
        db_sem.acquire()
        res = conn.get('storage/url-exists', {'url': url})
    except Exception, e:
        raise e
    else:
        return res and (res['code'] == True or str(res['code']) == '1')
    finally:
        db_sem.release()


def add_page(**kwargs):
    try:
        db_sem.acquire()
        res = conn.set('storage/add-page', kwargs)
    except Exception, e:
        raise e
    else:
        if res and str(res['code']) == '0':
            raise Exception(res['msg'])
        return res and res['code'] == True
    finally:
        db_sem.release()


def media_exists(page_url, media_url):
    try:
        db_sem.acquire()
        res = conn.get('storage/media-exists', {'page_url': page_url, 'media_url': media_url})
    except Exception, e:
        raise e
    else:
        return res and (res['code'] == True or str(res['code']) == '1')
    finally:
        db_sem.release()


def add_media(**kwargs):
    try:
        db_sem.acquire()
        res = conn.set('storage/add-media', kwargs)
    except Exception, e:
        raise e
    else:
        if res and str(res['code']) == '0':
            raise Exception(res['msg'])
        return res and res['code'] == True
    finally:
        db_sem.release()


def xy_exists(source, text, x):
    try:
        db_sem.acquire()
        res = conn.get('xy/point-exists', {'source': source, 'text': text, 'x': x})
    except Exception, e:
        raise e
    else:
        return res and (res['code'] == True or str(res['code']) == '1')
    finally:
        db_sem.release()


def add_xy(**kwargs):
    try:
        db_sem.acquire()
        res = conn.set('xy/add', kwargs)
    except Exception, e:
        raise e
    else:
        if res and str(res['code']) == '0':
            raise Exception(res['msg'])
        return res and res['code'] == True
    finally:
        db_sem.release()


def set_value(key, value):
    try:
        db_sem.acquire()
        res = conn.set('storage/set-value', {'key': key, 'value': value})
    except Exception, e:
        raise e
    else:
        return res and (res['code'] == True or str(res['code']) == '1')
    finally:
        db_sem.release()


def get_value(key):
    try:
        db_sem.acquire()
        res = conn.get('storage/get-value', {'key': key})
    except Exception, e:
        raise e
    else:
        return res
    finally:
        db_sem.release()


def test():
    print media_exists("http://finance.takungpao.com/dujia/2016-09/3374744.html", 'h1')
    try:
        print add_media(page_url='http://finance.takungpao.com/dujia/2016-09/3374744', media_url='h1', description='none', media_type='image', created_at=001, source='none')
    except Exception, e:
        print e.message

if __name__ == '__main__':
    print url_exists(u'https://www.hk01.com/01博評-生活/83465/-%E5%A5%B3%E4%BA%BA%E5%9B%9B%E5%8D%81-%E7%94%9F%E5%91%BD%E4%B8%AD%E4%B8%8D%E8%83%BD%E6%89%BF%E5%8F%97%E7%9A%84%E5%A5%B3%E6%B3%A2%E5%A3%AB')

