# -*- coding:utf-8 -*-
import requests
import urllib2
import re
from pyquery import PyQuery as pq
import threading
from json import *
import thread
import json
import time
import sys
import codecs
import urllib
import random
import gc
import spiders.util as util

'<div id="news-date">2016年7月14日 16:39 星期四</div>'
'<td id="main-left"><div style="font-weight:bold; color:#000; margin:25px 10px">2016年7月14日 星期四 16:40 </div></td>'
'<div class="date">2016/07/14 星期四 16:39</div>'
'<div style="float:left; font-size:15px">2016年07月14日 16:36 星期四</div>'

'''
ip_pattern = re.compile(ur'\d+\.\d+\.\d+\.\d')
_ips = set()
for i in range(2):
    print '**** New IPs: ****'
    ips = set()
    r = requests.get('http://proxy.com.ru/list_' + str(i+1) + '.html')
    r.encoding = 'gb2312'
    d = pq(r.text)
    for tr in d('tr').items():
        if ip_pattern.match(tr('td:nth-child(3)').text()) and (tr('td:nth-child(4)').text() == '80' or tr('td:nth-child(4)').text() == '8080'):
            print tr('td:nth-child(3)').text() + ':' + tr('td:nth-child(4)').text()
            ips.add(tr('td:nth-child(3)').text() + ':' + tr('td:nth-child(4)').text())
    print '**** Checking IPs: ****'
    for ip in ips:
        url = u'http://www.google.com'
        proxies = {'http': ip}
        proxy_support = urllib2.ProxyHandler(proxies)  # 注册代理
        opener = urllib2.build_opener(proxy_support)
        good = True
        try:
            response = opener.open(url, timeout=3)
        except Exception, e:
            good = False
            print e
            pass
        if good:
            _ips.add(ip)
    print '**** Valid IPs: ****'
    for ip in _ips:
        print ip
'''

'''
r = requests.get('http://www.kuaidaili.com/free/inha/1/')
d = pq(r.text)
for tr in d('.table tr').items():
    if ip_pattern.match(tr('td:nth-child(1)').text()):
        print tr('td:nth-child(1)').text() + ':' + tr('td:nth-child(2)').text()
        ips.add(tr('td:nth-child(1)').text() + ':' + tr('td:nth-child(2)').text())
print '*******************'
for ip in ips:
    url = u'http://www.google.com/'
    proxies = {'http': ip}
    proxy_support = urllib2.ProxyHandler(proxies)  # register the proxy
    opener = urllib2.build_opener(proxy_support)
    good = True
    try:
        response = opener.open(url, timeout=3)
    except Exception, e:
        good = False
        print e
        pass
    if good:
        _ips.add(ip)
print '++++++++++++++++++++'
for ip in _ips:
    print ip
'''

'''
from selenium import webdriver
from selenium import common
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

url = 'https://hk.news.yahoo.com/%E9%A2%B1%E9%A2%A8%E9%AE%8E%E9%AD%9A%E5%B0%87%E5%BD%A2%E6%88%90-%E4%B8%8B%E5%91%A8%E4%B8%AD%E5%9C%8B%E6%9D%B1%E5%8D%97%E6%B2%BF%E5%B2%B8%E7%8B%82%E9%A2%A8%E5%A4%A7%E9%A9%9F%E9%9B%A8-052800514.html'
driver = webdriver.PhantomJS('C://Users/benwu/Desktop/phantomjs.exe')
try:
    # PhantomJS('C://Users/benwu/Desktop/phantomjs.exe') # Ie('C://Users/benwu/Desktop/IEDriverServer.exe')# #
    driver.get(url)
    driver.execute_script('scrollTo(0, 10000);')
    d = pq(driver.page_source)
    while not d('#ugccmt-container'):
        d = pq(driver.page_source)
    while True:
        try:
            view_more = driver.find_element_by_class_name('ugccmt-view-more')
            driver.execute_script('scrollTo(0, 10000);')
            view_more.click()
        except common.exceptions.NoSuchElementException, e:
            print e
            break
    d = pq(driver.page_source)
    for cmt in d('.ugccmt-comment').items():
        print cmt('.ugccmt-user-cmt').text()
        print cmt('.ugccmt-commenttext').text()
finally:
    driver.close()
'''

import os.path

hash_pattern = re.compile(ur'#[àâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ\w\d_]+')


def get_hash_tag(s):
    return hash_pattern.findall(s)


if __name__ == '__main__':
    # r = requests.get('http://www.mtr.com.hk/share/customer/js/jplannerdata_chi.js')
    # d = pq(r.text)
    # print d.text()
    # sres = re.findall(r'(myValue\d+ = "\d+".+"\w+";\n+)+', d.text())
    # print sres
    ssss = u'''
    var all_station_row_count = 273;	// All station + 1;
var hk_station_row_count = 133;		// Last Hong Kong station + 1
var hk_station_wo_AEL_row_count = 115;
//Updated by kailey 2014/7/29
disableStationIds = "";

myValue0 = ""; caption0 = "-- 港島&#32171; --"; style0 = "background-color:#999999;color:#FFFFFF";
myValue1 = "83"; caption1 = "堅尼地城"; lineValue1 = "isline";
myValue2 = "82"; caption2 = "香港大學"; lineValue2 = "isline";
myValue3 = "81"; caption3 = "西營盤"; lineValue3 = "isline";
myValue4 = "26"; caption4 = "上環"; lineValue4 = "isline";
myValue5 = "1"; caption5 = "中環"; lineValue5 = "isline";
myValue6 = "2"; caption6 = "金鐘"; lineValue6 = "isline";
myValue7 = "27"; caption7 = "灣仔"; lineValue7 = "isline";
myValue8 = "28"; caption8 = "銅鑼灣"; lineValue8 = "isline";
myValue9 = "29"; caption9 = "天后"; lineValue9 = "isline";
myValue10 = "30"; caption10 = "炮台山"; lineValue10 = "isline";
myValue11 = "31"; caption11 = "北角"; lineValue11 = "isline";
myValue12 = "32"; caption12 = "&#x9C02;魚涌"; lineValue12 = "isline";
myValue13 = "33"; caption13 = "太古"; lineValue13 = "isline";
myValue14 = "34"; caption14 = "西灣河"; lineValue14 = "isline";
myValue15 = "35"; caption15 = "筲箕灣"; lineValue15 = "isline";
myValue16 = "36"; caption16 = "杏花&#37032;"; lineValue16 = "isline";
myValue17 = "37"; caption17 = "柴灣"; lineValue17 = "isline";
myValue18 = ""; caption18 = "";

myValue19 = ""; caption19 = "-- 南港島&#32171; --"; style19 = "background-color:#999999;color:#FFFFFF";
myValue20 = "2"; caption20 = "金鐘"; lineValue20 = "siline";
myValue21 = "86"; caption21 = "海洋公園"; lineValue21 = "siline";
myValue22 = "87"; caption22 = "黃竹坑"; lineValue22 = "siline";
myValue23 = "88"; caption23 = "利東"; lineValue23 = "siline";
myValue24 = "89"; caption24 = "海怡半島"; lineValue24 = "siline";
myValue25 = ""; caption25 = "";

myValue26 = ""; caption26 = "-- 觀塘&#32171; --"; style26 = "background-color:#999999;color:#FFFFFF";
myValue27 = "85"; caption27 = "黃埔"; lineValue27 = "ktline";
myValue28 = "84"; caption28 = "何文田"; lineValue28 = "ktline";
myValue29 = "5"; caption29 = "油麻地"; lineValue29 = "ktline";
myValue30 = "6"; caption30 = "旺角"; lineValue30 = "ktline";
myValue31 = "16"; caption31 = "太子"; lineValue31 = "ktline";
myValue32 = "7"; caption32 = "石硤尾"; lineValue32 = "ktline";
myValue33 = "8"; caption33 = "九龍塘"; lineValue33 = "ktline";
myValue34 = "9"; caption34 = "樂富"; lineValue34 = "ktline";
myValue35 = "10"; caption35 = "黃大仙"; lineValue35 = "ktline";
myValue36 = "11"; caption36 = "鑽石山"; lineValue36 = "ktline";
myValue37 = "12"; caption37 = "彩虹"; lineValue37 = "ktline";
myValue38 = "13"; caption38 = "九龍灣"; lineValue38 = "ktline";
myValue39 = "14"; caption39 = "牛頭角"; lineValue39 = "ktline";
myValue40 = "15"; caption40 = "觀塘"; lineValue40 = "ktline";
myValue41 = "38"; caption41 = "藍田"; lineValue41 = "ktline";
myValue42 = "48"; caption42 = "油塘"; lineValue42 = "ktline";
myValue43 = "49"; caption43 = "調景嶺"; lineValue43 = "ktline";
myValue44 = ""; caption44 = "";

myValue45 = ""; caption45 = "-- 荃灣&#32171; --"; style45 = "background-color:#999999;color:#FFFFFF";
myValue46 = "1"; caption46 = "中環"; lineValue46 = "twline";
myValue47 = "2"; caption47 = "金鐘"; lineValue47 = "twline";
myValue48 = "3"; caption48 = "尖沙咀"; lineValue48 = "twline";
myValue49 = "4"; caption49 = "佐敦"; lineValue49 = "twline";
myValue50 = "5"; caption50 = "油麻地"; lineValue50 = "twline";
myValue51 = "6"; caption51 = "旺角"; lineValue51 = "twline";
myValue52 = "16"; caption52 = "太子"; lineValue52 = "twline";
myValue53 = "17"; caption53 = "深水&#22487;"; lineValue53 = "twline";
myValue54 = "18"; caption54 = "長沙灣"; lineValue54 = "twline";
myValue55 = "19"; caption55 = "&#x8318;枝角"; lineValue55 = "twline";
myValue56 = "20"; caption56 = "美孚"; lineValue56 = "twline";
myValue57 = "21"; caption57 = "&#x8318;景"; lineValue57 = "twline";

myValue58 = "22"; caption58 = "葵芳"; lineValue58 = "twline";
myValue59 = "23"; caption59 = "葵興"; lineValue59 = "twline";
myValue60 = "24"; caption60 = "大窩口"; lineValue60 = "twline";
myValue61 = "25"; caption61 ="荃灣"; lineValue61 = "twline";
myValue62 = ""; caption62 = "";

myValue63 = ""; caption63 = "-- 將軍澳&#32171; --"; style63 = "background-color:#999999;color:#FFFFFF";
myValue64 = "31"; caption64 = "北角"; lineValue64 = "tkline";
myValue65 = "32"; caption65 = "&#x9C02;魚涌"; lineValue65 = "tkline";
myValue66 = "48"; caption66 = "油塘"; lineValue66 = "tkline";
myValue67 = "49"; caption67 = "調景嶺"; lineValue67 = "tkline";
myValue68 = "50"; caption68 = "將軍澳"; lineValue68 = "tkline";
myValue69 = "51"; caption69 = "坑口"; lineValue69 = "tkline";
myValue70 = "52"; caption70 = "寶琳"; lineValue70 = "tkline";
myValue71 = "57"; caption71 = "康城"; lineValue71 = "tkline";
myValue72 = ""; caption72 = "";

myValue73 = ""; caption73 = "-- 東涌&#32171;及迪士尼&#32171; -- "; style73 = "background-color:#999999;color:#FFFFFF";
myValue74 = ""; caption74 = ""; style74 = "";
myValue75 = "39"; caption75 = "香港"; lineValue75 = "tcline";
myValue76 = "40"; caption76 = "九龍"; lineValue76 = "tcline";
myValue77 = "41"; caption77 = "奧運"; lineValue77 = "tcline";
myValue78 = "53"; caption78 = "南昌"; lineValue78 = "tcline";
myValue79 = "21"; caption79 = "&#x8318;景"; lineValue79 = "tcline";
myValue80 = "42"; caption80 = "青衣"; lineValue80 = "tcline";
myValue81 = "43"; caption81 = "東涌"; lineValue81 = "tcline";
myValue82 = "54"; caption82 = "欣澳"; lineValue82 = "tcline,drline";
myValue83 = "55"; caption83 = "迪士尼"; lineValue83 = "drline";
myValue84 = ""; caption84 = "";
myValue85 = ""; caption85 = ""; style85 = "display: none";

myValue86 = ""; caption86 = "-- 東鐵&#32171; --"; style86 = "background-color:#999999;color:#FFFFFF";
myValue87 = "64"; caption87 = "紅磡"; lineValue87 = "erline";
myValue88 = "65"; caption88 = "旺角東"; lineValue88 = "erline";
myValue89 = "8"; caption89 = "九龍塘"; lineValue89 = "erline";
myValue90 = "67"; caption90 = "大圍"; lineValue90 = "erline";
myValue91 = "68"; caption91 = "沙田"; lineValue91 = "erline";
myValue92 = "69"; caption92 = "火炭"; lineValue92 = "erline";
myValue93 = "70"; caption93 = "馬場"; lineValue93 = "erline";
myValue94 = "71"; caption94 = "大學"; lineValue94 = "erline";
myValue95 = "72"; caption95 = "大埔墟"; lineValue95 = "erline";
myValue96 = "73"; caption96 = "太和"; lineValue96 = "erline";
myValue97 = "74"; caption97 = "粉嶺"; lineValue97 = "erline";
myValue98 = "75"; caption98 = "上水"; lineValue98 = "erline";
myValue99 = "78"; caption99 = "落馬洲"; lineValue99 = "erline";
myValue100 = "76"; caption100 = "羅湖"; lineValue100 = "erline";
myValue101 = ""; caption101 = "";

myValue102 = ""; caption102 = "-- 馬鞍山&#32171; --"; style102 = "background-color:#999999;color:#FFFFFF";
myValue103 = "67"; caption103 = "大圍"; lineValue103 = "moline";
myValue104 = "96"; caption104 = "車公廟"; lineValue104 = "moline";
myValue105 = "97"; caption105 = "沙田圍"; lineValue105 = "moline";
myValue106 = "98"; caption106 = "第一城"; lineValue106 = "moline";
myValue107 = "99"; caption107 = "石門"; lineValue107 = "moline";
myValue108 = "100"; caption108 = "大水坑"; lineValue108 = "moline";
myValue109 = "101"; caption109 = "恆安"; lineValue109 = "moline";
myValue110 = "102"; caption110 = "馬鞍山"; lineValue110 = "moline";
myValue111 = "103"; caption111 = "烏溪沙"; lineValue111 = "moline";
myValue112 = ""; caption112 = "";

myValue113 = ""; caption113 = "-- 西鐵&#32171; --"; style113 = "background-color:#999999;color:#FFFFFF";
myValue114 = "64"; caption114 = "紅磡"; lineValue114 = "wrline";
myValue115 = "80"; caption115 = "尖東"; lineValue115 = "wrline";
myValue116 = "111"; caption116 = "柯士甸"; lineValue116 = "wrline";
myValue117 = "53"; caption117 = "南昌"; lineValue117 = "wrline";
myValue118 = "20"; caption118 = "美孚"; lineValue118 = "wrline";
myValue119 = "114"; caption119 = "荃灣西"; lineValue119 = "wrline";
myValue120 = "115"; caption120 = "錦上路"; lineValue120 = "wrline";
myValue121 = "116"; caption121 = "元朗"; lineValue121 = "wrline";
myValue122 = "117"; caption122 = "朗屏"; lineValue122 = "wrline";
myValue123 = "118"; caption123 = "天水圍"; lineValue123 = "wrline";
myValue124 = "119"; caption124 = "兆康"; lineValue124 = "wrline";
myValue125 = "120"; caption125 = "屯門"; lineValue125 = "wrline";
myValue126 = ""; caption126 = "";

myValue127 = ""; caption127 = "-- 機場快&#32171; --"; style127 = "background-color:#999999;color:#FFFFFF";
myValue128 = "44"; caption128 = "香港"; lineValue128 = "aeline";
myValue129 = "45"; caption129 = "九龍"; lineValue129 = "aeline";
myValue130 = "46"; caption130 = "青衣"; lineValue130 = "aeline";
myValue131 = "47"; caption131 = "機場"; lineValue131 = "aeline";
myValue132 = "56"; caption132 = "博覽館"; lineValue132 = "aeline";
myValue133 = ""; caption133 = "";

myValue134 = ""; caption134 = "-- 深圳一&#32171; --"; style134 = "background-color:#999999;color:#FFFFFF";
myValue135 = "516"; caption135 = "羅湖(深圳)"; lineValue135 = "line1";
myValue136 = "517"; caption136 = "國貿"; lineValue136 = "line1";
myValue137 = "518"; caption137 = "老街"; lineValue137 = "line1";
myValue138 = "519"; caption138 = "大劇院"; lineValue138 = "line1";
myValue139 = "520"; caption139 = "科學館"; lineValue139 = "line1";
myValue140 = "521"; caption140 = "華強路"; lineValue140 = "line1";
myValue141 = "522"; caption141 = "崗夏"; lineValue141 = "line1";
myValue142 = "503"; caption142 = "會展中心"; lineValue142 = "line1";

myValue143 = "523"; caption143 = "購物公園"; lineValue143 = "line1";
myValue144 = "524"; caption144 = "香蜜湖"; lineValue144 = "line1";
myValue145 = "525"; caption145 = "車公廟(深圳)"; lineValue145 = "line1";
myValue146 = "526"; caption146 = "竹子林"; lineValue146 = "line1";
myValue147 = "527"; caption147 = "僑城東"; lineValue147 = "line1";
myValue148 = "528"; caption148 = "華僑城"; lineValue148 = "line1";
myValue149 = "529"; caption149 = "世界之窗"; lineValue149 = "line1";
myValue150 = "530"; caption150 = "白石洲"; lineValue150 = "line1";
myValue151 = "531"; caption151 = "高新園"; lineValue151 = "line1";
myValue152 = "532"; caption152 = "深大"; lineValue152 = "line1";
myValue153 = "533"; caption153 = "桃園"; lineValue153 = "line1";
myValue154 = "534"; caption154 = "大新"; lineValue154 = "line1";
myValue155 = "535"; caption155 = "鯉魚門"; lineValue155 = "line1";
myValue156 = "536"; caption156 = "前海灣"; lineValue156 = "line1";
myValue157 = "537"; caption157 = "新安"; lineValue157 = "line1";
myValue158 = "538"; caption158 = "寶安中心"; lineValue158 = "line1";
myValue159 = "539"; caption159 = "寶體"; lineValue159 = "line1";
myValue160 = "540"; caption160 = "坪洲"; lineValue160 = "line1";
myValue161 = "541"; caption161 = "西鄉"; lineValue161 = "line1";
myValue162 = "542"; caption162 = "固戍"; lineValue162 = "line1";
myValue163 = "543"; caption163 = "後瑞"; lineValue163 = "line1";
myValue164 = "544"; caption164 = "機場東"; lineValue164 = "line1";
myValue165 = ""; caption165 = "";

myValue166 = ""; caption166 = "-- 深圳二&#32171; --"; style166 = "background-color:#999999;color:#FFFFFF";
myValue167 = "545"; caption167 = "赤灣"; lineValue167 = "line2";
myValue168 = "546"; caption168 = "蛇口港"; lineValue168 = "line2";
myValue169 = "547"; caption169 = "海上世界"; lineValue169 = "line2";
myValue170 = "548"; caption170 = "水灣"; lineValue170 = "line2";
myValue171 = "549"; caption171 = "東角頭"; lineValue171 = "line2";
myValue172 = "550"; caption172 = "灣廈"; lineValue172 = "line2";
myValue173 = "551"; caption173 = "海月"; lineValue173 = "line2";
myValue174 = "552"; caption174 = "登良"; lineValue174 = "line2";
myValue175 = "553"; caption175 = "后海"; lineValue175 = "line2";
myValue176 = "554"; caption176 = "科苑"; lineValue176 = "line2";
myValue177 = "555"; caption177 = "紅樹灣"; lineValue177 = "line2";
myValue178 = "529"; caption178 = "世界之窗"; lineValue178 = "line2";
myValue179 = "556"; caption179 = "僑城北"; lineValue179 = "line2";
myValue180 = "557"; caption180 = "深康"; lineValue180 = "line2";
myValue181 = "558"; caption181 = "安托山"; lineValue181 = "line2";
myValue182 = "559"; caption182 = "僑香"; lineValue182 = "line2";
myValue183 = "560"; caption183 = "香蜜"; lineValue183 = "line2";
myValue184 = "561"; caption184 = "香梅北"; lineValue184 = "line2";
myValue185 = "562"; caption185 = "景田"; lineValue185 = "line2";
myValue186 = "563"; caption186 = "蓮花西"; lineValue186 = "line2";
myValue187 = "564"; caption187 = "福田"; lineValue187 = "line2";
myValue188 = "504"; caption188 = "市民中心"; lineValue188 = "line2";
myValue189 = "565"; caption189 = "崗廈北"; lineValue189 = "line2";
myValue190 = "566"; caption190 = "華強北"; lineValue190 = "line2";
myValue191 = "567"; caption191 = "燕南"; lineValue191 = "line2";
myValue192 = "519"; caption192 = "大劇院"; lineValue192 = "line2";
myValue193 = "568"; caption193 = "湖貝"; lineValue193 = "line2";
myValue194 = "569"; caption194 = "黃貝嶺"; lineValue194 = "line2";
myValue195 = "570"; caption195 = "新秀"; lineValue195 = "line2";
myValue196 = ""; caption196 = "";

myValue197 = ""; caption197 = "-- 深圳三&#32171; --"; style197 = "background-color:#999999;color:#FFFFFF";
myValue198 = "571"; caption198 = "益田"; lineValue198 = "line3";
myValue199 = "572"; caption199 = "石廈"; lineValue199 = "line3";
myValue200 = "523"; caption200 = "購物公園"; lineValue200 = "line3";
myValue201 = "564"; caption201 = "福田"; lineValue201 = "line3";
myValue202 = "505"; caption202 = "少年宮"; lineValue202 = "line3";
myValue203 = "573"; caption203 = "蓮花村"; lineValue203 = "line3";
myValue204 = "574"; caption204 = "華新"; lineValue204 = "line3";
myValue205 = "575"; caption205 = "通心嶺"; lineValue205 = "line3";
myValue206 = "576"; caption206 = "紅嶺"; lineValue206 = "line3";
myValue207 = "518"; caption207 = "老街"; lineValue207 = "line3";
myValue208 = "577"; caption208 = "曬布"; lineValue208 = "line3";
myValue209 = "578"; caption209 = "翠竹"; lineValue209 = "line3";
myValue210 = "579"; caption210 = "田貝"; lineValue210 = "line3";
myValue211 = "580"; caption211 = "水貝"; lineValue211 = "line3";
myValue212 = "581"; caption212 = "草埔"; lineValue212 = "line3";
myValue213 = "582"; caption213 = "布吉"; lineValue213 = "line3";
myValue214 = "583"; caption214 = "木棉灣"; lineValue214 = "line3";
myValue215 = "584"; caption215 = "大芬"; lineValue215 = "line3";
myValue216 = "585"; caption216 = "丹竹頭"; lineValue216 = "line3";
myValue217 = "586"; caption217 = "六約"; lineValue217 = "line3";
myValue218 = "587"; caption218 = "塘坑"; lineValue218 = "line3";
myValue219 = "588"; caption219 = "橫崗"; lineValue219 = "line3";
myValue220 = "589"; caption220 = "永湖"; lineValue220 = "line3";
myValue221 = "590"; caption221 = "荷坳"; lineValue221 = "line3";
myValue222 = "591"; caption222 = "大運"; lineValue222 = "line3";
myValue223 = "592"; caption223 = "愛聯"; lineValue223 = "line3";
myValue224 = "593"; caption224 = "吉祥"; lineValue224 = "line3";
myValue225 = "594"; caption225 = "龍城廣場"; lineValue225 = "line3";
myValue226 = "595"; caption226 = "南聯"; lineValue226 = "line3";
myValue227 = "596"; caption227 = "雙龍"; lineValue227 = "line3";
myValue228 = ""; caption228 = "";

myValue229 = ""; caption229 = "-- 深圳四&#32171; --"; style229 = "background-color:#999999;color:#FFFFFF";
myValue230 = "501"; caption230 = "福田口岸"; lineValue230 = "line4";
myValue231 = "502"; caption231 = "福民"; lineValue231 = "line4";
myValue232 = "503"; caption232 = "會展中心"; lineValue232 = "line4";
myValue233 = "504"; caption233 = "市民中心"; lineValue233 = "line4";
myValue234 = "505"; caption234 = "少年宮"; lineValue234 = "line4";
myValue235 = "506"; caption235 = "蓮花北"; lineValue235 = "line4";
myValue236 = "507"; caption236 = "上梅林"; lineValue236 = "line4";
myValue237 = "508"; caption237 = "民樂"; lineValue237 = "line4";
myValue238 = "509"; caption238 = "白石龍"; lineValue238 = "line4";
myValue239 = "510"; caption239 = "深圳北站"; lineValue239 = "line4";
myValue240 = "511"; caption240 = "紅山"; lineValue240 = "line4";
myValue241 = "512"; caption241 = "上塘"; lineValue241 = "line4";
myValue242 = "513"; caption242 = "龍勝"; lineValue242 = "line4";
myValue243 = "514"; caption243 = "龍華"; lineValue243 = "line4";
myValue244 = "515"; caption244 = "清湖"; lineValue244 = "line4";
myValue245 = ""; caption245 = "";

myValue246 = ""; caption246 = "-- 深圳五&#32171; --"; style246 = "background-color:#999999;color:#FFFFFF";
myValue247 = "597"; caption247 = "臨海"; lineValue247 = "line5";
myValue248 = "598"; caption248 = "寶華"; lineValue248 = "line5";
myValue249 = "538"; caption249 = "寶安中心"; lineValue249 = "line5";
myValue250 = "599"; caption250 = "翻身"; lineValue250 = "line5";
myValue251 = "600"; caption251 = "靈芝"; lineValue251 = "line5";
myValue252 = "601"; caption252 = "洪浪北"; lineValue252 = "line5";
myValue253 = "602"; caption253 = "興東"; lineValue253 = "line5";
myValue254 = "603"; caption254 = "留仙洞"; lineValue254 = "line5";
myValue255 = "604"; caption255 = "西麗"; lineValue255 = "line5";
myValue256 = "605"; caption256 = "大學城"; lineValue256 = "line5";
myValue257 = "606"; caption257 = "塘朗"; lineValue257 = "line5";
myValue258 = "607"; caption258 = "長嶺陂"; lineValue258 = "line5";
myValue259 = "510"; caption259 = "深圳北站"; lineValue259 = "line5";
myValue260 = "608"; caption260 = "民治"; lineValue260 = "line5";
myValue261 = "609"; caption261 = "五和"; lineValue261 = "line5";
myValue262 = "610"; caption262 = "&#22338;田"; lineValue262 = "line5";
myValue263 = "611"; caption263 = "楊美"; lineValue263 = "line5";
myValue264 = "612"; caption264 = "上水徑"; lineValue264 = "line5";
myValue265 = "613"; caption265 = "下水徑"; lineValue265 = "line5";
myValue266 = "614"; caption266 = "長龍"; lineValue266 = "line5";
myValue267 = "582"; caption267 = "布吉"; lineValue267 = "line5";
myValue268 = "615"; caption268 = "百鴿籠"; lineValue268 = "line5";
myValue269 = "616"; caption269 = "布心"; lineValue269 = "line5";
myValue270 = "617"; caption270 = "太安"; lineValue270 = "line5";
myValue271 = "618"; caption271 = "怡景"; lineValue271 = "line5";
myValue272 = "569"; caption272 = "黃貝嶺"; lineValue272 = "line5";

var myValueArr = new Array();
var captionArr = new Array();
var lineValueArr = new Array();
//Old Station
//var styleArr = new Array("style0","style19","style36","style54","style64","style77","style93","style104","style118","style125","style157","style188","style220","style237");
var styleArr = new Array("style0","style19","style26","style45","style63","style73","style86","style102","style113","style127","style134","style166","style197","style229","style246");
// var hr_byStationMyValueArr = new Array('40','8','13','75','612','507','512','26','613','100','584','72','67','534','591','24','519','71','605','1','585','609','116','586','118','29','16','33','617','73','505','120','583','580','548','69','14','529','31','504','616','582','608','508','589','579','530','509','99','7','572','119','593','553','558','3','80','615','526','518','541','83','604','34','4','610','51','36','68','97','545','96','525','542','540','618','6','65','549','43','54','5','48','2','18','614','607','42','536','53','595','543','101','111','601','30','554','520','511','555','64','576','20','55','561','39','82','560','524','117','37','533','547','551','103','603','571','74','25','114','581','19','21','70','102','531','517','81','50','522','565','57','12','532','17','510','557','515','98','590','546','575','56','562','568','552','566','521','574','528','10','569','587','606','41','592','537','570','503','611','35','78','22','23','556','527','559','502','564','501','578','28','9','506','563','573','49','47','544','588','567','602','115','594','513','514','597','523','599','38','596','535','76','516','538','52','598','539','32','577','600','27','550','15','11');
var hr_byStationMyValueArr = new Array('2','592','47','544','558','56','111','615','509','530','610','538','539','598','582','616','581','28','1','37','607','614','96','525','18','505','545','12','98','504','503','578','584','585','534','552','11','55','549','80','74','599','69','30','502','501','564','522','565','519','517','542','551','51','590','36','101','588','531','82','39','601','576','511','555','553','543','569','566','521','574','568','64','562','593','4','115','81','554','40','13','8','22','23','15','19','21','38','518','506','563','573','600','597','603','586','535','76','57','9','78','117','594','514','513','516','102','20','508','608','65','6','583','53','595','14','31','528','41','540','52','16','536','527','556','559','515','32','70','34','83','520','547','68','97','577','17','507','612','512','35','7','99','546','557','510','532','75','26','572','523','596','580','548','119','54','72','100','67','73','24','617','33','587','606','533','579','29','118','49','575','50','3','42','25','114','120','43','591','71','605','27','550','529','10','103','609','561','560','524','613','604','537','602','570','541','611','567','5','48','618','571','589','116','526');
// var filterValueArr = [0,19,36,37,38,41,42,43,54,55,56,57,58,64,65,70,77,80,93,94,104,105,108,109,118,119,121,120,125,157,183,188,191,192,198,220,224,237,258,263];
var filterValueArr = [0,19,20,26,45,46,47,50,51,52,63,64,65,66,67,73,74,79,86,89,102,103,113,114,117,118,127,128,129,130,134,166,192,197,200,201,207,229,233,246,267,272];

//------ For Service Hours (service_hours_search.php) - 20 June, 2016 -----
var lineMapping = {
	"EAL" : "東鐵&#32171;",
	"KTL" : "觀塘&#32171;",
	"TWL" : "荃灣&#32171;",
	"ISL" : "港島&#32171;",
	"TCL" : "東涌&#32171;",
	"AEL" : "機場快&#32171;",
	"TKL" : "將軍澳&#32171;",
	"WRL" : "西鐵&#32171;",
	"MOL" : "馬鞍山&#32171;",
	"DRL" : "迪士尼&#32171;",
	"SIL" : "南港島&#32171;"
};    '''


