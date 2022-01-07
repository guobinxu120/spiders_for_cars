# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from collections import OrderedDict
from scrapy.http import TextResponse
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time, json, os, csv

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class motrio_frSpider(Spider):
    name = "motrio_fr"
    start_url = 'https://www.motrio.fr/garage_locator/'
    domain1 = 'https://www.motrio.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['URL', 'Nom', 'Adresse', 'Téléphone', "Horaires d'ouverture", 'post code']
    ids = []
    total_count = 0

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        for i in range(95):
            n = str(i + 1)
            if len(n) < 2:
                n = '0' + n
            post_code = n + '000'
            url = 'https://www.motrio.fr/garage_locator/ajax/locator/?postal_code={}&latitude=0&longitude=0&partners_only=0'.format(post_code)
            yield Request(url, self.parse, headers=headers, meta={'post_code': post_code})
            # break

    def parse(self, response):
        #########################################
        garage_details = response.xpath('//div[@class="garage-details"]/div[@class="details"]')
        for container in garage_details:
            item = OrderedDict()
            for field_name in self.field_names:
                item[field_name] = ''

            item['URL'] = 'https://www.motrio.fr/garage_locator/'
            item['Nom'] = container.xpath('./div[@class="description-title"]/ul/li/text()').extract_first().strip()

            addr = container.xpath('.//div[@class="contact"]/p/text()').extract()
            item['Adresse'] = ', '.join(addr)

            phone = container.xpath('.//div[@class="phone-number"]/@href').extract_first()
            if phone:
                phone = phone.replace('tel:', '')
                item['Téléphone'] = phone

            hours = container.xpath('./div[@class="hours"]/table/tbody/tr')
            hour_temps = []
            for h in hours:
                hour_temps.append(' '.join(h.xpath('./td/text()').extract()))

            item["Horaires d'ouverture"] = ' / '.join(hour_temps)
            item["post code"] = response.meta.get('post_code')

            self.total_count += 1
            print('Total count: ' + str(self.total_count))

            yield item

