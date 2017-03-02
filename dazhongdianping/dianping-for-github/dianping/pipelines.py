# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from dianping.dbconnect import connection
from bs4 import BeautifulSoup
import re

conn = None

class DianpingPipeline(object):

    def __init__(self):
        self.setupDBCon()
        self.createTable()

    def process_item(self, item, spider):
        for key, value in item.items():
            # handle list and useless HTML tag
            if(isinstance(value,list)):
                if value:   # eliminate empty list
                    templist = []
                    for obj in value:
                        temp = self.stripHTML(obj)
                        templist.append(temp)
                        templist = [i.strip() for i in templist if i] # get rid of empty list element
                    item[key] = templist
                else:
                    item[key] = ""  
            else:
                item[key] = self.stripHTML(value)  

        self.storeInDb(item)

        return item 

    def setupDBCon(self):
        self.cur, self.conn = connection()
        self.conn.set_charset('utf8')
        self.cur.execute('SET NAMES utf8;')
        self.cur.execute('SET CHARACTER SET utf8;')
        self.cur.execute('SET character_set_connection=utf8;')

    def createTable(self):
        """Create table """
        self.cur.execute("DROP TABLE IF EXISTS shops")
        self.cur.execute("CREATE TABLE IF NOT EXISTS shops(id INT NOT NULL AUTO_INCREMENT,\
            shopName VARCHAR(255) default NULL COMMENT '商户名',\
            alias VARCHAR(255) default NULL COMMENT '别名',\
            city_pinyin VARCHAR(20) default NULL COMMENT '城市-拼音',\
            channel VARCHAR(20) default NULL COMMENT '一级分类频道',\
            classify VARCHAR(20) default NULL COMMENT '二级分类',\
            classifysub VARCHAR(20) default NULL COMMENT '三级分类',\
            region VARCHAR(20) default NULL COMMENT '行政大区',\
            subregion VARCHAR(20) default NULL COMMENT '行政子区',\
            overallRate VARCHAR(20) default NULL COMMENT '总体星级',\
            price VARCHAR(20) default NULL COMMENT '均价',\
            phone VARCHAR(50) default NULL COMMENT '电话',\
            reservationNum MEDIUMINT default NULL COMMENT '预定数',\
            hour VARCHAR(100) default NULL COMMENT '营业时间',\
            traffic VARCHAR(512) default NULL COMMENT '交通',\
            addr VARCHAR(255) default NULL COMMENT '地址',\
            start VARCHAR(255) default NULL COMMENT '创立时间',\
            special VARCHAR(255) default NULL COMMENT '特色',\
            commentNum MEDIUMINT default NULL COMMENT '评论数',\
            first_rating VARCHAR(20) default NULL COMMENT '第一项评分',\
            second_rating VARCHAR(20) default NULL COMMENT '第二项评分',\
            third_rating VARCHAR(20) default NULL COMMENT '第三项评分',\
            star1 SMALLINT default NULL COMMENT '一星评价数',\
            star2 SMALLINT default NULL COMMENT '二星评价数',\
            star3 SMALLINT default NULL COMMENT '三星评价数',\
            star4 SMALLINT default NULL COMMENT '四星评价数',\
            star5 SMALLINT default NULL COMMENT '五星评价数',\
            tags VARCHAR(255) default NULL COMMENT '标签',\
            recommend VARCHAR(255) default NULL COMMENT '推荐',\
            info VARCHAR(2000) default NULL COMMENT '介绍',\
            url VARCHAR(100) default NULL COMMENT '网址',\
            navigation VARCHAR(100) default NULL COMMENT '导航',\
            branch VARCHAR(100) default NULL COMMENT '分店数',\
            picurl VARCHAR(512) default NULL COMMENT '图片网址',\
            nearby_shops VARCHAR(255) default NULL COMMENT '附近商户',\
            nearby_group VARCHAR(255) default NULL COMMENT '附近团购',\
            map_type SMALLINT default NULL COMMENT '地图类型码',\
            poi VARCHAR(50) default NULL COMMENT 'poi字符串',\
            original_latitude FLOAT(11,8) default NULL COMMENT '纬度',\
            original_longitude FLOAT(11,8) default NULL COMMENT '经度',\
            PRIMARY KEY (id)\
            )")


    def storeInDb(self,item):
        self.cur.execute("INSERT INTO `shops`(\
            `shopName`,\
            `alias`,\
            `city_pinyin`,\
            `channel`,\
            `classify`,\
            `classifysub`,\
            `region`,\
            `subregion`,\
            `overallRate`,\
            `price`,\
            `phone`,\
            `reservationNum`,\
            `hour`,\
            `traffic`,\
            `addr`,\
            `start`,\
            `special`,\
            `commentNum`,\
            `first_rating`,\
            `second_rating`,\
            `third_rating`,\
            `star1`,\
            `star2`,\
            `star3`,\
            `star4`,\
            `star5`,\
            `tags`,\
            `recommend`,\
            `info`,\
            `url`,\
            `navigation`,\
            `branch`,\
            `picurl`,\
            `nearby_shops`,\
            `nearby_group`,\
            `map_type`,\
            `poi`,\
            `original_latitude`,\
            `original_longitude`\
            ) \
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",\
               (\
                item.get('shopName','') or "ShopNameNeedToChange",   # shop name problem because of unknown reason
                item.get('alias',''),
                item.get('city_pinyin',''),
                item.get('channel',''),
                item.get('classify',''),
                item.get('classifysub',''),
                item.get('region',''),
                item.get('subregion',''),
                item.get('overallRate','')[0],
                self.cleanPrice(item.get('price')),
                ','.join(item.get('phone','')),
                item.get('reservationNum','0').split('\n')[0],
                item.get('hour','0')[0],
                item.get('traffic','Null'),
                item.get('addr','nothing'), 
                item.get('start',''),
                ','.join(item.get('special','')),
                int(item.get('commentNum') or '0'),
                item.get('first_rating',''),
                item.get('second_rating',''),
                item.get('third_rating',''),
                int(self.cleanEmpty(item.get('star1'),default='0')),
                int(self.cleanEmpty(item.get('star2'),default='0')),
                int(self.cleanEmpty(item.get('star3'),default='0')), 
                int(self.cleanEmpty(item.get('star4'),default='0')),
                int(self.cleanEmpty(item.get('star5'),default='0')),
                ','.join(item.get('tags','')),
                ','.join(item.get('recommend','')),
                item.get('info','0')[0],
                item.get('url',''),
                '>>'.join(item.get('navigation','')),
                item.get('branch',''),
                ','.join(item.get('picurl','')),
                ','.join(item.get('nearby_shops','')),
                ','.join(item.get('nearby_group','')),

                item.get('map_type',''),
                item.get('poi',''),
                item.get('original_latitude',''),
                item.get('original_longitude',''),
                ))
        self.conn.commit()
        # except Exception as e:
                #     print(e)
                # 
    def cleanPrice(self,string):
        """extract only number from price string"""
        if string not in ["Null","\r","-",'']:
            return re.search(r'[0-9]+',string).group()
        else:
            return string

    def cleanEmpty(self,string,default=None):
        return string if string else default

    def __del__(self):
        self.closeDB()

    def closeDB(self):
        self.conn.close()

    def stripHTML(self,string):
        string_without_escape = string.strip('\n\t ')
        tagStripper = MLStripper()
        tagStripper.feed(string_without_escape)
        return tagStripper.get_data()

class DianpingPipelineAppend(DianpingPipeline):

    def createTable(self):
        """Create table """
        self.cur.execute("DROP TABLE IF EXISTS shops_append")
        self.cur.execute("CREATE TABLE IF NOT EXISTS shops_append(id INT NOT NULL AUTO_INCREMENT,\
            shopName VARCHAR(255) default NULL COMMENT '商户名',\
            alias VARCHAR(255) default NULL COMMENT '别名',\
            city_pinyin VARCHAR(20) default NULL COMMENT '城市-拼音',\
            channel VARCHAR(20) default NULL COMMENT '一级分类频道',\
            classify VARCHAR(20) default NULL COMMENT '二级分类',\
            classifysub VARCHAR(20) default NULL COMMENT '三级分类',\
            region VARCHAR(20) default NULL COMMENT '行政大区',\
            subregion VARCHAR(20) default NULL COMMENT '行政子区',\
            overallRate VARCHAR(20) default NULL COMMENT '总体星级',\
            price VARCHAR(20) default NULL COMMENT '均价',\
            phone VARCHAR(50) default NULL COMMENT '电话',\
            reservationNum MEDIUMINT default NULL COMMENT '预定数',\
            hour VARCHAR(100) default NULL COMMENT '营业时间',\
            traffic VARCHAR(512) default NULL COMMENT '交通',\
            addr VARCHAR(255) default NULL COMMENT '地址',\
            start VARCHAR(255) default NULL COMMENT '创立时间',\
            special VARCHAR(255) default NULL COMMENT '特色',\
            commentNum MEDIUMINT default NULL COMMENT '评论数',\
            first_rating VARCHAR(20) default NULL COMMENT '第一项评分',\
            second_rating VARCHAR(20) default NULL COMMENT '第二项评分',\
            third_rating VARCHAR(20) default NULL COMMENT '第三项评分',\
            star1 SMALLINT default NULL COMMENT '一星评价数',\
            star2 SMALLINT default NULL COMMENT '二星评价数',\
            star3 SMALLINT default NULL COMMENT '三星评价数',\
            star4 SMALLINT default NULL COMMENT '四星评价数',\
            star5 SMALLINT default NULL COMMENT '五星评价数',\
            tags VARCHAR(255) default NULL COMMENT '标签',\
            recommend VARCHAR(255) default NULL COMMENT '推荐',\
            info VARCHAR(2000) default NULL COMMENT '介绍',\
            url VARCHAR(100) default NULL COMMENT '网址',\
            navigation VARCHAR(100) default NULL COMMENT '导航',\
            branch VARCHAR(100) default NULL COMMENT '分店数',\
            picurl VARCHAR(512) default NULL COMMENT '图片网址',\
            nearby_shops VARCHAR(255) default NULL COMMENT '附近商户',\
            nearby_group VARCHAR(255) default NULL COMMENT '附近团购',\
            map_type SMALLINT default NULL COMMENT '地图类型码',\
            poi VARCHAR(50) default NULL COMMENT 'poi字符串',\
            original_latitude FLOAT(11,8) default NULL COMMENT '纬度',\
            original_longitude FLOAT(11,8) default NULL COMMENT '经度',\
            PRIMARY KEY (id)\
            )")

    def storeInDb(self,item):
        self.cur.execute("INSERT INTO `shops_append`(\
            `shopName`,\
            `alias`,\
            `city_pinyin`,\
            `channel`,\
            `classify`,\
            `classifysub`,\
            `region`,\
            `subregion`,\
            `overallRate`,\
            `price`,\
            `phone`,\
            `reservationNum`,\
            `hour`,\
            `traffic`,\
            `addr`,\
            `start`,\
            `special`,\
            `commentNum`,\
            `first_rating`,\
            `second_rating`,\
            `third_rating`,\
            `star1`,\
            `star2`,\
            `star3`,\
            `star4`,\
            `star5`,\
            `tags`,\
            `recommend`,\
            `info`,\
            `url`,\
            `navigation`,\
            `branch`,\
            `picurl`,\
            `nearby_shops`,\
            `nearby_group`,\
            `map_type`,\
            `poi`,\
            `original_latitude`,\
            `original_longitude`\
            ) \
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",\
               (\
                item.get('shopName','') or "ShopNameNeedToChange",   # shop name problem because of unknown reason
                item.get('alias',''),
                item.get('city_pinyin',''),
                item.get('channel',''),
                item.get('classify',''),
                item.get('classifysub',''),
                item.get('region',''),
                item.get('subregion',''),
                item.get('overallRate',''),

                self.cleanPrice(item.get('price')),
                ','.join(item.get('phone','')),
                item.get('reservationNum','0').split('\n')[0],
                item.get('hour',''),
                item.get('traffic',''),
                item.get('addr',''), 
                item.get('start',''),
                ','.join(item.get('special','')),
                int(item.get('commentNum') or '0'),
                item.get('first_rating',''),
                item.get('second_rating',''),
                item.get('third_rating',''),
                int(self.cleanEmpty(item.get('star1'),default='0')),
                int(self.cleanEmpty(item.get('star2'),default='0')),
                int(self.cleanEmpty(item.get('star3'),default='0')), 
                int(self.cleanEmpty(item.get('star4'),default='0')),
                int(self.cleanEmpty(item.get('star5'),default='0')),
                ','.join(item.get('tags','')),
                ','.join(item.get('recommend','')),
                item.get('info',''),
                item.get('url',''),
                '>>'.join(item.get('navigation','')),
                item.get('branch',''),
                ','.join(item.get('picurl','')),
                ','.join(item.get('nearby_shops','')),
                ','.join(item.get('nearby_group','')),

                item.get('map_type',''),
                item.get('poi',''),
                item.get('original_latitude',''),
                item.get('original_longitude',''),
                ))
        self.conn.commit()



from html.parser import HTMLParser#
class MLStripper(HTMLParser):
    """receive a string which has useless html tag and return another string without tag
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed=[]
    def handle_data(self,d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)