# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ShopItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    shopName = Field()           # 商户名

    
    # 分类
    channel = Field()            # 频道
    classify = Field()           # 大分类
    classifysub = Field()        # 子分类
    city_pinyin = Field()        # 城市
    region = Field()             # 所属行政位置，如朝阳、海淀、东城等
    subregion = Field()          # 商圈
    
    # url
    url = Field()                # 点评网址
    picurl = Field()             # 图片网址 
    
    #for study
    start = Field()          # 创业时间
    special = Field()            # 特色服务

    # general information
    navigation = Field()         # 导航
      
    # the most import info
    overallRate = Field()        # 总体星级
    commentNum = Field()         # 点评数
    price = Field()              # 人均价格
    first_rating = Field()
    second_rating = Field()
    third_rating = Field()
    addr = Field()               # 商户地址
    phone = Field()              # 联系电话
    
    # branch and recommend
    branch = Field()             # 分店数
    recommend = Field()          # 推荐菜

    # other infor
    alias = Field()              # 别名
    hour = Field()               # 营业时间
    tags = Field()               # 分类标签
    info = Field()               # 商户简介
    reservationNum = Field()     # 预约人数（学习培训）

    # stars numbers
    star5 = Field()            # 五星评价数
    star4 = Field()            # 四星评价数
    star3 = Field()            # 三星评价数
    star2 = Field()            # 二星评价数
    star1 = Field()            # 一星评价数

    # map -related
    poi = Field()
    map_type = Field()
    original_latitude = Field()
    original_longitude = Field()

    # side-bar
    traffic = Field()              # 交通
    nearby_shops = Field()         # 附近商户
    nearby_group = Field()         # 附近团购    