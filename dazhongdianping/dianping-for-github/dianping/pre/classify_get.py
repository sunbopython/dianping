#!/usr/bin/python
# -*- coding: utf-8 -*-

Original = """#!/usr/bin/python3
# -*- coding: utf-8 -*-

##
##

def Content():

    CLASSIFY_DICT = {}
    return CLASSIFY_DICT

if __name__ == "__main__":
    x = Content()
    for channel in x:
        for each in x[channel]:
            print(each[0],each[1])
"""

from bs4 import BeautifulSoup
import re
import logging
try:
    import urllib2 
except:
    import urllib.request as urllib2

# CLASSIFY Ready to supplement the value
CLASSIFY_DICT = {
        ('food',10,'美食'):[],
        ('movie',25,'电影'):[],
        ('life',30,'休闲娱乐'):[],
        ('hotel',60,'酒店'):[('g171','经济型'),('g3020','五星级/豪华型'),('g3022','四星级/高档型'),('g3024','三星级/舒适型'),('g6714','精品酒店'), ('g172','青年旅舍'),('g6693','公寓式酒店'),('g25842','客栈旅舍'),('g173','度假村'),('g174','更多酒店住宿')],
        ('beauty',50,'丽人'):[],
        ('KTV',15,'k歌'):[],
        ('sports',45,'运动健身'):[],
        ('view',35,'景点'):[('g193','亲子摄影'),('g27761','早教中心'),('g161','亲子游乐'),('g27767','婴儿游泳'),('g188','幼儿教育'),    ('g27762','幼儿外语'),('g27763','幼儿才艺'),('g2784','月子会所'),('g27814','孕妇写真'),('g258','孕产护理'),('g33792','上门拍'),('g33797','宝宝派对'),('g125','亲子购物'),('g20009','托班/托儿所'),('g189','幼儿园'),('g33803','亲子玩乐'),('g33808','亲子旅游'),('g27769','更多亲子服务') ],
        ('baby',70,'亲子'):[],
        ('wedding',55,'结婚'):[('','旅游婚纱'),('g163','婚纱摄影'),('g165','婚宴'),('g191','婚戒首饰'),('g162','婚纱礼服'),('g167','婚庆公司'),('g166','彩妆造型'),('g6700','个性写真'),('g164','司仪主持'),('g185','婚礼跟拍'),('g186','婚车租赁'),('g25410','婚房装修'),('g6844','更多婚礼服务'),('g25412','男士礼服'),('g192','婚礼小商品')],
        ('shoppping',20,'购物'):[],
        ('pet',95,'宠物'):[],
        ('other',80,'生活服务'):[],
        ('education',75,'学习培训'):[],
        ('car',65,'爱车'):[],
        ('medical',85,'医疗健康'):[],
        ('home',90,'家装'):[('g25475','装修设计'),('g6826','建材'),('g6828','厨房卫浴'),('g32702','家具家居'),('g32704','家装卖场'),('g32705','家用电器')],
        ('hall',40,'宴会'):[('g3014','酒店宴会厅'),('g3016','特色餐饮'),('g3018','一站式会馆')]
                }
CHANNEL_ID = [ key[1] for key in CLASSIFY_DICT]

class Tag(object):
    """extract our interested tag which has an ID identifiers
    """

    def __init__(self,tag,tagid,cityID=2,channelID=0,classifyID=None,regionID=None):
        self._tag = str(tag)
        self._tagid = str(tagid)
        self.cityID = cityID
        self.channelID = channelID
        self.classifyID = classifyID
        self.regionID = regionID
        self._build_url()

    def _build_url(self):  
        if self.classifyID and self.regionID:
            self.url = 'http://www.dianping.com/search/category/'+str(self.cityID)+\
                        '/'+str(self.channelID)+'/'+str(self.classifyID)+str(self.regionID)
        elif self.classifyID and not self.regionID:
            self.url = 'http://www.dianping.com/search/category/'+str(self.cityID)+\
                        '/'+str(self.channelID)+'/'+str(self.classifyID)
        elif not self.classifyID and self.regionID:
            self.url = 'http://www.dianping.com/search/category/'+\
                        str(self.cityID)+'/'+str(self.channelID)+'/'+str(self.regionID)
        else:
            self.url = 'http://www.dianping.com/search/category/'+\
                        str(self.cityID)+'/'+str(self.channelID)
        print("Request url is: %s" % self.url)

    def _get_tag(self):
        
        req = urllib2.Request(self.url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64)\
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36'})
        html = urllib2.urlopen(req).read()
        soup = BeautifulSoup(html,'html.parser')
        try:        
            return soup.select('#'+self._tagid)[0]
        except IndexError:
            logging.warn("No interesed tag found")

class Classify(Tag):

    def _get_inside_list(self):
        bstag = self._get_tag()
        self._tagList = bstag.select('a')

    def extract_tag_pair_list(self):
        self.taglist=[]
        self._get_inside_list()
        for t in self._tagList:
            ID = re.findall(r'/(\w+)',str(t['href']))[-1]
            pairs = (ID,t.string)
            self.taglist.append(pairs)

if __name__ == '__main__':
    # fill up classify-dict
    for i in CLASSIFY_DICT:
        classify = Classify(tag='div',tagid='classfy',channelID=i[1])
        try:
            classify.extract_tag_pair_list()  
            for c in classify.taglist:
                CLASSIFY_DICT[i].append((c[0],c[1]))
        except:
            logging.warn("No found for channel-%s,id:%s" % (i[0],i[1]))

    # save classify-dict to file
    New = Original.replace("{}",str(CLASSIFY_DICT))
    with open("classfiy.py",'w',encoding ='utf-8') as f:
        f.write(New)
    