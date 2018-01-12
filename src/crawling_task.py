# -*- coding:utf-8 -*-
import spiders.config
import time
from spiders import *
from spiders.common_news_spider import CommonNewsSpider
import spiders.common_news_spider
import gc
import logging

logger_con = logging.getLogger(spiders.config.COMMON_NEWS_SPIDER_CONSOLE_LOG_NAME)
logger_file = logging.getLogger(spiders.config.COMMON_NEWS_SPIDER_FILE_LOG_NAME)


def current_sec():
    return time.localtime().tm_hour*3600 + time.localtime().tm_min*60 + time.localtime().tm_sec


def run_spider_module(crawling_function=None, lazy_mode=False, offset=0, **kwargs):
    if lazy_mode:
        current_day_sec = current_sec()
        if not (((4*3600 + 45*60) < current_day_sec < (5*3600 + 15*60)) or ((10*3600 + 45*60) < current_day_sec < (11*3600 + 15*60)) or ((16*3600 + 45*60) < current_day_sec < (17*3600 + 15*60)) or ((22*3600 + 45*60) < current_day_sec < (23*3600 + 15*60))):
            return
    try:
        # run spider
        crawling_function(offset=offset, **kwargs)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, e:
        print type(e)
        print e
        logger_file.info(str(e))
        logger_con.info('Main task failure. Wait 5 seconds and continue.')
        logger_file.info('Main task failure. Wait 5 seconds and continue.')
        time.sleep(5)

if __name__ == '__main__':

    CommonNewsSpider.PUT_IN_STORAGE = True
    CommonNewsSpider.ADD_MEDIA = True
    CommonNewsSpider.DEFAULT_PUT_IN_FILE = False
    OFFSET = 0

    while True:

        print 'round start.'

        # pt spider
        run_spider_module(crawling_function=spider_passiontimes.SpiderPt.start_crawling, offset=OFFSET)

        # hk01 spider
        run_spider_module(crawling_function=spider_hk01.SpiderHK01.start_crawling, offset=OFFSET)

        # mk spider
        run_spider_module(crawling_function=spider_metro.SpiderMetro.start_crawling, offset=OFFSET)

        # gov spider
        run_spider_module(crawling_function=spider_govnews.SpiderGov.start_crawling, offset=OFFSET)

        # st spider
        run_spider_module(crawling_function=spider_standnews.SpiderStand.start_crawling, offset=OFFSET)

        # sina spider
        run_spider_module(crawling_function=spider_sina.SpiderSina.start_crawling, offset=OFFSET)

        # singtao spider
        run_spider_module(crawling_function=spider_singtao.SpiderSingTao.start_crawling, offset=OFFSET)

        # macao spider
        run_spider_module(crawling_function=spider_macao.SpiderMacao.start_crawling, offset=OFFSET)

        # wenwei spider
        run_spider_module(crawling_function=spider_wenwei.SpiderWenWei.start_crawling, offset=OFFSET)

        # takungpao spider
        run_spider_module(crawling_function=spider_takungpao.SpiderTaKungPao.start_crawling, offset=OFFSET)

        # hket spider
        run_spider_module(crawling_function=spider_hket.SpiderHKET.start_crawling, offset=OFFSET)

        # hkcd spider
        run_spider_module(crawling_function=spider_hkcd.SpiderHKCD.start_crawling, offset=OFFSET)

        # rthk spider
        run_spider_module(crawling_function=spider_rthk.SpiderRTHK.start_crawling, offset=OFFSET)

        # skypost spider
        run_spider_module(crawling_function=spider_skypost.SpiderSkyPost.start_crawling, offset=OFFSET)

        # hkej spider
        run_spider_module(crawling_function=spider_hkej.SpiderHKEJ.start_crawling, offset=OFFSET)

        # crntt spider
        run_spider_module(crawling_function=spider_crntt.SpiderCRN.start_crawling, offset=OFFSET)

        # vj spider
        run_spider_module(crawling_function=spider_vj.SpiderVJMedia.start_crawling, offset=OFFSET)

        # initium spider
        run_spider_module(crawling_function=spider_initium.SpiderInitium.start_crawling, offset=OFFSET)

        # bastille post spider
        run_spider_module(crawling_function=spider_bastillepost.SpiderBastillePost.start_crawling, offset=OFFSET)

        # cable news spider
        run_spider_module(crawling_function=spider_cablenews.SpiderCableNews.start_crawling, offset=OFFSET)

        # east week spider
        run_spider_module(crawling_function=spider_eastweek.SpiderEastWeek.start_crawling, offset=OFFSET)

        # am730 fresh news spider
        run_spider_module(crawling_function=spider_am730.SpiderAM730.start_crawling, offset=OFFSET)

        # am730 news with categories spider
        run_spider_module(crawling_function=spider_am730_cat.SpiderAM730Categories.start_crawling, offset=OFFSET)

        # finet spider
        run_spider_module(crawling_function=spider_finet.SpiderFinet.start_crawling, offset=OFFSET)

        # inmedia spider
        run_spider_module(crawling_function=spider_inmedia.SpiderInMedia.start_crawling, offset=OFFSET)

        # now news spider
        run_spider_module(crawling_function=spider_now.SpiderNow.start_crawling, offset=OFFSET)

        # commercial radio spider
        run_spider_module(crawling_function=spider_commercialradio.SpiderCommercialRadio.start_crawling, offset=OFFSET)

        # tvb spider
        run_spider_module(crawling_function=spider_tvb.SpiderTVB.start_crawling, offset=OFFSET)

        # legco spider
        run_spider_module(crawling_function=spider_legco.SpiderLegco.start_crawling, offset=OFFSET, lazy_mode=True)

        # oriental spider
        run_spider_module(crawling_function=spider_oriental.SpiderOriental.start_crawling, offset=OFFSET)

        # 852 spider
        run_spider_module(crawling_function=spider_852.Spider852.start_crawling, offset=OFFSET, lazy_mode=True)

        # bauhinia spider
        run_spider_module(crawling_function=spider_bauhinia.SpiderBauhinia.start_crawling, offset=OFFSET, lazy_mode=True)

        # bbc spider
        run_spider_module(crawling_function=spider_bbc.SpiderBBC.start_crawling, offset=OFFSET, lazy_mode=True)

        # edb spider
        run_spider_module(crawling_function=spider_edb.SpiderEDB.start_crawling, offset=OFFSET, lazy_mode=True)

        # fmco spider
        run_spider_module(crawling_function=spider_fmco.SpiderFmco.start_crawling, offset=OFFSET, lazy_mode=True)

        # hkcna spider
        run_spider_module(crawling_function=spider_hkcna.SpiderHKCNA.start_crawling, offset=OFFSET)

        # hkma spider
        run_spider_module(crawling_function=spider_hkma.SpiderHKMA.start_crawling, offset=OFFSET, lazy_mode=True)

        # hkpri spider
        run_spider_module(crawling_function=spider_hkpri.SpiderHKPRI.start_crawling, offset=OFFSET, lazy_mode=True)

        # localpress spider
        run_spider_module(crawling_function=spider_localpress.SpiderLocalpress.start_crawling, offset=OFFSET, lazy_mode=True)

        # locpg spider
        run_spider_module(crawling_function=spider_locpg.SpiderLocpg.start_crawling, offset=OFFSET, lazy_mode=True)

        # metro finance spider
        run_spider_module(crawling_function=spider_metrofinance.SpiderMetroFinance.start_crawling, offset=OFFSET)

        # newcentforum spider
        run_spider_module(crawling_function=spider_newcentforum.SpiderNewCenturyForum.start_crawling, offset=OFFSET, lazy_mode=True)

        # peanut spider
        run_spider_module(crawling_function=spider_peanut.SpiderPeanut.start_crawling, offset=OFFSET, lazy_mode=True)

        # savantas spider
        run_spider_module(crawling_function=spider_savantas.SpiderSavantas.start_crawling, offset=OFFSET, lazy_mode=True)

        # us consulate spider
        run_spider_module(crawling_function=spider_usconsulate.SpiderUSConsulate.start_crawling, offset=OFFSET, lazy_mode=True)

        # wsj spider
        run_spider_module(crawling_function=spider_wsj.SpiderWSJ.start_crawling, offset=OFFSET)

        # xinhua spider
        run_spider_module(crawling_function=spider_xinhua.SpiderXinhua.start_crawling, offset=OFFSET)

        # zaobao spider
        run_spider_module(crawling_function=spider_zaobao.SpiderZaobao.start_crawling, offset=OFFSET)

        # jd spider
        run_spider_module(crawling_function=spider_jd.SpiderJD.start_crawling, offset=OFFSET, lazy_mode=True)

        # reuters spider
        run_spider_module(crawling_function=spider_reuters.SpiderReuters.start_crawling, offset=OFFSET)

        # rfi spider
        run_spider_module(crawling_function=spider_rfi.SpiderRFI.start_crawling, offset=OFFSET)

        # scmp spider
        run_spider_module(crawling_function=spider_scmp.SpiderSCMP.start_crawling, offset=OFFSET)

        # speakout spider
        run_spider_module(crawling_function=spider_speakout.SpiderSpeakout.start_crawling, offset=OFFSET, lazy_mode=True)

        # people spider
        run_spider_module(crawling_function=spider_people.SpiderPeople.start_crawling, offset=OFFSET, lazy_mode=True)

        # govinfo spider
        run_spider_module(crawling_function=spider_govinfo.SpiderGovInfoNews.start_crawling, offset=OFFSET)

        # ubeat spider
        # run_spider_module(crawling_function=spider_ubeat.SpiderUBeat.start_crawling, offset=OFFSET)

        # am730 column spider
        run_spider_module(crawling_function=spider_730_column.Spider730Column.start_crawling, offset=OFFSET)

        # china daily spider
        run_spider_module(crawling_function=spider_chinadaily.SpiderChinaDaily.start_crawling, offset=OFFSET)

        # hkfp spider
        run_spider_module(crawling_function=spider_hkfp.SpiderHKFP.start_crawling, offset=OFFSET)

        # cnbc spider
        run_spider_module(crawling_function=spider_cnbc.SpiderCNBC.start_crawling, offset=OFFSET)

        # tmhk spider
        run_spider_module(crawling_function=spider_tmhk.SpiderTMHK.start_crawling, offset=OFFSET, lazy_mode=True)

        # standard spider
        run_spider_module(crawling_function=spider_standard.SpiderStandard.start_crawling, offset=OFFSET)

        # house news blogger spider
        run_spider_module(crawling_function=spider_housenews_blogger.SpiderHouseNewsBlogger.start_crawling, offset=OFFSET, lazy_mode=True)

        # house news blogger spider
        run_spider_module(crawling_function=spider_cool3c.SpiderCool3C.start_crawling, offset=OFFSET)

        # citizen news spider
        run_spider_module(crawling_function=spider_citizen.SpiderCitizen.start_crawling, offset=OFFSET)

        # news lens spider
        run_spider_module(crawling_function=spider_newslens.SpiderNewsLens.start_crawling, offset=OFFSET)

        # garbage collection
        clear_str = str(gc.collect())
        logger_con.info("Collect garbage: " + clear_str)
        logger_file.info("Collect garbage: " + clear_str)

        # wait for 10 seconds
        time.sleep(10)



