import re

import scrapy
import time
import random
import requests
import json


class IcSpider(scrapy.Spider):
    name = 'ic'
    # allowed_domains = ['www.xx.com']
    start_urls = ['https://member.ic.net.cn/search.php?key=LM324N']

    def start_requests(self):
        url = self.start_urls[0]
        cookies = self.get_cookies_dict()
        yield scrapy.Request(
            url=url,
            cookies=cookies,
            callback=self.parse
        )

    def get_cookies_dict(self):
        ts = str(int(time.time() * 1000))
        formdata = {
            'callback': 'jQuery18107990379122109847_1602315434494',
            'IC_Method': 'userlogin',
            'UserName': '15616122577',
            'Pwd': '123456',
            'RndCode': '',
            'AutoLogin': '1',
            '_': ts
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.14 Safari/537.36',
            'referer': 'https://member.ic.net.cn/login.php',
        }
        url2 = 'https://member.ic.net.cn/asyncCall/login.asy.php'
        result = requests.get(url=url2, params=formdata, headers=headers)
        cookies = requests.utils.dict_from_cookiejar(result.cookies)  # 转成字典格式
        return cookies

    def parse(self, response, **kwargs):
        li_list = response.xpath('//ul[@id="resultList"]/li[contains(@class,"stair_tr")]')[1:]
        for li in li_list:
            item = {}
            a = li.xpath('./div[2]/a/text()').extract_first()
            a = a.strip() if a else None
            b = li.xpath('./div[3]/span/text()').extract_first()
            c = li.xpath('./div[4]/text()').extract_first()
            d = li.xpath('./div[5]/text()').extract_first()
            e = li.xpath('./div[6]/text()').extract_first()
            f = li.xpath('./div[7]/text()').extract_first()
            g = li.xpath('./div[8]//text()').extract()
            item['supplier'] = a
            item['model'] = b
            item['firm'] = c
            item['bat_num'] = d
            item['num'] = e
            item['package'] = f
            item['addr'] = ''.join(g).replace('\r','').replace('\n','').replace('\t','')

            yield item
        # 翻页
        page_num = int(response.xpath('//input[@id="thisPage"]/@value').extract_first())
        if page_num < 11:
            next_url = self.start_urls[0] + f'&page={page_num+1}'
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
            )