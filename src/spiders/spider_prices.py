# -*- coding: utf-8 -*-
import common_news_spider
import util
import requests
import re
import json
import threading
import time
import storage
from pyquery import PyQuery as pq

products = {
    1: {'name': u'木棉', 'cat': 1},
    2: {'name': u'黑鯧', 'cat': 1},
    3: {'name': u'狗肚', 'cat': 1},
    5: {'name': u'鷹鯧', 'cat': 1},
    7: {'name': u'沙鯭', 'cat': 1},
    8: {'name': u'牛鰍', 'cat': 1},
    9: {'name': u'紅衫', 'cat': 1},
    10: {'name': u'青門鱔', 'cat': 1},
    11: {'name': u'烏頭', 'cat': 1},
    12: {'name': u'牙帶', 'cat': 1},
    13: {'name': u'青根', 'cat': 1},
    14: {'name': u'白飯魚', 'cat': 1},
    15: {'name': u'鮫魚', 'cat': 1},
    16: {'name': u'鰦魚', 'cat': 1},
    17: {'name': u'瓜衫', 'cat': 1},
    18: {'name': u'瓜核', 'cat': 1},
    19: {'name': u'泥斑', 'cat': 1},
    20: {'name': u'泥鯭', 'cat': 1},
    21: {'name': u'沙鑽', 'cat': 1},
    22: {'name': u'鱸魚', 'cat': 1},
    23: {'name': u'龍脷', 'cat': 1},
    24: {'name': u'馬友', 'cat': 1},
    25: {'name': u'丁公', 'cat': 1},
    26: {'name': u'白鯧', 'cat': 1},
    27: {'name': u'白立', 'cat': 1},
    28: {'name': u'黃花', 'cat': 1},
    29: {'name': u'黃腳立', 'cat': 1},
    61: {'name': u'老虎斑', 'cat': 1},
    62: {'name': u'芝麻斑', 'cat': 1},
    63: {'name': u'杉斑', 'cat': 1},
    64: {'name': u'金絲立', 'cat': 1},
    65: {'name': u'青斑', 'cat': 1},
    66: {'name': u'頭鱸', 'cat': 1},
    67: {'name': u'東星斑', 'cat': 1},
    68: {'name': u'紅魚', 'cat': 1},
    69: {'name': u'紅鮪', 'cat': 1},
    70: {'name': u'細鱗', 'cat': 1},
    71: {'name': u'黃立鯧', 'cat': 1},
    72: {'name': u'泥鯭', 'cat': 1},
    73: {'name': u'紅斑', 'cat': 1},
    74: {'name': u'火點', 'cat': 1},
    75: {'name': u'黃腳立', 'cat': 1},
    76: {'name': u'沙巴躉', 'cat': 1},
    77: {'name': u'鯇魚', 'cat': 2},
    78: {'name': u'大魚', 'cat': 2},
    79: {'name': u'鯪魚', 'cat': 2},
    100: {'name': u'王菜', 'cat': 3},
    101: {'name': u'生菜', 'cat': 3},
    102: {'name': u'西洋菜', 'cat': 3},
    103: {'name': u'芥蘭', 'cat': 3},
    104: {'name': u'油麥菜', 'cat': 3},
    105: {'name': u'青白菜', 'cat': 3},
    106: {'name': u'菠菜', 'cat': 3},
    107: {'name': u'菜芯', 'cat': 3},
    108: {'name': u'青椰菜', 'cat': 3},
    109: {'name': u'豆苗', 'cat': 3},
    110: {'name': u'節瓜', 'cat': 3},
    111: {'name': u'青瓜', 'cat': 3},
    112: {'name': u'番茄', 'cat': 3},
    113: {'name': u'薯仔', 'cat': 3},
    114: {'name': u'白蘿蔔', 'cat': 3},
    115: {'name': u'紅蘿蔔', 'cat': 3},
    116: {'name': u'芋頭', 'cat': 3},
    117: {'name': u'西生菜', 'cat': 3},
    118: {'name': u'西蘭花', 'cat': 3},
    200: {'name': u'活豬', 'cat': 4},
    201: {'name': u'活牛', 'cat': 4},
    202: {'name': u'活雞', 'cat': 5},
    300: {'name': u'內地啡蛋', 'cat': 6}
}
cats = {
    1: {'unit': u'公斤', 'info': u'鹹水魚'},
    2: {'unit': u'斤', 'info': u'淡水魚'},
    3: {'unit': u'斤', 'info': u'蔬菜'},
    4: {'unit': u'擔', 'info': u'牲畜'},
    5: {'unit': u'斤', 'info': u'家禽'},
    6: {'unit': u'隻', 'info': u'蛋'},
}
mtr_line_names = {
    'isline': u'港島綫',
    'siline': u'南港島綫',
    'ktline': u'觀塘綫',
    'twline': u'荃灣綫',
    'tkline': u'將軍澳綫',
    'tcline': u'東涌綫',
    'drline': u'迪士尼綫',
    'erline': u'東鐵綫',
    'wrline': u'西鐵綫',
    'moline': u'馬鞍山綫',
    'aeline': u'機場快綫'
}
fmo_pattern = re.compile(r'http://www\.fmo\.org\.hk/fish-price.+')
vmo_pattern = re.compile(r'http://www\.vmo\.org/tc/index/page_winterprice/')
afcd_pattern = re.compile(r'http://www\.afcd\.gov\.hk/tc_chi/agriculture/agr_fresh/agr_fresh\.html')
supermarket_pattern = re.compile(r'http://www3\.consumer\.org\.hk/pricewatch/supermarket/')
towngas_pattern = re.compile(r'https://www\.towngas\.com/tc/Household/Customer-Services/Tariff')
clp_pattern = re.compile(r'https://www\.clp\.com\.hk/zh/customer-service/tariff/residential-customers')
taxi_pattern = re.compile(
    r'http://www\.td\.gov\.hk/en/transport_in_hong_kong/public_transport/taxi/taxi_fare_of_hong_kong/')
mtr_data_pattern = re.compile(
    r'http://www\.mtr\.com\.hk/share/customer/include/getdata\.php\?&type=data&sid=\d+&eid=\d+')
date_pattern = re.compile(r'\d{4}\-\d\d-\d\d')
date_pattern_2 = re.compile(r'\d+/\d+/\d{4}')


class SpiderPrices(common_news_spider.CommonNewsSpider):
    prices = {}
    stored_prices = {}
    cur_date_stamp = util.get_day_stamp(0)
    prices_lock = threading.Lock()

    class PriceItem:
        def __init__(self, source, text, x, y, created_at):
            self.source = source
            self.text = text
            self.x = x
            self.y = y
            self.created_at = created_at

    def send_request(self, task):
        r = requests.get(task.url, timeout=self.RESPONSE_TIMEOUT_VALUE)
        r.encoding = 'utf8'
        return r

    def solve_price_item(self, price_item):
        with self.prices_lock:
            if price_item.x not in self.prices:
                self.prices[price_item.x] = {}
            self.prices[price_item.x][price_item.text] = [price_item.y, price_item.source]
            if not (price_item.source == 'ConsumerCouncil' and (
                            price_item.x in self.stored_prices and price_item.source in self.stored_prices[
                        price_item.x])):
                if storage.xy_exists(price_item.source, price_item.text, price_item.x):
                    self.logger_con.info('exists data of ' + price_item.source + ': ' + str(price_item.x))
                    if price_item.x not in self.stored_prices:
                        self.stored_prices[price_item.x] = {}
                    self.stored_prices[price_item.x][price_item.source] = 1
                else:
                    storage.add_xy(source=price_item.source, text=price_item.text, x=price_item.x, y=price_item.y,
                                   created_at=price_item.created_at)
                    self.logger_con.info(
                        'put in server: ' + price_item.source + ', ' + price_item.text + ', ' + str(price_item.y))

    def normal_solver(self, task, response):
        doc = self.get_doc(response)
        if fmo_pattern.match(task.url):
            pid = int(task.url.split('=')[-1])
            t = doc('div.trend-discount-date').text()
            t_search = date_pattern.findall(t)
            if t_search:
                t_str = t_search[-1]
                t_stamp = util.get_timestamp_from_string(t_str)
                script = doc('script:nth-last-child(2)').text()
                dtxt = re.findall(r'(?<="data":)\[.+?\]', script)[0]
                j = json.loads(dtxt)
                if float(j[-1]) != 0:
                    self.solve_price_item(
                        self.PriceItem('FMO', products[pid]['name'] + u' 1公斤', t_stamp, float(j[-1]), int(time.time())))
        elif vmo_pattern.match(task.url):
            t = doc('table.winterprice-left-formholder span.menu').text().split(' ')[0]
            t_stamp = util.get_timestamp_from_string(t)
            for tr in doc('table.newsbanner tr').items():
                if tr('td.winterprice-td-col1'):
                    p_name = tr('td.winterprice-td-col2').text()
                    p = float(tr('td.winterprice-td-col4').text().split('$')[-1])
                    for pid in products:
                        if products[pid]['name'] == p_name:
                            self.solve_price_item(self.PriceItem('VMO', p_name + u' 1斤', t_stamp, p, int(time.time())))
                            break
        elif afcd_pattern.match(task.url):
            t_search = date_pattern_2.findall(doc('h1').text())
            if t_search:
                t = t_search[0]
                t_stamp = util.get_timestamp_from_string(t, '%d/%m/%Y')
                for table in doc('table').items():
                    if table('caption'):
                        cap = table('caption').text()
                        pids = {}
                        if cap == u'牲畜':
                            for tr in table('tr').items():
                                trtxt = tr('td').text()
                                ptxt = tr('td:nth-last-child(1)').text()
                                if re.findall(u'活豬', trtxt):
                                    if re.match(r'\d+[,\d]+\d+', ptxt):
                                        pids[200] = float(re.sub(',', '', ptxt))
                                elif re.findall(u'活牛', trtxt):
                                    if re.match(r'\d+[,\d]+\d+', ptxt):
                                        pids[201] = float(re.sub(',', '', ptxt))
                        elif cap == u'家禽':
                            for tr in table('tr').items():
                                trtxt = tr('td').text()
                                if re.findall(u'本地', trtxt):
                                    pids[202] = float(tr('td:nth-last-child(1)').text())
                        elif cap == u'淡水魚':
                            for tr in table('tr').items():
                                trtxt = tr('td').text()
                                if re.findall(u'鯇魚', trtxt):
                                    pids[77] = float(tr('td:nth-last-child(1)').text())
                                if re.findall(u'大魚', trtxt):
                                    pids[78] = float(tr('td:nth-last-child(1)').text())
                                if re.findall(u'鯪魚', trtxt):
                                    pids[79] = float(tr('td:nth-last-child(1)').text())
                        elif cap == u'雞蛋':
                            for tr in table('tr').items():
                                trtxt = tr('td').text()
                                if re.findall(u'內地啡蛋', trtxt):
                                    pids[300] = float(tr('td:nth-last-child(1)').text())
                        if len(pids) > 0:
                            for pid in pids:
                                self.solve_price_item(
                                    self.PriceItem('AFCD',
                                                   products[pid]['name'] + u' 1' + cats[products[pid]['cat']]['unit'],
                                                   t_stamp, pids[pid],
                                                   int(time.time()))
                                )
        elif supermarket_pattern.match(task.url):
            t = doc('#theMainContent span.comment').text()
            t_search = date_pattern.findall(t)
            if t_search:
                t_stamp = util.get_timestamp_from_string(t_search[0])
                for tr in doc('form[name="itemlist"] tr').items():
                    if tr('td.pr1') or tr('td.pr2'):
                        brand = tr('td:nth-child(3)')
                        p_name = tr('td:nth-child(4)')
                        wk_price = tr('td:nth-child(5)').text()
                        ps_price = tr('td:nth-child(6)').text()
                        p = -1
                        if wk_price != '--':
                            p = float(wk_price.encode('utf-8').split(' ')[-1])
                        elif ps_price != '--':
                            p = float(ps_price.split(' ')[-1])
                        if p > 0:
                            self.solve_price_item(
                                self.PriceItem('ConsumerCouncil', brand.text() + u' ' + p_name.text(), t_stamp, p,
                                               int(time.time()))
                            )
        elif towngas_pattern.match(task.url):
            ps = []
            levs_add = []
            lev_0 = 0
            unit_s = re.findall(ur'(?<=\().+(?=\))',
                                doc('div.gasTableContainer table tr:nth-child(1) th:nth-child(1)').text())
            if unit_s:
                unit = unit_s[0]
                for tr in doc('div.gasTableContainer table tr').items():
                    if tr('td:nth-last-child(1)').text().find(u'仙') >= 0:
                        lev = float((tr('td:nth-last-child(2)').text().split(' ')[0]).replace(',', ''))
                        lev_c = lev
                        p = float(tr('td:nth-last-child(1)').text().split(' ')[0]) / 100
                        if tr('td:nth-child(1)').text() == u'首':
                            lev_0 = lev
                        if tr('td:nth-child(1)').text() == u'次':
                            levs_add.append(lev)
                            lev_c = sum(levs_add) + lev_0
                        pn = str(lev_c)
                        if tr('td:nth-child(1)').text() == u'逾':
                            pn = str(lev_c) + '+'
                        ps.append(self.PriceItem('TownGas', pn + ' 1' + unit, self.cur_date_stamp, p, int(time.time())))
                adj_fee = doc('h3.pageSubTitleBlack').text()
                if re.match(ur'燃料調整費(.+)', adj_fee):
                    fee_s = re.findall(ur'\d+\.\d+', adj_fee)
                    if fee_s:
                        fee = float(fee_s[0]) / 100
                        ps.append(
                            self.PriceItem('TownGas', u'燃料調整費 1' + unit, self.cur_date_stamp, fee, int(time.time())))
            for pi in ps:
                self.solve_price_item(pi)
        elif clp_pattern.match(task.url):
            ps = []
            levs_add = []
            lev_0 = 0
            unit = u'度'
            for table in doc('table').items():
                if re.findall(u'收費率', table('tbody tr').text()):
                    for tr in table('tr').items():
                        levtxt = tr('td:nth-child(1)').text()
                        lev = -1
                        pn = ''
                        if re.findall(u'首', levtxt):
                            lev = float(re.findall(r'\d+', levtxt)[0])
                            lev_0 = lev
                            pn = str(lev)
                        elif re.findall(u'次', levtxt):
                            lev = float(re.findall(r'\d+', levtxt)[0])
                            levs_add.append(lev)
                            pn = str(sum(levs_add) + lev_0)
                        elif re.findall(u'逾', levtxt):
                            lev = float(re.findall(r'\d+', levtxt)[0])
                            pn = str(lev) + '+'
                        if lev > 0 and pn != '':
                            p = float(tr('td:nth-last-child(1)').text()) / 100
                            ps.append(self.PriceItem('CLP', pn + ' 1' + unit, self.cur_date_stamp, p, int(time.time())))
                    for strong in doc('p strong').items():
                        if re.findall(u'燃料調整費', strong.text()):
                            fee_p = strong.parent('p').next('p')
                            fee_s = re.findall(ur'\d+\.\d+', fee_p.text())
                            if fee_s:
                                fee = float(fee_s[0]) / 100
                                ps.append(
                                    self.PriceItem('CLP', u'燃料調整費 1' + unit, self.cur_date_stamp, fee,
                                                   int(time.time())))
                            break
            for pi in ps:
                self.solve_price_item(pi)
        elif taxi_pattern.match(task.url):
            src = 'TransportDepartment'
            ps = []
            for tb in doc('table.content_table1').items():
                if tb('tr:nth-child(1)').text() == 'Fare Table - Urban Taxi':
                    pn = 'Urban Taxi'
                    for tr in tb('tr.TLevel4').items():
                        if tr('td:nth-child(2)'):
                            if re.match(r'\$ [\d\.]+$', tr('td:nth-child(2)').text()):
                                p = float(tr('td:nth-child(2)').text().split(' ')[-1])
                                dt = tr('td:nth-child(1)').text()
                                if dt != '':
                                    ps.append(
                                        self.PriceItem(src, pn + ' - ' + dt, self.cur_date_stamp, p, int(time.time())))
                            elif tr('td:nth-child(2) p'):
                                for i in range(2):
                                    if tr('td:nth-child(2) p:nth-last-child(' + str(i+1) + ')') and re.match(
                                            r'\$ [\d\.]+$',
                                            tr('td:nth-child(2) p:nth-last-child(' + str(i+1) + ')').text()):
                                        p = float(
                                            tr('td:nth-child(2) p:nth-last-child(' + str(i+1) + ')').text().split(' ')[
                                                -1])
                                        if tr('td:nth-child(1) li:nth-last-child(' + str(i+1) + ')').text():
                                            dt = tr('td:nth-child(1) li:nth-last-child(' + str(i+1) + ')').text()
                                            ps.append(self.PriceItem(src, pn + ' - ' + dt + ' per 200 metres',
                                                                     self.cur_date_stamp, p, int(time.time())))
            for pi in ps:
                self.solve_price_item(pi)
        elif mtr_data_pattern.match(task.url):
            ss = re.findall(r'(?<=sid=)\d+', task.url)[0]
            ee = re.findall(r'(?<=eid=)\d+', task.url)[0]
            jdata = json.loads(doc.text())
            src = 'MTR'
            a_oct = float(jdata['a_oct'])
            a_tic = float(jdata['a_tic'])
            if ss + '_' + ee in self.mtr_lines:
                self.solve_price_item(
                    self.PriceItem(src, u'MTR - adult octopus, ' + self.mtr_lines[ss + '_' + ee][0],
                                   self.cur_date_stamp,
                                   a_oct,
                                   int(time.time())))
                self.solve_price_item(
                    self.PriceItem(src, u'MTR - adult ticket, ' + self.mtr_lines[ss + '_' + ee][0],
                                   self.cur_date_stamp,
                                   a_tic,
                                   int(time.time())))


def main():
    seeds = {'http://www.vmo.org/tc/index/page_winterprice/',
             'http://www.afcd.gov.hk/tc_chi/agriculture/agr_fresh/agr_fresh.html#5',
             'http://www3.consumer.org.hk/pricewatch/supermarket/',
             'https://www.towngas.com/tc/Household/Customer-Services/Tariff',
             'https://www.clp.com.hk/zh/customer-service/tariff/residential-customers',
             'http://www.td.gov.hk/en/transport_in_hong_kong/public_transport/taxi/taxi_fare_of_hong_kong/'}
    util.get_day_string('-', offset=0)
    for pid in products:
        if products[pid]['cat'] == 1:
            seeds.add('http://www.fmo.org.hk/fish-price?path=12_43_55&id=3&start=' +
                      util.get_day_string('-', offset=1) +
                      '&end=' +
                      util.get_day_string('-', offset=0) +
                      '&items%5B%5D=' +
                      str(pid))
    # add mtr tasks
    r = requests.get('http://www.mtr.com.hk/share/customer/js/jplannerdata_chi.js')
    mtr_lines = {}
    lname = u''
    lstart = None
    lend = None
    vl_res = re.findall(r'myValue.+', r.text)
    for vi in range(len(vl_res)):
        if re.match(r'.+lineValue\d+ = .+', vl_res[vi]):
            lns = re.findall(r'(?<=").+(?=")', vl_res[vi].split(';')[-2])
            if lns:
                ln = lns[0]
                sid = int(re.findall(r'(?<=").+(?=")', vl_res[vi].split(';')[0])[0])
                if ln == 'tcline,drline':
                    ln = 'drline'
                if lstart and (ln != lname or vi == len(vl_res) - 1) and not re.match(r'line\d+', ln):
                    if lname in mtr_line_names:
                        mtr_lines[str(lstart) + '_' + str(lend)] = [mtr_line_names[lname], lstart, int(lend)]
                    else:
                        print 'UNKNOWN LINE ' + lname
                if not lstart or ln != lname:
                    lname = ln
                    lstart = sid
                lend = sid
    for l in mtr_lines:
        seeds.add('http://www.mtr.com.hk/share/customer/include/getdata.php?&type=data&sid=' + str(
            mtr_lines[l][1]) + '&eid=' + str(mtr_lines[l][2]))
    spider_prices = SpiderPrices(seed_urls=seeds,
                                 regs=['http://www.afcd.gov.hk/tc_chi/agriculture/agr_fresh/agr_fresh.html',
                                       'http://www.vmo.org/tc/index/page_winterprice/',
                                       r'http://www\.fmo\.org\.hk/fish\-price\?path=12_43_55&id=3.+',
                                       'http://www3.consumer.org.hk/pricewatch/supermarket/',
                                       'https://www.towngas.com/tc/Household/Customer-Services/Tariff',
                                       'https://www.clp.com.hk/zh/customer-service/tariff/residential-customers',
                                       'http://www.td.gov.hk/en/transport_in_hong_kong/public_transport/taxi/taxi_fare_of_hong_kong/',
                                       'http://www\.mtr\.com\.hk/share/customer/include/getdata\.php\?&type=data&sid=\d+&eid=\d+'],
                                 MAX_DEPTH=0,
                                 THREAD_NUM=1)
    spider_prices.mtr_lines = mtr_lines
    spider_prices.start()
    time.sleep(3)
    # for stamp in spider_prices.prices:
    #     print stamp
    #     for pn in spider_prices.prices[stamp]:
    #         print pn + ' ' + str(spider_prices.prices[stamp][pn][0]) + ' ' + spider_prices.prices[stamp][pn][1]


if __name__ == '__main__':
    while True:
        # loop every 12 hours
        main()
        time.sleep(3600 * 12)
