# -*- coding:utf-8 -*-
import calendar
from new_spider import *
from spiders import *

if __name__ == '__main__':

    NewSpider.PUT_IN_STORAGE = True
    '''
    s = requests.session()
    data = {'txtname': 'TP062016', 'txtpassword': 'tp201606'}
    r = s.post('http://stepaper.stheadline.com/login.asp', data=data)
    cookies = dict(r.cookies)
    '''
    cookies = {'ASPSESSIONIDSSTRSARS':'HACGAEDCPBOFAKCJNHHDNCBD',
               '__gads':'ID=352fabd817c03872:T=1467622623:S=ALNI_MYwrQJrdQaUkzeMBPe06fktAWW1vA',
               '_ga':'GA1.2.1204727515.1467634927',
               'login%5Fsession%5Fstr':'HA2QCAVGMmcnshJ'}

    cats = {'1':'要聞港聞', '2':'財經',
            '3':'地產', '4':'中國',
            '5':'國際', '6':'娛樂',
            '7':'副刊', '8':'家教',
            '9':'體育', '10':'馬經'}

    for cat_num in range(10, 10):

        cat_name = cats[str(cat_num+1)]

        # 2014
        from_mon = time.localtime().tm_mon
        from_day = time.localtime().tm_mday
        mon_day = calendar.monthrange(2014, from_mon)[1]
        while from_mon <= 12:
            search_url = ('http://stepaper.stheadline.com/search_result.asp?keyword=&op=0' +
                          '&category=' + str(cat_num + 1) +
                          '&SearchYear=2014' +
                          '&FromMonth=' + str(from_mon) +
                          '&FromDay=' + str(from_day) +
                          '&ToMonth=' + str(from_mon) +
                          '&ToDay=' + str(mon_day) +
                          '&headline_content=0')
            r_search = requests.get(search_url, cookies=cookies)
            r_search.encoding = 'big5hkscs'
            search_index = pq(r_search.text)
            total_page = search_index('form[name=search_page_form] input[name=total_page]').attr('value')
            if total_page is None:
                total_page = 1
            else:
                total_page = int(total_page)
            print 'Month: ' + str(from_mon)
            print 'Category: ' + cat_name
            print 'Total pages: ' + str(total_page)
            singtao_seed = set()
            for i in range(total_page):
                singtao_seed.add(search_url + '&page=' + str(i+1))
            spider_singtao = SpiderSingTao('SpiderSingTao', singtao_seed, 'http://stepaper\.stheadline\.com/news_content_related\.asp?.*',
                                            THREAD_NUM=30, max_depth=1, cookies=cookies, cat=cat_name)
            spider_singtao.start()

            from_mon += 1
            if from_mon <= 12:
                mon_day = calendar.monthrange(2014, from_mon)[1]
            from_day = 1

        # 2015
        from_mon = 1
        from_day = 1
        mon_day = 31
        while from_mon <= 12:
            search_url = ('http://stepaper.stheadline.com/search_result.asp?keyword=&op=0' +
                          '&category=' + str(cat_num + 1) +
                          '&SearchYear=2015' +
                          '&FromMonth=' + str(from_mon) +
                          '&FromDay=' + str(from_day) +
                          '&ToMonth=' + str(from_mon) +
                          '&ToDay=' + str(mon_day) +
                          '&headline_content=0')
            r_search = requests.get(search_url, cookies=cookies)
            r_search.encoding = 'big5hkscs'
            search_index = pq(r_search.text)
            total_page = search_index('form[name=search_page_form] input[name=total_page]').attr('value')
            if total_page is None:
                total_page = 1
            else:
                total_page = int(total_page)
            print 'Month: ' + str(from_mon)
            print 'Category: ' + cat_name
            print 'Total pages: ' + str(total_page)
            singtao_seed = set()
            for i in range(total_page):
                singtao_seed.add(search_url + '&page=' + str(i + 1))
            spider_singtao = SpiderSingTao('SpiderSingTao', singtao_seed,
                                            'http://stepaper\.stheadline\.com/news_content_related\.asp?.*',
                                            THREAD_NUM=30, max_depth=1, cookies=cookies, cat=cat_name)
            spider_singtao.start()

            from_mon += 1
            if from_mon <= 12:
                mon_day = calendar.monthrange(2015, from_mon)[1]
            from_day = 1

    for cat_num in range(9, 10):

        cat_name = cats[str(cat_num + 1)]

        # 2016
        from_mon = 1
        from_day = 1
        mon_day = 31
        while from_mon <= time.localtime().tm_mon:
            if from_mon == time.localtime().tm_mon:
                mon_day = time.localtime().tm_mday
            search_url = ('http://stepaper.stheadline.com/search_result.asp?keyword=&op=0' +
                          '&category=' + str(cat_num + 1) +
                          '&SearchYear=2016' +
                          '&FromMonth=' + str(from_mon) +
                          '&FromDay=' + str(from_day) +
                          '&ToMonth=' + str(from_mon) +
                          '&ToDay=' + str(mon_day) +
                          '&headline_content=0')
            r_search = requests.get(search_url, cookies=cookies)
            r_search.encoding = 'big5hkscs'
            search_index = pq(r_search.text)
            total_page = search_index('form[name=search_page_form] input[name=total_page]').attr('value')
            if total_page is None:
                total_page = 1
            else:
                total_page = int(total_page)
            print 'Month: ' + str(from_mon)
            print 'Category: ' + cat_name
            print 'Total pages: ' + str(total_page)
            singtao_seed = set()
            for i in range(total_page):
                singtao_seed.add(search_url + '&page=' + str(i + 1))
            spider_singtao = SpiderSingTao('SpiderSingTao', singtao_seed,
                                            'http://stepaper\.stheadline\.com/news_content_related\.asp?.*',
                                            THREAD_NUM=15, max_depth=1, cookies=cookies, cat=cat_name)
            spider_singtao.start()

            from_mon += 1
            if from_mon <= 12:
                mon_day = calendar.monthrange(2016, from_mon)[1]
            from_day = 1