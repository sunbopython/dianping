from scrapy.utils.request import request_fingerprint
from scrapy.http import Request
import os

def creat_requests_seen():
	requests_seen=set()
	with open('urls.seen','r') as f:
		for line in f:
			r = Request(line.rstrip('\n'))  # remember to strip the '\n' character!!!
			sha1 = request_fingerprint(r)
			requests_seen.add(sha1)
			print("count:{}".format(len(requests_seen)))
	print("finished converting from urls to sha1 total:{}".format(len(requests_seen)))

	with open('requests.seen','a+') as fw:
		for seen in requests_seen:
			fw.write(seen+os.linesep)   # which is "\r\n"

if __name__ == '__main__':
	creat_requests_seen()