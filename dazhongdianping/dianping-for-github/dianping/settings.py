# -*- coding: utf-8 -*-

# Scrapy settings for dianping project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'dianping'

SPIDER_MODULES = ['dianping.spiders']
NEWSPIDER_MODULE = 'dianping.spiders'

# duplicate handles
#JOBDIR = "duplicate" 

# 
DUPEFILTER_CLASS = 'dianping.dupefilters.VerboseRFPDupeFilter'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 \
#           (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 20

#DOWNLOAD_DELAY = 0.05

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
COOKIES_ENABLED=False


DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'zh-CN,zh;q=0.8',
}

# Configure item pipelines
ITEM_PIPELINES = {
    'dianping.pipelines.DianpingPipeline': 300,
    #'dianping.pipelines.DianpingPipelineAppend':400
}
      
                                                                                                            
# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'dianping.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'dianping.downloadermiddlewares.rotate_useragent.RotateUserAgentMiddleware':400,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware':500,               # scrapy has its defaults
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware':None,
    'dianping.downloadermiddlewares.rotateproxy.ProxyMiddleware': 750,
    #'dianping.downloadermiddlewares.rotateproxy.TopProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 780,  # the order is important here!!
}

# Download_timeout setting
DOWNLOAD_TIMEOUT = 10      # default timeout is 3mins(180s)

# Retry middleware setting
RETRY_ENABLED = True
# Retry many times since proxies often fail
RETRY_TIMES = 6  # initial response + 6 retries = 7 requests
#
RETRY_HTTP_CODES = [404, 408, 500, 502, 503, 504] 

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=True

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
