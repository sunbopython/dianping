#!/usr/bin/python3
# -*- coding: utf-8 -*-

from dianping.catalog.classfysubdict import Classify 
#from dianping.catalog.classfysubdict_sp_for_food import Classify  # contempory:for food channel
#from dianping.catalog.classfysubdict_sp_for_shopping import Classify  # contempory:for shopping channel
from dianping.catalog.regiondict import Region
from scrapy.spiders import Spider, CrawlSpider, Rule
from scrapy.http.request import Request
from scrapy.http.response import Response
from dianping.items import ShopItem
import logging
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from dianping.utils.dianping_poi import decode
from dianping.dbconnect import connection
import codecs

cur1, conn1 = connection() 

class Dianping(Spider):
    """This is dianping spider
    """
    allowed_domains = ['dianping.com']
    baseurl = "http://www.dianping.com"
    name = "dianping"
    _city_id = 2
    _city_pingyin = "beijing"
    # the third item within the tuple of REGION var. is for hotel channel only
    REGION = [('r14','朝阳区','c226'),
            ('r17','海淀区','c274'),
            ('r15','东城区','c242'),
            ('r16','西城区','c258'),
            ('r20','丰台区','c322'),
            ('r5952','大兴区','c95234'),
            ('r5950','昌平区','95202'),
            ('r5951','通州区','95218'),
            ('r328','石景山区','c5250'),
            ('r9158','顺义区','c146530'),
            ('r27615','怀柔区','c441842'),
            ('r9157','房山区','c146514'),
            ('r27614','门头沟区','c441826'),
            ('r27616','平谷区','c441858'),
            ('c434','密云县','c6946'),
            ('c435','延庆县','c6962')]

    website_possible_httpstatus_list = [200,307,403, 404, 408, 500, 502, 503, 504]


    def _extract_classify(self):
        """ extract classifyid for use to build complete url

            Returns: 
                channelID,channel,classifyID,classifyname,classifysubID,classifysubname,label
                ('10','美食','g110','火锅','g3027','鱼火锅','classifysub')
                or
                ('25','电影','g136','电影院','classify')
                or
                ('60','酒店','g172','青年旅社','classify')

        """
        for channel, classifylist in Classify().items():
            crawl_just_one_channel = False
            if not crawl_just_one_channel:
            #if channel[2]=='美食':        
            #if channel[2]=='电影':         
            #if channel[2]=='休闲娱乐':     
            #if channel[2]=='酒店':         
            #if channel[2]=='丽人':         
            #if channel[2]=='k歌':          
            #if channel[2]=='运动健身':     
            #if channel[2]=='景点':         
            #if channel[2]=='亲子':         
            #if channel[2]=='结婚':         
            #if channel[2]=='购物':         
            #if channel[2]=='宠物':         
            #if channel[2]=='生活服务':     
            #if channel[2]=='学习培训':      
            #if channel[2]=='爱车':         
            #if channel[2]=='医疗健康':     
            #if channel[2]=='家装':         
            #if channel[2]=='宴会':         
                for classify in classifylist:
                    if len(classify) == 3:
                        for classifysub_index, classifysub in enumerate(classify[2]):
                            #if classifysub_index==0:  # only use "不限"
                            # the following is open the gate of classifysub
                            if classifysub_index>0:   # do not use "不限" but use the classfysub
                                classifysub_id = str(classifysub[0])
                                classifysub_name = str(classifysub[1])
                                msg = "classifysub"
                                yield  str(channel[1]), str(channel[2]), classify[0],\
                                    classify[1], classifysub_id, classifysub_name, msg
                    elif len(classify)==2:
                        classify_id = str(classify[0])
                        classify_name = str(classify[1])
                        msg = "classify"
                        yield  str(channel[1]), str(channel[2]), classify_id, classify_name, msg
            else:
                print("Please uncomment one of the above if statement first ")

    def _build_classify_url_ignore_region(self):
        """build url without considering region part
        """
        for classifyx in self._extract_classify():
            if classifyx[1]=="酒店":
                #if classifyx[-2]=='五星级/豪华型':  # locking only this classify for test
                url = "http://www.dianping.com/"+self._city_pingyin+\
                        "/hotel/"+classifyx[-3]    #[-3] is classifyid
                yield url, classifyx[-2]   # [-2] is clasifyname etc. '经济酒店'
            elif classifyx[1] == "结婚":
                #"旅游婚纱"  do not have region classify http://www.dianping.com/wedding/travel/2
                #"婚宴"   http://www.dianping.com/wedding/hunyan?categoryIds=165&cityId=2
                if classifyx[3]=="旅游婚纱":
                    url = "http://www.dianping.com/wedding/travel/2"
                    yield url,classifyx[3]
                elif classifyx[3]=="婚宴":
                    url ="http://www.dianping.com/wedding/hunyan?categoryIds=165&cityId=2"
                    yield url,classifyx[3]
                else:
                    url = "http://www.dianping.com/search/category/"+str(self._city_id)+\
                        "/"+classifyx[0]+"/"+classifyx[-3]    #[-3] is either classifyid or classifysubid
                    yield url, classifyx[-2]   # [-2] is either clasifyname or classifysubname

            elif classifyx[1] == "宴会":
                # ignore classify also
                url = "http://www.dianping.com/search/category/"+str(self._city_id)+\
                    "/" + classifyx[0]
                yield url, "宴会全部"
            else:
                #print(classifyx)
                #if classifyx[3]=='其他': # locking only this classify for test
                url = "http://www.dianping.com/search/category/"+str(self._city_id)+\
                        "/"+classifyx[0]+"/"+classifyx[-3]    #[0] channle id [-3] is either classifyid or classifysubid
                yield url, classifyx[-2]   # [-2] is either clasifyname or classifysubname

            
    def start_requests(self):
        for count, (url, classifyx) in enumerate(self._build_classify_url_ignore_region()):  
            # locking only one classification or one classificationsub 
            # if count ==0:
            if classifyx == "宴会全部":
                yield Request(url=url,callback=self.parse_classify_region,meta={'classifyx':classifyx})
            elif classifyx == "旅游婚纱":
                yield Request(url=url,callback=self.parse_classify_region,meta={'classifyx':classifyx})
            elif classifyx=="婚宴":
                yield Request(url=url,callback=self.parse_classify_region,meta={'classifyx':classifyx})
            elif self.is_belong_to_hotel_channel(classifyx):
                # miyun and yanqing, it indirect to home page, 
                for region in self.REGION:
                        #if region[1]=='朝阳区':   # locking only one region 
                        # method-1 use classify
                        #yield Request(url=url+region[0]+region[2],callback=self.parse_classify_region,meta={'region':region[1],'classifyx':classifyx})
                        # method-3 do not use classify
                    yield Request(url="http://www.dianping.com/"+self._city_pingyin+"/hotel/"+region[0]+region[2],callback=self.parse_classify_region,meta={'region':region[1],'classifyx':classifyx})
            else:  
                for region in self.REGION:
                    #if region[1] == '东城区':   # locking only one region
                    yield Request(url=url+region[0],callback=self.parse_classify_region,meta={'region':region[1],'classifyx':classifyx})

    def parse_classify_region(self,response):
        """parse region especillly subregion id  'region-nav-sub'
        """
        
        classifyx = response.meta.get('classifyx')
        region = response.meta.get('region')
        
        max_page_of_this_region = self.get_max_page(response,classifyx)

        if self.is_belong_to_hall_channel(classifyx):
            # all the index pages are below 50
            for request_or_item in self.parse_hall_index(response):
                yield request_or_item

        elif self.is_belong_to_hotel_channel(classifyx):
            # As for some regions like miyun and yanqing, it indirect to home page, 
            # they would been ignored
            if max_page_of_this_region < 50:
                for request_or_item in self.parse_hotel_index(response):   # response with two parameaters(region and classify)
                    yield request_or_item 
            else:
                # following codes are temporary,just tell me which classify needs especially handle
                sum_of_this_region = response.xpath("//span[@class='detail']/text()").re(r'[0-9]+')[0] 
                print("We met difficult situation here, because max_page_of_this_region is above 50")
                with open('loss_statistics_for_.txt',mode='a',encoding='utf-8') as f:
                    writing_str = "{},{},{},{}'\n'".format("酒店",classifyx,region,sum_of_this_region)
                    f.write(writing_str)

                # if subregion exits, make request for every subregion and pass to parse_index
                # if subregion not exits, parse response directly
                if response.xpath("//div[@class='recom J_choice-content-2nd ']/a").extract().__len__() == 1:
                    logging.info("situation2 here")
                    for request_or_item2 in self.parse_hotel_index(response):  # 全部 situation
                        yield request_or_item2 
                elif response.xpath("//div[@class='recom J_choice-content-2nd ']/a").extract().__len__() > 1:
                    #subregionList = response.xpath("//div[@class='recom J_choice-content-2nd ']/a\
                    #               /text()").extract()[1:]   # not include "全部"   
                    for subregionsel in response.xpath("//div[@class='recom J_choice-content-2nd ']/a")[1:]:  # the first matched obj is "全部"
                        subregion = subregionsel.xpath("text()").extract()[0]          # not include "全部" 
                        subregionpath = subregionsel.xpath("@href").extract()[0]
                        url = self.baseurl + subregionpath
                        yield Request(url=url,
                                    callback=self.parse_hotel_index,
                                    meta={'region':region,
                                        'subregion':subregion,
                                        'classifyx':classifyx})

                # hotel: use price to separate shops instead of subregions
                # it seems not good maybe because of price separate
                # <100: y100
                # 100<200: y200x100
                # 200<300: y300x200
                # 300<500: y500x300
                # >500: x500
                #price_separate_code = ['y100','y200x100','y300x200','y500x300','x500']
                #for price_index, price_path in enumerate(price_separate_code):
                #    #if price_index==0:         # locking just one 
                #    url = response.url+price_path
                #    yield Request(url=url,
                #                    callback =self.parse_hotel_index,
                #                    meta={'region':region,'classifyx':classifyx,'price_classify':price_path})

        elif self.is_belong_to_baby_channel(classifyx):
            if max_page_of_this_region < 50:
                for request_or_item in self.parse_baby_index(response):
                    yield request_or_item 
            else:
                sum_of_this_region = "Unknown" 
                # following codes are temporary,just tell me which classify needs especially handle
                print("We met difficult situation here, because max_page_of_this_region is above 50")
                with open('loss_statistics_for_.txt',mode='a',encoding='utf-8') as f:
                    writing_str = "{},{},{},{}'\n'".format("亲子",classifyx,region,sum_of_this_region)
                    f.write(writing_str)

                # if subregion exits, make request for every subregion and pass to parse_index
                # if subregion do not exits, parse response directly
                if response.xpath("//div[contains(@class,'tsub-list')]/ul").extract_first() is not None:
                    subregionList = response.xpath("//div[contains(@class,'tsub-list')]/ul/li/a/text()[1]").extract()
                    for subregionsel in response.xpath("//div[contains(@class,'tsub-list')]\
                                    /ul/li/a[contains(@href,'search')]"):  
                        subregion = subregionsel.re(r'title:\'(.*?)\'')[0]         # includes "不限" 
                        subregionpath = subregionsel.xpath("@href").extract()[0]
                        url = self.baseurl + subregionpath
                        yield Request(url=url,
                                    callback=self.parse_baby_index,
                                    meta={'region':region,
                                        'subregion':subregion,
                                        'subregionList':subregionList,
                                        'classifyx':classifyx})
        elif self.is_belong_to_wedding_channel(classifyx):
            if max_page_of_this_region != 50:  # including: http://www.dianping.com/wedding/travel/2
                for request_or_item in self.parse_wedding_index(response):
                    yield request_or_item 
            else:
                # following codes are temporary,just tell me which classify needs especially handle
                sum_of_this_region = "Unknown"
                print("We met difficult situation here, because max_page_of_this_region is above 50")
                with open('loss_statistics_for_.txt',mode='a',encoding='utf-8') as f:
                    writing_str = "{},{},{},{}'\n'".format("结婚",classifyx,region,sum_of_this_region)
                    f.write(writing_str)

                # if subregion exits, make request for every subregion and pass to parse_index
                # if subregion not exits, parse response directly
                if response.xpath("//li[contains(@class,'t-district')]/div/div[contains(@class,'t-list')]/ul").extract_first() is not None:
                    subregionList = response.xpath("//li[contains(@class,'t-district')]/\
                                        div/div[contains(@class,'t-list')]/ul/li/a/text()").extract()[1:]   # not include "不限"   
                    for subregionsel in response.xpath("//li[contains(@class,'t-district')]/\
                                        div/div[contains(@class,'t-list')]/ul/li/a"):  
                        subregion = subregionsel.xpath("text()").extract()[0]         # includes "不限" 
                        subregionpath = subregionsel.xpath("@href").extract()[0]
                        url = self.baseurl + subregionpath
                        yield Request(url=url,
                                    callback=self.parse_wedding_index,
                                    meta={'region':region,
                                        'subregion':subregion,
                                        'subregionList':subregionList,
                                        'classifyx':classifyx})


        elif self.is_belong_to_home_channel(classifyx):
            if max_page_of_this_region < 50:
                for request_or_item in self.parse_home_index(response):
                    #print(max_page_of_this_region)
                    yield request_or_item 
            else:
                sum_of_this_region = "unknown"
                # following codes are temporary,just tell me which classify needs especially handle
                print("We met difficult situation here, because max_page_of_this_region is above 50")
                with open('loss_statistics_for_.txt',mode='a',encoding='utf-8') as f:
                    writing_str = "{},{},{},{}'\n'".format("家装",classifyx,region,sum_of_this_region)
                    f.write(writing_str)

                # if subregion exists, make request for every subregion and pass to parse_index
                # if subregion not exits, parse response directly
                # Structure 1, for example: http://www.dianping.com/search/category/2/90/g25475r14
                if response.xpath("//ul[@class='sub-content']").extract_first() is not None:
                    subregionList = response.xpath("//ul[@class='sub-content']/li/a[contains(@href,'search')]/text()").extract()[1:]   # not include "不限"   
                    for subregionsel in response.xpath("//ul[@class='sub-content']/li/a[contains(@href,'search')]"):  
                        subregion = subregionsel.xpath("text()").extract()[0]         # includes "不限" 
                        subregionpath = subregionsel.xpath("@href").extract()[0]
                        url = self.baseurl + subregionpath
                        yield Request(url=url,
                                    callback=self.parse_home_index,
                                    meta={'region':region,
                                        'subregion':subregion,
                                        'subregionList':subregionList,
                                        'classifyx':classifyx},)
                # Structure 2, for example: http://www.dianping.com/search/category/2/90/g6826r9157 
                if response.xpath("//div/div[2]/div[@class='content']") is not None:
                    subregionList = response.xpath("//div/div[2]/div[@class='content']/ul/li/a/text()").extract() 
                    for subregionsel in response.xpath("//div/div[2]/div[@class='content']/ul/li/a[contains(@href,'search')]"):
                        subregion  = subregionsel.xpath("text()").extract()[0]
                        subregionpath = subregionsel.xpath("@href").extract()[0]
                        url = self.baseurl + subregionpath
                        yield Request(url=url,
                                    callback=self.parse_home_index,
                                    meta={'region':region,
                                        'subregion':subregion,
                                        'subregionList':subregionList,
                                        'classifyx':classifyx},)
        else:         
            if max_page_of_this_region < 50:
                for request_or_item in self.parse_index(response):
                    yield request_or_item       
            else:
                sum_of_this_region = response.xpath("//span[@class='num']/text()").re(r'[0-9]+')[0]               
                # following codes are temporary,just tell me which classify needs especially handle
                print("We met difficult situation here, because max_page_of_this_region is above 50")
                channel = response.xpath("//div[contains(@class,'bread')]/span[2]/a/span/text()").extract()[0]
                with open('loss_statistics_for_.txt',mode='a',encoding='utf-8') as f:
                    writing_str = "{},{},{},{}'\n'".format(channel,classifyx,region,sum_of_this_region)
                    f.write(writing_str)

                # if subregion exits, make request for every subregion and pass to parse_index
                # if subregion not exits, parse response directly
                if response.xpath("//div[@id='region-nav-sub']").extract_first() is not None:
                    subregionList = response.xpath("//div[@id='region-nav-sub']\
                                    /a[contains(@href,'search')]/span/text()").extract()[1:]   # not include "不限"   
                    for subregionsel in response.xpath("//div[@id='region-nav-sub']\
                                    /a[contains(@href,'search')]"):  
                        subregion = subregionsel.xpath("span/text()").extract()[0]         # includes "不限" 
                        subregionpath = subregionsel.xpath("@href").extract()[0]
                        url = self.baseurl + subregionpath
                        yield Request(url=url,
                                    callback=self.parse_index,
                                    meta={'region':region,
                                        'subregion':subregion,
                                        'subregionList':subregionList,
                                        'classifyx':classifyx})

    def parse_index(self,response):
        """parse index page
        """
        classify_or_classifysub = response.meta.get('classifyx')
        region = response.meta.get('region')
        subregion = response.meta.get('subregion',None)
        subregionList = response.meta.get('subregionList',None)

        # locking to only one page
        # linkextractor to get pages url and return request
        lx = LinkExtractor(restrict_xpaths=("//div[@class='page']",),)
        seen = set()
        links = [lnk for lnk in lx.extract_links(response)
                 if lnk not in seen]
        for link in links:
            seen.add(link)
            r = Request(url=link.url, callback=self.parse_index, 
                                    meta={'region':region,
                                'subregion':subregion,
                                'subregionList':subregionList,
                                'classifyx':classify_or_classifysub}) 
            yield r 
                
        for index, sel in enumerate(response.xpath("//div[@id='shop-all-list']/ul/li")):
            #if index == 0:    # locking only one from shop-all-list
            if not subregion:
                yield self._parse_index(response,sel,region,subregion,classify_or_classifysub)
            elif "不限" in subregion:
                if  sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/a[2]/span[@class='tag']/text()").extract()[0] not in subregionList:
                    yield self._parse_index(response,sel,region,subregion,classify_or_classifysub)
            else:
                # logging to loss_statistics_for_.txt file
                channel = response.xpath("//div[contains(@class,'bread')]/span[2]/a/span/text()").extract()[0]
                sum_of_this_subregion = response.xpath("//div[contains(@class,'bread')]/span[@class='num']/text()").re(r'[0-9]+')[0] 
                with open('loss_statistics_for_.txt',mode='a',encoding='utf-8') as f1:
                    f1.write("{},{},{},{},{}'\n'".format(channel,classify_or_classifysub,region,subregion,sum_of_this_subregion))
                yield self._parse_index(response,sel,region,subregion,classify_or_classifysub)

    def _parse_index(self,response,sel,region,subregion,classify_or_classifysub):
        """middle step for parsing index page
        """
        item = ShopItem()
        c = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tit')]/a[1]/@title").extract()  
        item['shopName'] = ''.join(c)  
        item['classifysub'] = classify_or_classifysub
        item['url'] = self.baseurl + sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tit')]/a[1]/@href").extract()[0].split("?")[0]
        item['picurl'] = sel.xpath("div[@class='pic']/a/img/@data-src").extract() if sel.xpath("div[@class='pic']/a/img/@data-src").extract() else sel.xpath("div[@class='pic']/a/img/@src").extract()
        item['overallRate'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'comment')]/span/@title").extract()
        item['commentNum'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'comment')]/a[contains(@class,'review-num')]/b/text()").extract_first(default='0')
        item['price'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'comment')]/a[contains(@class,'mean-price')]/b/text()").extract_first(default='Null') 
        item['classify'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/a[1]/span[@class='tag']/text()").extract()[0]   

        
        item['region'] = region
        # if subregion exist, use it as this format "望京(xxx)"
        # because sometimes xxx！= 望京
        item['subregion'] = subregion +"("+self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/a[2]/span[contains(@class,'tag')]/text()").extract())+")" if subregion else self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/a[2]/span[contains(@class,'tag')]/text()").extract())
        a = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/span[@class='addr']/text()").extract()
        item['addr'] = ''.join(a)
        return Request(item['url'],meta={'item':item},callback=self.parse_shop)

    def parse_hotel_index(self,response):
        """parse hotel index page"""
        region = response.meta.get('region','')
        classifyx = response.meta.get('classifyx','')
        subregion = response.meta.get('subregion',None)   #'望京' or  None
 
        # linkextractor to get pages url and return request
        lx = LinkExtractor(restrict_xpaths=("//div[@class='page']",),)
        seen = set()
        links = [lnk for lnk in lx.extract_links(response)
                 if lnk not in seen]
        for link in links:
            seen.add(link)
            r = Request(url=link.url, callback=self.parse_hotel_index, 
                                    meta={'region':region,
                                        'classifyx':classifyx,
                                        'subregion':subregion
                                        }) 
            yield r 

        # statistics for loss here
        if subregion:
            # logging to loss_statistics_for_.txt file
            sum_of_this_subregion = response.xpath("//span[@class='detail']/text()").re(r'[0-9]+')[0]
            with open('loss_statistics_for_.txt',mode='a',encoding='utf-8') as f:
                writing_str = "{},{},{},{},{}'\n'".format("酒店",classifyx,region,subregion,sum_of_this_subregion)
                f.write(writing_str)

        # the 15 index item from one page 
        for index,sel in enumerate(response.xpath("//ul[contains(@class,'hotelshop-list')]/li")):    
            #if index == 0:    # locking only one from this list
            yield self._parse_hotel_index(response,sel,region,subregion)
            
    def _parse_hotel_index(self,response,sel,region,subregion):
        """middle step for parsing hotel index page
        """
        item = ShopItem()
        s = sel.xpath("div/div/h2/a/text()").extract()
        item['shopName'] = ''.join(s)
        item['url'] = self.baseurl + sel.xpath("div/div/h2/a[1]/@href").extract()[0].split("?")[0]
        item['picurl'] = sel.xpath("div[@class='hotel-pics']/ul/li/a/img/@data-lazyload").extract()
        item['overallRate'] = sel.xpath("div/div[@class='hotel-remark']/div[@class='remark']/div/div/span/@title").extract()
        item['price'] = self.ifNotEmptyGetIndex(sel.xpath("div/div[@class='hotel-remark']/div[@class='price']/strong/text()").extract())
        item['commentNum'] = self.ifNotEmptyGetIndex(sel.xpath("div/div[@class='hotel-remark']/div[@class='remark']/div/div/a/text()").re(r'[0-9]+'))
        item['region'] = region
        #item['classify'] = response.meta['classifyx']
        item['subregion'] = subregion or "Null"
        return Request(item['url'],meta={'item':item},callback=self.parse_hotel_shop)

    def parse_baby_index(self,response):
        """parse baby index page"""

        classify_or_classifysub = response.meta.get('classifyx')
        region = response.meta.get('region',"")
        subregion = response.meta.get('subregion',"")
        subregionList = response.meta.get('subregionList',"")

        # linkextractor to get pages url and return request
        lx = LinkExtractor(restrict_xpaths=("//div[@class='Pages']",),) 
        seen = set()
        links = [lnk for lnk in lx.extract_links(response)
                 if lnk not in seen]
        for link in links:
            seen.add(link)
            r = Request(url=link.url, callback=self.parse_baby_index, 
                                    meta={'region':region,
                                        'subregion':subregion,
                                        'subregionList':subregionList,
                                        'classifyx':classify_or_classifysub}) 
            yield r 

        for index, sel in enumerate(response.xpath("//ul[contains(@class,'shop-list')]/li")):
            #if index == 0:    # locking only one from shop-all-list
            yield self._parse_baby_index(response,sel,region,subregion,classify_or_classifysub)

    def _parse_baby_index(self,response,sel,region,subregion,classify_or_classifysub):
        """middle step for parsing hotel index page
        """
        item = ShopItem()
        s = sel.xpath("div[contains(@class,'info')]/p[contains(@class,'title')]/a/@title").extract()
        item['shopName'] = ''.join(s)
        item['url'] = self.baseurl + sel.xpath("div[contains(@class,'info')]/p[contains(@class,'title')]/a/@href").extract()[0].split("?")[0]
        item['picurl'] = sel.xpath("a/img/@data-lazyload").extract() if sel.xpath("a/img/@data-lazyload").extract() else sel.xpath("a/img/@src").extract()
        item['overallRate'] = sel.xpath("div[contains(@class,'info')]/p[contains(@class,'remark')]/span[contains(@class,'item-rank-rst')]/@title").extract()
        item['commentNum'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/p[contains(@class,'remark')]/span[2]/a/text()").re(r'[0-9]+'))
        item['price'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/p[contains(@class,'average')]/span/text()").extract()) or self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/p[contains(@class,'remark')]/span/a/em/text()").extract())
            # later one is for channel-home
        item['tags'] = sel.xpath("div[contains(@class,'info')]/p[contains(@class,'key-list')]/a/text()").extract() 
        item['classify'] = classify_or_classifysub    
        item['region'] = region 
        item['subregion'] = subregion

        return Request(item['url'],meta={'item':item},callback=self.parse_baby_shop)

    def parse_wedding_index(self,response):
        """parse wedding index page"""
        
        classifyx = response.meta['classifyx']
        subregion = response.meta.get('subregion')
        
        if response.meta['classifyx']=="旅游婚纱":
            # linkextractor to get pages url and return request
            pageMax = self.get_max_page(response,"旅游婚纱")
            for pagenum in range(pageMax):
                r = Request(url="http://www.dianping.com/wedding/travel/2/p"+str(pagenum+1), callback=self.parse_wedding_index,meta={'classifyx':'旅游婚纱'}) 
                yield r 
            # every shop within one pages
            for index, sel in enumerate(response.xpath("//ul[@class='shop-item-list']/li")):
                #if index == 0:    # locking only one from this list
                yield self._parse_wedding_index(response,sel)
        
        if response.meta['classifyx']=="婚宴":
            pageMax = self.get_max_page(response,"婚宴")
            # get every pages
            for pagenum in range(pageMax):
                r = Request(url="http://www.dianping.com/wedding/hunyan?categoryIds=165&cityId=2&page="+str(pagenum+1), callback=self.parse_wedding_index,meta={'classifyx':"婚宴"}) 
                yield r 
            # every shop within one page
            for index, sel in enumerate(response.xpath("//div[contains(@class,'shop-list')]/ul/li")):
                #if index == 0:    # locking only one from this list
                yield self._parse_wedding_index(response,sel)
        else:
            for wedding_sel in self.parse_baby_index(response):   # the same as baby page
                yield wedding_sel
    def _parse_wedding_index(self,response,sel):
        """"""
        if response.meta['classifyx']=="旅游婚纱":
            item = ShopItem()  
            s = sel.xpath("div[contains(@class,'wedding-shop-name')]/h3/a/text()").extract()
            item['shopName'] = ''.join(s)
            item['price'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'price')]/h5/text()").extract())
            item['url'] = self.baseurl + sel.xpath("div[contains(@class,'wedding-shop-name')]/h3/a/@href").extract()[0].split("?")[0]
            item['picurl']=sel.xpath("div[contains(@class,'pic')]/a/img/@src").extract()
            item['overallRate'] = sel.xpath("div[contains(@class,'wedding-shop-name')]/div[contains(@class,'shop-info')]/div/span[1]/@title").extract()
            item['commentNum'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'wedding-shop-name')]/div[contains(@class,'shop-info')]/div/span[2]/a/text()").re(r'[0-9]+'))
            return Request(item['url'],meta={'item':item},callback=self.parse_baby_shop)
        elif response.meta['classifyx']=="婚宴":
            item= ShopItem()
            s = sel.xpath("a/div[2]/div[contains(@class,'tit')]/h3/@title").extract()
            item['shopName'] = ''.join(s)
            item['url']=self.baseurl+sel.xpath("a/@href").extract()[0].split("?")[0]
            item['picurl']=sel.xpath("a/div[1]/img/@src").extract()
            item['overallRate']=sel.xpath("a/div[2]/div[contains(@class,'comment-rst')]/span[1]/@title").extract()
            item['commentNum']=self.ifNotEmptyGetIndex(sel.xpath("a/div[2]/div[contains(@class,'comment-rst')]/span[2]/text()").re(r'[0-9]+'))
            return Request(item['url'],meta={'item':item},callback=self.parse_wedding_shop)


    def parse_home_index(self,response):
        """parse home index page"""  
        classify_or_classifysub = response.meta.get('classifyx')
        region = response.meta['region']
        subregion = response.meta.get('subregion',"")
        subregionList = response.meta.get('subregionList',"")

        # linkextractor to get pages url and return request
        if response.xpath("//div[@class='Pages']"):
            lx = LinkExtractor(restrict_xpaths=("//div[@class='Pages']",),)
        else:
            lx = LinkExtractor(restrict_xpaths=("//div[@class='pages']",),)
        seen = set()
        links = [lnk for lnk in lx.extract_links(response)
                 if lnk not in seen]
        for link in links:
            seen.add(link)
            r = Request(url=link.url, callback=self.parse_home_index, 
                                    meta={'region':region,
                                        'subregion':subregion,
                                        'subregionList':subregionList,
                                        'classifyx':classify_or_classifysub}) 
            yield r 
        # First html structure for example: http://www.dianping.com/search/category/2/90/g6826r14
        for index, sel in enumerate(response.xpath("//ul[contains(@class,'shop-list')]/li")):
            #if index == 0:    # locking only one from shop-all-list
            yield self._parse_baby_index(response,sel,region,subregion,classify_or_classifysub)
        # Second html structure for example: http://www.dianping.com/search/category/2/90/g25475r14
        for index2, sel2 in enumerate(response.xpath("//div[@class='shop-list']/div")):
            if index2!=0:
                yield self._parse_home_index(response,sel2,region,subregion,classify_or_classifysub)

    def _parse_home_index(self,response,sel,region,subregion,classify_or_classifysub):
        """Write different logics for different html strucures"""
        item = ShopItem()   
        s = sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/h3/a/text()").extract()
        item['shopName'] = ''.join(s)
        item['url'] = self.baseurl + sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/h3/a/@href").extract()[0].split("?")[0]
        item['picurl'] = sel.xpath("a/img/@data-src").extract() if sel.xpath("a/img/@data-src").extract() else sel.xpath("a/img/@src").extract()
        item['overallRate'] = sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/span[contains(@class,'item-rank-rst')]/text()").extract()  
        item['commentNum'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/a/text()").re(r'[0-9]+'))
        item['price'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/span[@class='avg-price']/a/text()").re(r'[0-9]+')) or "Null"
        item['classify'] = classify_or_classifysub    
        item['region'] = region 
        item['subregion'] = subregion
        # has rating values in this channel
        item['first_rating'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/div[contains(@class,'shop-score')]/a[1]/text()").extract())+self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/div[contains(@class,'shop-score')]/a[1]/i/text()").extract())
        item['second_rating'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/div[contains(@class,'shop-score')]/a[2]/text()").extract())+self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/div[contains(@class,'shop-score')]/a[2]/i/text()").extract())
        item['third_rating'] = self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/div[contains(@class,'shop-score')]/a[3]/text()").extract())+self.ifNotEmptyGetIndex(sel.xpath("div[contains(@class,'info')]/div[1]/div[contains(@class,'shop-title')]/following-sibling::div[1]/div[contains(@class,'shop-score')]/a[3]/i/text()").extract())

        return Request(item['url'],meta={'item':item},callback=self.parse_home_shop)

    def parse_hall_index(self,response):
        """parse hall index page"""
        # linkextractor to get pages url and return request
        pageMax = self.get_max_page(response,response.meta.get('classifyx'))
        for pagenum in range(pageMax):
            r = Request(url="http://www.dianping.com/search/category/2/40?pageNo="+str(pagenum+1), callback=self.parse_hall_index) 
            yield r 

        for index, sel in enumerate(response.xpath("//div[@class='shop-list']/div")):
            #if index == 0:    # locking only one from this list
            yield self._parse_hall_index(response,sel)

    def _parse_hall_index(self,response,sel):
        """middle step for parsing hotel index page
        """
        item = ShopItem()
        #item['classify'] = response.meta['classifyx']
        s = sel.xpath("a/div[2]/div[contains(@class,'shop-title')]/span[1]/text()").extract()
        item['shopName'] = ''.join(s)
        item['url'] = self.baseurl + self.ifNotEmptyGetIndex(sel.xpath("a[1]/@href").extract()).split("?")[0]
        item['picurl'] = sel.xpath("a[1]/div[1]/img/@src").extract()
        #item['region'] = response.meta['region']
        a = sel.xpath("a/div[2]/div[contains(@class,'round-box')]/div/span[2]/text()").extract()
        item['addr'] = ''.join(a)
        item['tags'] = sel.xpath("a/div[2]/div[contains(@class,'shop-title')]/span[1]/following-sibling::span").extract()
        return Request(item['url'],meta={'item':item},callback=self.parse_hall_shop)

    def parse_shop(self,response):
        """parse detailed info of every shop
        """
        item = response.meta['item']
        # navigation and channel info
        item = self.navigation_helper(response,item) 
        item = self._mapchannel(response,item) 
        # branchs
        item = self.get_branches(response,item) 
        # poi
        item = self._poi_maptype_and_traffic(response,item)
        #recommend
        item = self._get_recommend(response,item)
        return item

    def parse_wedding_shop(self,response):
        """parse detailed info of every baby shop
        """
        item = self.parse_shop(response)
        item['addr'] = response.xpath("//div/span[@class='info-name']/@title").extract() if not item.get('addr','') else item['addr']  
        item['phone'] = response.xpath("//p/span[@class='info-name']/following-sibling::node()[2]/text()").extract()
        item['info'] = response.xpath("//div[@class='txt-c']/text()").extract()
        item['price'] = "Null"
        
        return item

    def parse_hotel_shop(self,response):
        """parse detailed info of every hotel shop
        """
        item = self.parse_shop(response)
        item['classify'] = item['navigation'][-1]
        a = self.ifNotEmptyGetIndex(response.xpath("//p[@class='shop-address']/text()").extract())
        item['addr'] = ''.join(a)
        return item

    def parse_baby_shop(self,response):
        """parse detailed info of every baby shop
        """
        item = self.parse_shop(response)
        item['addr'] = response.xpath("//div[contains(@class,'shop-addr')]/span/text()").extract() or response.xpath("//span[contains(@class,'road-addr')]/text()").extract() if not item.get('addr','') else item['addr']  # the later one is for wedding page which has the same page as baby page
        
        return item

    def parse_home_shop(self,response):
        item = self.parse_shop(response)

        return item

    def parse_hall_shop(self,response):
        """parse detailed info of every hall shop
        """
        item = self.parse_shop(response)
        item['overallRate'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'merchant-review')]/span/@title").extract())
        item['price'] = "Null"
        return item

    def navigation_helper(self,response,item):
        """handle some difference between navigations
        """

        if response.xpath("//div[@class='breadcrumb']/a/text()").extract():
            item['navigation'] = response.xpath("//div[@class='breadcrumb']/a/text()").extract()
        elif response.xpath("//div[@class='breadcrumb']/div/a/text()").extract():
            item['navigation'] = response.xpath("//div[@class='breadcrumb']/div/a/text()").extract()
        elif response.xpath("//div[@class='breadcrumb']/b/a/span/text()").extract():
            item['navigation'] = response.xpath("//div[@class='breadcrumb']/b/a/span/text()").extract()
        elif response.xpath("//ul[contains(@class,'crumbs-list')]/li/a/span/text()").extract():
            item['navigation'] = response.xpath("//ul[contains(@class,'crumbs-list')]/li/a/span/text()").extract()
        elif response.xpath("//div[@class='breadcrumb-wrapper']/ul/li/a/text()").extract():
            item['navigation'] = response.xpath("//div[@class='breadcrumb-wrapper']/ul/li/a/text()").extract()
        elif response.xpath("//div[@class='bread J_bread']"):
            firstkey = response.xpath("//div[@class='bread J_bread']/a/span/text()").extract()[0]
            keys = response.xpath("//div[@class='bread J_bread']/span[@class='detail']/a/text()").extract()
            x = [i for i in keys if '\n' not in i]
            x = x.insert(0,firstkey)
            item['navigation'] = x

        # handle some strange situation happended in "延庆县"
        if item.get('navigation')[0].strip().startswith('县'):
            item['channel']=item.get('navigation')[0].strip()[1:]
        else:
            item['channel'] = item.get('navigation')[0].strip() 
        return item

    def get_branches(self,response,item):
        """branch information
        """
        if response.xpath("//div[contains(@class,'shop-branchs')]/a[@class='more-shop']/text()").extract():
            branch_included_string = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'shop-branchs')]/a[@class='more-shop']/text()").extract())
        elif response.xpath("//*[@class='shop-title']/following-sibling::node()[2]/text()").extract():
            branch_included_string = self.ifNotEmptyGetIndex(response.xpath("//*[@class='shop-title']/following-sibling::node()[2]/text()").extract())
        elif response.xpath("//a[contains(@class,'js-other-merchant other-merchant-btn')]/text()").extract():
            branch_included_string = self.ifNotEmptyGetIndex(response.xpath("//a[contains(@class,'js-other-merchant other-merchant-btn')]/text()").extract())
        elif response.xpath("//*[@class='shop-title']/following-sibling::node()[1]/a/text()").extract():
            branch_included_string = self.ifNotEmptyGetIndex(response.xpath("//*[@class='shop-title']/following-sibling::node()[1]/a/text()").extract())
        else:
            branch_included_string = ""

        # extract number from string 
        try:
            item['branch'] = re.search(r'[0-9]+',branch_included_string).group(0)
        except AttributeError:
            item['branch'] = '0'
        return item

    def get_3rate(self,response,item,flag):
        """get first,second,third rating info
        """
        if flag == "most":
            if response.xpath("//div[contains(@class,'brief-info')]/span/text()").__len__()>3:
            #sel_basic_info = response.xpath("//div[@id='basic-info']")
                item['first_rating'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'brief-info')]/span[last()-2]/text()").extract())
                item['second_rating'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'brief-info')]/span[last()-1]/text()").extract())
                item['third_rating'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'brief-info')]/span[last()]/text()").extract())
        if flag == "study":
            item['first_rating'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'brief-info')]/div[contains(@class,'rank')]/span[last()-2]/text()").extract())
            item['second_rating'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'brief-info')]/div[contains(@class,'rank')]/span[last()-1]/text()").extract())
            item['third_rating'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'brief-info')]/div[contains(@class,'rank')]/span[last()]/text()").extract())

        return item

    def get_phone(self,response,item,flag):
        """get phone info
        """
        if flag == "most":
            item['phone'] = response.xpath("//div[@id='basic-info']/p[contains(@class,'tel')]/span[2]/text()").extract()
        elif flag =="study":
            item['phone'] = response.xpath("//*[@class='phone']/span[contains(@class,'item')]/text()").extract()
        elif flag == "hotel":
            item['phone'] = response.xpath("//div[contains(@class,'nobusiness-action')]/p[3]/em/text()").extract() or response.xpath("//*[@id='hotel-intro']/div[1]/p/span/text()").re(r'电话:(.+)')
        elif flag == "baby":
            item['phone'] = response.xpath("//div[contains(@class,'shopinfor')]/p/span[1]/text()").extract() or response.xpath("//div[@class='shop-contact']/span[1]/text()").extract() if not item.get('phone','') else item['phone']
        elif flag == "hall":
            item['phone'] = response.xpath("//span[contains(@class,'hightlight')]/text()").extract()
        return item

    def get_reservationNum(self,response,item):
        """particular for study channel"""
        item['reservationNum'] = self.ifNotEmptyGetIndex(response.xpath("//div[@class='book']/span[@class='num']/text()").extract())
        return item

    def get_star(self,response,item,flag):
        """get star 5,4,3,2,1 info 
        """
        if flag == "most":
            item['star5'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'shop-score')]/ul[contains(@class,'stars')]/li[1]/text()[3]").extract())
            item['star4'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'shop-score')]/ul[contains(@class,'stars')]/li[2]/text()[3]").extract())
            item['star3'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'shop-score')]/ul[contains(@class,'stars')]/li[3]/text()[3]").extract())
            item['star2'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'shop-score')]/ul[contains(@class,'stars')]/li[4]/text()[3]").extract())
            item['star1'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'shop-score')]/ul[contains(@class,'stars')]/li[5]/text()[3]").extract())
        elif flag == "hotel":
            item['star5'] = self.ifNotEmptyGetIndex(response.xpath("//div[@id='comment']/h2/span/a[contains(@data-value,'5star')]/span/text()").re(r'[0-9]+'))      # elimanite ()
            item['star4'] = self.ifNotEmptyGetIndex(response.xpath("//div[@id='comment']/h2/span/a[contains(@data-value,'4star')]/span/text()").re(r'[0-9]+'))  
            item['star3'] = self.ifNotEmptyGetIndex(response.xpath("//div[@id='comment']/h2/span/a[contains(@data-value,'3star')]/span/text()").re(r'[0-9]+'))  
            item['star2'] = self.ifNotEmptyGetIndex(response.xpath("//div[@id='comment']/h2/span/a[contains(@data-value,'2star')]/span/text()").re(r'[0-9]+'))  
            item['star1'] = self.ifNotEmptyGetIndex(response.xpath("//div[@id='comment']/h2/span/a[contains(@data-value,'1star')]/span/text()").re(r'[0-9]+'))  
        elif flag == "baby" or flag == "study":
            # the first structure for example: http://www.dianping.com/shop/5361706
            item['star5'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'comment-star')]/dl/dd/a[contains(@data-order,'5star')]/following-sibling::node()/following-sibling::node()/text()").re(r'[0-9]+')) 
            item['star4'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'comment-star')]/dl/dd/a[contains(@data-order,'4star')]/following-sibling::node()/following-sibling::node()/text()").re(r'[0-9]+')) 
            item['star3'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'comment-star')]/dl/dd/a[contains(@data-order,'3star')]/following-sibling::node()/following-sibling::node()/text()").re(r'[0-9]+')) 
            item['star2'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'comment-star')]/dl/dd/a[contains(@data-order,'2star')]/following-sibling::node()/following-sibling::node()/text()").re(r'[0-9]+')) 
            item['star1'] = self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'comment-star')]/dl/dd/a[contains(@data-order,'1star')]/following-sibling::node()/following-sibling::node()/text()").re(r'[0-9]+'))
            # the second structure for example: http://www.dianping.com/shop/50600655
            item['star5'] = self.ifNotEmptyGetIndex(response.xpath("//ul[@class='status-list']/li[1]/a/text()").re(r'[0-9]+'))  if not item.get('star5','') else item['star5'] 
            item['star4'] = self.ifNotEmptyGetIndex(response.xpath("//ul[@class='status-list']/li[2]/a/text()").re(r'[0-9]+'))  if not item.get('star4','') else item['star4'] 
            item['star3'] = self.ifNotEmptyGetIndex(response.xpath("//ul[@class='status-list']/li[3]/a/text()").re(r'[0-9]+'))  if not item.get('star3','') else item['star3'] 
            item['star2'] = self.ifNotEmptyGetIndex(response.xpath("//ul[@class='status-list']/li[4]/a/text()").re(r'[0-9]+'))  if not item.get('star2','') else item['star2'] 
            item['star1'] = self.ifNotEmptyGetIndex(response.xpath("//ul[@class='status-list']/li[5]/a/text()").re(r'[0-9]+'))  if not item.get('star1','') else item['star1'] 

        elif flag =="hall":
            item['star5'] = self.ifNotEmptyGetIndex(response.xpath("//li[contains(@data-name,'default')]/@data-5star").extract())
            item['star4'] = self.ifNotEmptyGetIndex(response.xpath("//li[contains(@data-name,'default')]/@data-4star").extract())
            item['star3'] = self.ifNotEmptyGetIndex(response.xpath("//li[contains(@data-name,'default')]/@data-3star").extract())
            item['star2'] = self.ifNotEmptyGetIndex(response.xpath("//li[contains(@data-name,'default')]/@data-2star").extract())
            item['star1'] = self.ifNotEmptyGetIndex(response.xpath("//li[contains(@data-name,'default')]/@data-1star").extract())
            item['commentNum'] = self.ifNotEmptyGetIndex(response.xpath("//li[contains(@data-name,'default')]/@data-all").extract())

        return item

    def _poi_maptype_and_traffic(self,response,item):
        """ poi related info
        """
        # poi 
        # include_str = response.xpath("(//*[@id='top']/script)[last()]").extract()[0]
        # include_str = self.ifNotEmptyGetIndex([sc for sc in response.xpath("//body/script").extract() if 'entry' in sc])
        item['city_pinyin'] = self._city_pingyin
        try:
            include_str = response.xpath("//body/script[last()]").extract()[0]   
            try:
                pattern = r'poi: "(.+)"'
                poi = re.search(pattern,include_str).group(1)
            except AttributeError:
                pattern = r"poi: '(.+)'"
                poi = re.search(pattern,include_str).group(1)

            if poi:
                poi_dict = decode(poi)
                item['poi'] = poi
                item['original_latitude'] = str(poi_dict['lat'])
                item['original_longitude'] = str(poi_dict['lng']) 
            else:
                item['poi'] = 'Null'
                item['original_latitude'] = '0'
                item['original_longitude'] = '0'            
            # poi_dict = decode(poi)
            # item['poi'] = poi 
            # item['original_latitude'] = str(poi_dict['lat'])
            # item['original_longitude'] = str(poi_dict['lng'])

            # map type and traffic
            pattern2 = r'mapType: "(.+)",'
            pattern3 = r'traffic: "(.+)",'

            # important: convert escaped character
            item['map_type'] = self.restore_escape_character(re.search(pattern2,include_str).group(1)) if re.search(pattern2,include_str) else "Null"
            if not item.get('traffic',''):
                if re.search(pattern3,include_str):
                    item['traffic'] = self.restore_escape_character(re.search(pattern3,include_str).group(1))   
                else: 
                    item['traffic'] = "Null"   
        except:
            # if something happens when used part of response, we instead use the whole response body
            large_string = response.body.decode()
            try:
                pattern = r'poi: "(.+)"'
                poi = re.search(pattern,large_string).group(1)
            except AttributeError:
                pattern = r"poi: '(.+)'"
                poi = re.search(pattern,large_string).group(1)

            if poi:
                poi_dict = decode(poi)
                item['poi'] = poi
                item['original_latitude'] = str(poi_dict['lat'])
                item['original_longitude'] = str(poi_dict['lng']) 
            else:
                item['poi'] = 'Null'
                item['original_latitude'] = '0'
                item['original_longitude'] = '0'
            # poi_dict = decode(poi)
            # item['poi'] = poi 
            # item['original_latitude'] = str(poi_dict['lat'])
            # item['original_longitude'] = str(poi_dict['lng'])

            item['map_type'] = self.restore_escape_character(re.search(r'mapType: "(.+)",',large_string).group(1)) if re.search(r'mapType: "(.+)",',large_string) else "Null"
            if not item.get('traffic',''):
                if re.search(r'traffic: "(.+)",',large_string):
                    item['traffic'] = self.restore_escape_character(re.search(r'traffic: "(.+)",',large_string).group(1))  
                else:
                    item['traffic'] = "Null" 
        finally:   # some shop does not have poi info
            return item

    def _get_recommend(self,response,item):
        """Recommend info is located in script tag
        """
        # method1 bs4
        recommendmaybe = self.ifNotEmptyGetIndex(response.xpath("//div[@id='shop-tabs']/script").extract())

        if "recommend-name" in recommendmaybe:
            recommendList=[]
            temp = BeautifulSoup(recommendmaybe,'lxml')  
            inside_string = temp.script.text   # get rid of the outside script tag 
            inside_tag = BeautifulSoup(inside_string,'lxml')
            for i in inside_tag.html.body.div.p.find_all('a'):
                recommendList.append(i['title'])
            item['recommend'] = recommendList
        return item

        #method 2: xml-failed for bad html structure
#        recommendmaybe = self.ifNotEmptyGetIndex(response.xpath("//div[@id='shop-tabs']/script").extract())
#        recommendStr = None if "recommend-name" not in recommendmaybe else recommendmaybe
#        if recommendStr:
#            recommendList=[]
#            root = ET.fromstring(recommendStr)
#            tag_p = root[0][0]
#            for a in tag_p:
#                recommendList.append(a.attrib['title'])
#            item['recommend'] = recommendList
#        return item

        #method 3: regular expression-not efficiecnt
#        if recommendStr:
#            pattern = r'dish.+title="(.+)"'  
#            recommendList = re.findall(pattern,recommendStr)
#            item['recommend'] = recommendList
#        return item


    def get_other_info(self,response,item,flag):
        """ Some of these items do not get values so i need to set a dafault for them
        """
        if flag == "most":
            for index, details in enumerate(response.xpath("//div[@id='basic-info']/div[contains(@class,'other')]/p")):
                titleDetails = details.xpath("span[contains(@class,'info-name')]/text()").extract()
                if(titleDetails):
                    item = self._mapDetails(response,item,self.ifNotEmptyGetIndex(titleDetails),index,flag)
        if flag == "study":
            for index, details in enumerate(response.xpath("//div[contains(@class,'shop-info')]/ul/li")):
                titleDetails = details.xpath("span[contains(@class,'title')]/text()").extract()
                if(titleDetails):
                    item = self._mapDetails(response,item,self.ifNotEmptyGetIndex(titleDetails),index,flag)
        if flag == "hotel":
            y = self.ifNotEmptyGetIndex(response.xpath("//p[contains(@class,'J_hotel-description')]/text()").extract())
            y = ''.join(y)
            if y.strip():
                item['info'] = self.ifNotEmptyGetIndex(response.xpath("//p[contains(@class,'J_hotel-description')]/text()").extract())
            else:
                item['info'] = 'nosomething'
            item['tags']=response.xpath("//p[contains(@class,'J_shop-tags')]/a/text()").extract()
        if flag == "baby":
            y = response.xpath("//div[contains(@class,'con J_showWarp')]/div[contains(@class,'block_all')]/div[contains(@class,'block_right')]/span/text()").extract()
            y = ''.join(y)
            if y.strip():
                item['info'] = response.xpath("//div[contains(@class,'con J_showWarp')]/div[contains(@class,'block_all')]/div[contains(@class,'block_right')]/span/text()").extract()
            else:
                item['info'] = 'nosomething'

            # first structure for example: http://www.dianping.com/shop/5361706
            for index,details in enumerate(response.xpath("//div[contains(@class,'con J_showWarp')]/table/tbody/tr")):
                titleDetails = details.xpath("td/div[1]/text()").extract()
                if(titleDetails):
                    item = self._mapDetails(response,item,self.ifNotEmptyGetIndex(titleDetails),index,flag)

            # second structure for example: http://www.dianping.com/shop/26964050
            for index2,details2 in enumerate(response.xpath("//div[contains(@class,'shop-info-inner')]/div[contains(@class,'desc-list')]/dl")):
                titleDetails2 = details2.xpath("dt/text()").extract()
                if(titleDetails2):
                    item = self._mapDetails(response,item,self.ifNotEmptyGetIndex(titleDetails2),index2,flag)
            for index3, details3 in enumerate(response.xpath("//div[contains(@class,'shop-detail-info')]/div[contains(@class,'desc-list')]/dl")):
                titleDetails3 = details3.xpath("dt/text()").extract()
                if(titleDetails3):
                    item = self._mapDetails(response,item,self.ifNotEmptyGetIndex(titleDetails3),index3,flag)
        if flag =="hall":
            y = response.xpath("//div[contains(@class,'intro-text')]/text()").extract()
            y = ''.join(y)
            if y.strip():
                item['info'] = response.xpath("//div[contains(@class,'intro-text')]/text()").extract()
            else:
                item['info'] = 'nosomething'
            item['special'] = response.xpath("//ul[contains(@class,'field-features-list')]/li/text()").extract()
        return item

    def get_nearby_info(self,response,item,flag):
        """ Get nearby shops and nearby group info
        """
        if flag == "most":
            item['nearby_group'] = response.xpath("//*[@id='around-info']/div[1]/ul/li/a[@class='title']/@title").extract()
            item['nearby_shops'] = response.xpath("//*[@id='around-info']/div[2]/ul/li/a[@class='title']/@title").extract()
        elif flag == "hotel":
            item['nearby_shops'] = response.xpath("//div[contains(@class,'hotel-nearby-blk J_panel')][1]/ul/li/div[2]/h4/a/@title").extract()
        elif flag == "study":
            item['nearby_group'] = response.xpath("//div[contains(@class,'tuan')]/div[contains(@class,'con')]/a/p[contains(@class,'title')]/text()").extract()
        elif flag == "baby":
            item['nearby_shops'] = response.xpath("//div[contains(@class,'nearby-shop')]/ul/li/h4/a/text()").extract() if not item.get('nearby_shops','') else item['nearby_shops']
        return item

    def _mapDetails(self,response,item,titleDetails,index,flag):
        """ This method looks at each item from the other info paragraph, 
            and figures out what text goes with item, seems thre are no clear ways of doing it otherwise
        """
        index +=1
        if(titleDetails):
            if flag=="most":
                if("别" and "名" in titleDetails):
                    item['alias'] = response.xpath("//div[@id='basic-info']/div[contains(@class,'other')]/p["+str(index)+"]/span[2]/text()").extract()
                if("营业时间" in titleDetails):
                    x = response.xpath("//div[@id='basic-info']/div[contains(@class,'other')]/p["+str(index)+"]/span[2]/text()").extract()
                    x = ''.join(x)
                    if x.strip():
                        item['hour'] = response.xpath("//div[@id='basic-info']/div[contains(@class,'other')]/p["+str(index)+"]/span[2]/text()").extract()
                    else:
                        item['hour'] = 'notime'
                if("分类标签" in titleDetails):
                    item['tags'] = response.xpath("//div[@id='basic-info']/div[contains(@class,'other')]/p["+str(index)+"]/span[@class='item']/a/text()").extract()
                if("简介" in titleDetails):
                    y = response.xpath("//div[@id='basic-info']/div[contains(@class,'other')]/p["+str(index)+"]/text()").extract()
                    y = ''.join(y)
                    if y.strip():
                        item['info'] = response.xpath("//div[@id='basic-info']/div[contains(@class,'other')]/p["+str(index)+"]/text()").extract() 
                    else:
                        item['info'] = 'nosomething'
            if flag=="study":
                if ("创立时间" in titleDetails):
                    item['start'] = response.xpath("//div[contains(@class,'shop-info')]/ul/li["+str(index)+"]/text()[2]").extract()
                if("商户介绍" in titleDetails):
                    if response.xpath("//div[contains(@class,'shop-info')]/ul/li["+str(index)+"]/text()[2]").extract() or 'nosomething':
                        item['info'] = response.xpath("//div[contains(@class,'shop-info')]/ul/li["+str(index)+"]/text()[2]").extract()
                    else:
                        item['info'] = 'nosomething'
                if("营业时间" in titleDetails):
                    x = response.xpath("//div[contains(@class,'shop-info')]/ul/li["+str(index)+"]/text()[2]").extract()
                    x = ''.join(x)
                    if x.strip():
                        item['hour'] = response.xpath("//div[contains(@class,'shop-info')]/ul/li["+str(index)+"]/text()[2]").extract() 
                    else:
                        item['hour'] = 'notime'
                if("特色服务" in titleDetails):
                    item['special'] = response.xpath("//div[contains(@class,'shop-info')]/ul/li["+str(index)+"]/span").extract()
            if flag=="baby":
                if ("创立时间" in titleDetails):
                    item['start'] = response.xpath("//div[contains(@class,'con J_showWarp')]/table/tbody/tr["+str(index)+"]/td/div[2]/text()").extract()
                if ("商户介绍" in titleDetails):
                    item['info'] = response.xpath("//div[contains(@class,'con J_showWarp')]/table/tbody/tr["+str(index)+"]/td/div[2]/text()").extract() if not item.get('info','') else item['info']
                if ("营业时间" in titleDetails):
                    x = response.xpath("//div[contains(@class,'con J_showWarp')]/table/tbody/tr["+str(index)+"]/td/div[2]/text()").extract() or response.xpath("//div[contains(@class,'shop-detail-info')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/span[1]/text()").extract()
                    x = ''.join(x)
                    if x.strip():
                        item['hour'] = response.xpath("//div[contains(@class,'con J_showWarp')]/table/tbody/tr["+str(index)+"]/td/div[2]/text()").extract() or response.xpath("//div[contains(@class,'shop-detail-info')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/span[1]/text()").extract()
                    else:
                        item['hour'] = 'notime'
                if ("特色" in titleDetails):
                    item['special'] = response.xpath("//div[contains(@class,'con J_showWarp')]/table/tbody/tr["+str(index)+"]/td/div[2]/text()").extract() or response.xpath("//div[contains(@class,'con J_showWarp')]/table/tbody/tr["+str(index)+"]/td/div[1]/ul/li/text()").extract()
                if ("地址" in titleDetails):
                    item['addr'] = response.xpath("//div[contains(@class,'shop-info-inner')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/span[1]/text()").extract() if not item.get('addr','') else item['addr']
                if ("电话" in titleDetails):
                    item['phone'] = response.xpath("//div[contains(@class,'shop-info-inner')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/strong/text()").extract() if not item.get('phone','') else item['phone']
                if ("标签" in titleDetails):
                    item['tags'] =  response.xpath("//div[contains(@class,'shop-info-inner')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/span/a/text()").extract() if not item.get('tags','') else item['tags']
                if ("公交信息" in titleDetails):
                    item['traffic'] = response.xpath("//div[contains(@class,'shop-detail-info')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/span[1]/text()").extract()
                    #print(item['traffic']) 
                if ("商户描述" in titleDetails):
                    y = response.xpath("//div[contains(@class,'shop-detail-info')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/span[1]/text()").extract()
                    y = ''.join(y)
                    if y.strip():
                        item['info'] = response.xpath("//div[contains(@class,'shop-detail-info')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/span[1]/text()").extract()
                    else:
                        item['info'] = 'nowhere'
                if ("别名" in titleDetails):
                    item['alias'] = response.xpath("//div[contains(@class,'shop-detail-info')]/div[contains(@class,'desc-list')]/dl["+str(index)+"]/dd/span[1]/text()").extract()


        return item

    def _mapchannel(self,response,item):
        """This method looks at each channel and choose seperate parse rule"""
        thischannel = item['channel'][2:]
        #print(thischannel)
        if thischannel:
            if(thischannel in ["学习培训"]):
                flag="study"
                item = self.get_reservationNum(response,item)
            elif(thischannel in ["酒店"]):
                flag = "hotel"
            elif(thischannel in ["亲子","结婚","家装"]):
                flag ="baby"
            elif(thischannel in ["宴会"]):
                flag = "hall"
            else:
                flag = "most"           # "餐厅","电影","休闲娱乐","丽人","k歌","K歌",
                                        #  "运动健身","周边游","购物","宠物",
                                        # "生活服务","爱车","医疗健康" 餐厅=美食
            # different setup
            # 3 rating
            item = self.get_3rate(response,item,flag)
            # mapping other infomation
            item = self.get_other_info(response,item,flag)
            # phone
            item = self.get_phone(response,item,flag)
            # stars
            item = self.get_star(response,item,flag)
            # nearby_shop and group
            item = self.get_nearby_info(response,item,flag)
        return item

    def ifNotEmptyGetIndex(self,somelist,index=0):
        """check to see it's not empty"""
        if somelist: 
            return somelist[index]
        else:
            return somelist
       
    def get_max_page(self,response,classifyx):
        """get max page number of the certain index response page """

        # if max page number is below 50, that means we can get all the company url from index page, 
        # this is what we expect, at this time, we would ignore subregion setup
        # raw max_page_of_this_region is either a str number like '8' or empty str ""

        if self.is_belong_to_hotel_channel(classifyx):
            max_page_of_this_region = self.ifNotEmptyGetIndex(
                            response.xpath("//div[@class='page']/a[contains(@class,'PageLink')]/text()").extract())
        elif self.is_belong_to_baby_channel(classifyx) or \
                self.is_belong_to_wedding_channel(classifyx) or \
                self.is_belong_to_home_channel(classifyx):
            max_page_of_this_region = self.ifNotEmptyGetIndex(
                            response.xpath("//a[contains(@class,'PageLink')]/text()").extract(),index=-1) or \
                                    self.ifNotEmptyGetIndex(
                            response.xpath("//a[contains(@class,'pageLink')]/text()").extract(),index=-1)

        elif self.is_belong_to_hall_channel(classifyx):
            if response.xpath("//a[contains(@class,'pages-link')]/text()").extract().__len__()==1:
                max_page_of_this_region = self.ifNotEmptyGetIndex(
                            response.xpath("//a[contains(@class,'pages-link')]/text()").extract(),index=-1)
            elif response.xpath("//a[contains(@class,'pages-link')]/text()").extract().__len__()>=2:
                max_page_of_this_region = self.ifNotEmptyGetIndex(
                            response.xpath("//a[contains(@class,'pages-link')]/text()").extract(),index=-2)
            elif response.xpath("//a[contains(@class,'pages-link')]/text()").extract().__len__()==0:
                 max_page_of_this_region = 1
        elif self.is_belong_to_home_channel(classifyx):
            max_page_of_this_region = self.ifNotEmptyGetIndex(
                            response.xpath("//div[@class='pages']/a[contains(@class,'pageLink')]/text()").extract(),index=-1)
        elif self.is_belong_to_wedding_channel(classifyx):
            max_page_of_this_region = self.ifNotEmptyGetIndex(
                            response.xpath("//div[@class='Pages']/a[contains(@class,'PageLink')]/text()").extract(), index=-1)
        else:  
            max_page_of_this_region = self.ifNotEmptyGetIndex(
                            response.xpath("//div[@class='page']/a[contains(@class,'PageLink')]/text()").extract(),index=-1)
        #print(max_page_of_this_region)

        return int(max_page_of_this_region) if max_page_of_this_region else 1

    def is_belong_to_hotel_channel(self,classify):
        """look up classifyid of hotel channel, return true if this classify belongs to the channel
        """
        classify_code_list = [i[1] for i in Classify()[('hotel',60,'酒店')]]
        return classify in classify_code_list

    def is_belong_to_baby_channel(self,classify):
        """look up classifyid of baby channel, return true if this classify belongs to the channel
        """
        classify_code_list = [i[1] for i in Classify()[('baby',70,'亲子')]]
        return classify in classify_code_list

    def is_belong_to_wedding_channel(self,classify):
        """look up classifyid of wedding channel, return true if this classify belongs to the channel
        """
        classify_code_list = [i[1] for i in Classify()[('wedding',55,'结婚')]]
        return classify in classify_code_list

    def is_belong_to_home_channel(self,classify):
        """look up classifyid of wedding channel, return true if this classify belongs to the channel
        """
        classify_code_list = [i[1] for i in Classify()[('home',90,'家装')]]
        return classify in classify_code_list

    def is_belong_to_hall_channel(self,classify):
        """look up classifyid of wedding channel, return true if this classify belongs to the channel
        """
        
        return classify=="宴会全部"


    @staticmethod
    def restore_escape_character(x):
        return codecs.getdecoder("unicode_escape")(x)[0]



class DianpingSupplement(Dianping):
    """This is supplement of dianping spider particular for the index pages
        extract more shops from index 50 pages, this problem url has to be given named "problem_index_xxx.txt"
    """
    name = "dianpingsupplement"
    problem_index_list=[]     # the index page for certain classify

    def read_problem_index(self):
        with open("problem_index_page_beauty.txt",encoding='utf-8') as f:
            for line in f:
                self.problem_index_list.append(line.strip("\n"))

    def start_requests(self):
        self.read_problem_index()  
        for index_info in self.problem_index_list:
            index_page = index_info.split(',')
            yield Request(url=index_page[0],
                        callback=self.parse_index,
                        meta={'region':index_page[2],
                            'classifyx':index_page[1]}) 

    def parse_index(self,response):
        """parse index page"""
        classify_or_classifysub = response.meta.get('classifyx')
        region = response.meta['region']

        lx = LinkExtractor(restrict_xpaths=("//div[@class='page']",),)
        seen = set()
        links = [lnk for lnk in lx.extract_links(response)
                 if lnk not in seen]
        for link in links:
            seen.add(link)
            r = Request(url=link.url,callback=self.parse_index, 
                                    meta={'region':region,
                                        'classifyx':classify_or_classifysub}) 
            yield r 
                
        for index, sel in enumerate(response.xpath("//div[@id='shop-all-list']/ul/li")):
            shop_url = self.baseurl + sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tit')]/a[1]/@href").extract()[0]
            if not self.is_in_database_named_beauty(shop_url):
                print("Gotta one!!")
                yield self._parse_index(response=response,sel=sel,region=region,subregion=None,classify_or_classifysub=classify_or_classifysub)

    def is_in_database_named_beauty(self,url):
        """check if this url is in DB
            Attation: the table name should been changed per. need
        """
        row = cur1.execute("SELECT * FROM `shops-beauty` WHERE `url`=%s", url)
        return row  # 1 stands for true



class DianpingSupplement2(Dianping):
    """add function of checking db for every shop item 
    """
    name = "dianpingsupplement2"

    def _parse_index(self,response,sel,region,subregion,classify_or_classifysub):
        """middle step for parsing index page
        """
        url = self.baseurl + sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tit')]/a[1]/@href").extract()[0]
        if not self.is_in_database(url):
            item = ShopItem()
            item['shopName'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tit')]/a[1]/@title").extract()  
            item['classifysub'] = classify_or_classifysub
            item['url'] = self.baseurl + sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tit')]/a[1]/@href").extract()[0].split("?")[0]
            item['picurl'] = sel.xpath("div[@class='pic']/a/img/@data-src").extract() if sel.xpath("div[@class='pic']/a/img/@data-src").extract() else sel.xpath("div[@class='pic']/a/img/@src").extract()
            item['overallRate'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'comment')]/span/@title").extract()
            item['commentNum'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'comment')]/a[contains(@class,'review-num')]/b/text()").extract_first(default='0')
            item['price'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'comment')]/a[contains(@class,'mean-price')]/b/text()").extract_first(default='Null') 
            item['classify'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/a[1]/span[@class='tag']/text()").extract()[0]   

            
            item['region'] = region
            # if subregion exist, use it as this format "望京(xxx)"
            # because sometimes xxx！= 望京
            item['subregion'] = subregion +"("+self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/a[2]/span[contains(@class,'tag')]/text()").extract())+")" if subregion else self.ifNotEmptyGetIndex(response.xpath("//div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/a[2]/span[contains(@class,'tag')]/text()").extract())
            item['addr'] = sel.xpath("div[contains(@class,'txt')]/div[contains(@class,'tag-addr')]/span[@class='addr']/text()").extract()
            return Request(item['url'],meta={'item':item},callback=self.parse_shop)
        else:
            # here just for an show
            logging.info("Ignore this {} because of repeat".format(url))
            print("Ignore this {} because of repeat".format(url))

    def _parse_hotel_index(self,response,sel,region,subregion):
        """middle step for parsing hotel index page
        """
        url = self.baseurl + sel.xpath("div/div/h2/a[1]/@href").extract()[0]
        if not self.is_in_database(url):
            item = ShopItem()
            item['shopName'] = sel.xpath("div/div/h2/a/text()").extract()
            item['url'] = url
            item['picurl'] = sel.xpath("div[@class='hotel-pics']/ul/li/a/img/@data-lazyload").extract()
            item['overallRate'] = sel.xpath("div/div[@class='hotel-remark']/div[@class='remark']/div/div/span/@title").extract()
            item['price'] = self.ifNotEmptyGetIndex(sel.xpath("div/div[@class='hotel-remark']/div[@class='price']/strong/text()").extract())
            item['commentNum'] = self.ifNotEmptyGetIndex(sel.xpath("div/div[@class='hotel-remark']/div[@class='remark']/div/div/a/text()").re(r'[0-9]+'))
            item['region'] = region
            item['subregion'] = subregion or "Null"
            return Request(item['url'],meta={'item':item},callback=self.parse_hotel_shop)
        else:
            # here just for an show
            logging.info("Ignore this {} because of repeat".format(url))
            print("Ignore this {} because of repeat".format(url))

    def is_in_database(self,url):
        """check if this url is in DB
            Attation: the table name should been changed per. need
        """
        row = cur1.execute("SELECT * FROM `shops-shopping` WHERE `url`=%s", url)
        return row  # 1 stands for true