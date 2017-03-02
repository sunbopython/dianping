#!/usr/bin/python3
# -*- coding: utf-8 -*-

##
##

def Region():

    REGION_DICT = {

                "chaoyang":'r14',
                        
                "haidian":'r17',
                           
                "dongcheng":'r15',
                            
                "xicheng":'r16',
                        
                "fengtai":'r20',
                           
                "daxing":'r5952',
                      
                "changping":'r5950',
                      
                "tongzhou":'r5951',
                       
                "shijingshan":'r328',
                      
                "shunyi":'r9158',
                       
                "huairou":'r27615',
                       
                "fangshan":'r9157',
                       
                "miyun":'c434',
                     
                "yanqing":'c435',
                       
                "mentougou":'r27614',

                "pinggu":'r27616',

            }



    return REGION_DICT

if __name__ == "__main__":
    x = Region()
    for region,regionID in x.items():
        print(region,regionID)