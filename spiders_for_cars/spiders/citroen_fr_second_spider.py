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

class citroen_frSecondSpider(Spider):
    name = "citroen_frSecond"
    start_url = 'https://reseau.citroen.fr/reparateur-callac-de-bretagne'
    domain1 = 'https://reseau.citroen.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['Site Web', 'Nom', 'Tel', 'Adresse']
    ids = []
    total_count = 0

    def start_requests(self):
        fname = 'input_data/CitroenSecond.csv'

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader):
            url = row[0]
            yield Request(url, self.parse)
            # break
        #
        # yield Request('https://reseau.citroen.fr/reparateur-callac-de-bretagne', self.parse)

    def parse(self, response):
        tags = response.xpath('//div[@id="ctl00_ctl00_ContentArticle_ContentArticle_ctl00_list_sup_offer"]/ul/li')
        for tag in tags:
            item = OrderedDict()
            for field_name in self.field_names:
                item[field_name] = ''

            item['Site Web'] = response.url
            item['Nom'] = tag.xpath('./div[@class="details"]/span[@class="red uppercase"]/text()').extract_first()

            tel = tag.xpath('./div[@class="details"]/div[@class="phoneLine"]/text()').extract_first()
            if tel:
                tel = tel.split('Tél :')[-1].strip()
            item['Tel'] = tel

            addresses = tag.xpath('./div[@class="details"]/span[2]//text()').extract()
            item['Adresse'] = ', '.join(addresses)
            yield item