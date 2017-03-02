#! /usr/bin/python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import re
from classify_get import Classify
import logging

Original = """
#!/usr/bin/python3
# -*- coding: utf-8 -*-

##
##

def Content():

    REGION_DICT = {}



    return REGION_DICT

if __name__ == "__main__":
    x = Content()
    for region in x:
        for each in x[region]:
            print(each[0],each[1])
"""

REGION_DICT ={
            "chaoyang":[('r14','不限')],
            "haidian":[('r17','不限')],
            "dongcheng":[('r15','不限')],
            "xicheng":[('r16','不限')],
            "fengtai":[('r20','不限')],
            "daxing":[('r5952','不限')],
            "changping":[('r5950','不限')],
            "tongzhou":[('r5951','不限')],
            "shijingshan":[('r328','不限')],
            "shunyi":[('r9158','不限')],
            "huairou":[('r27615','不限')],
            "fangshan":[('r9157','不限')],
            "miyun":[('c434','不限')],
            "yanqing":[('c435','不限')],
            "mentougou":[('r27614','门头沟区')],
            "pinggu":[('r27616','平谷区')]
            }
# get following from homepage, they stand for admin region id
REGION_ID = ['r14','r17','r15','r16','r20','r5952','r5950','r5951','r328','r9158',
                'r27615','r9157','r27614','r27616','c434','c435']

class Subregion(Classify):
    pass


if __name__ == '__main__':
    # fill up Region-sub
    for r in REGION_DICT:
        subregion = Subregion(tag='div',tagid='region-nav-sub',regionID=REGION_DICT[r][0][0])
        try:
            subregion.extract_tag_pair_list() 
            for index,g in enumerate(subregion.taglist):
                if index!=0:
                    REGION_DICT[r].append((g[0],g[1]))
        except:
            logging.warn("No found for region-%s" % r) 


        # save region-dict to file
        New = Original.replace("{}",str(REGION_DICT))
        with open('subregion.py','w',encoding='utf-8') as fd:
            fd.write(New)
