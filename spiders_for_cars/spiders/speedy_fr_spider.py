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

class speedy_frSpider(Spider):
    name = "speedy_fr"
    start_url = 'https://centres-auto.speedy.fr'
    domain1 = 'https://centres-auto.speedy.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['URL', 'Nom', 'Adresse', 'Tel', "Longitude", 'Horaires', 'Prestations']
    ids = []
    total_count = 0

    def start_requests(self):
        fname = 'input_data/speedy_urls.csv'

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader):
            url = row[0]
            # yield Request(url, self.parse)
            # break
        yield Request('https://centres-auto.speedy.fr/garage/paris-invalides-75007/426', self.parse)

    def parse(self, response):
        # item = OrderedDict()
        # for field_name in self.field_names:
        #     item[field_name] = ''
        #
        # item['URL'] = response.url
        # item['Nom'] = response.xpath('//div[@id="coordonnees-container"]/h1/text()').extract_first()
        #
        # addr = response.xpath('//div[@id="coordonnees-container"]//div[@itemprop="address"]/span/text()').extract()
        # item['Adresse'] = ', '.join(addr)
        #
        # phone = response.xpath('//div[@id="coordonnees-container"]//span[@itemprop="telephone"]/a/@href').extract_first()
        # if phone:
        #     phone = phone.replace('tel:', '')
        #     item['Tel'] = phone
        #
        # item['Lattitude'] = response.xpath('//meta[@itemprop="latitude"]/@content').extract_first()
        # item['Longitude'] = response.xpath('//meta[@itemprop="longitude"]/@content').extract_first()
        #
        # hours = response.xpath('//div[@id="jours"]/div')
        # hour_temps = []
        # for h in hours:
        #     hour_temps.append(' '.join(h.xpath('./span/text()').extract()))
        #
        # item["Horaires"] = ' / '.join(hour_temps)
        #
        # prestations = response.xpath('//div[@id="prestations"]/ul/li/a/text()').extract()
        # item["Prestations"] = ', '.join(prestations)
        #
        # self.total_count += 1
        # print('Total count: ' + str(self.total_count))
        #
        # yield item


        #########################################
        chrome_options = Options()
        chrome_options.add_argument("window-size=1500,1500")

        self.driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
        self.driver.set_page_load_timeout(300)

        fname = 'input_data/speedy_urls.csv'

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader):
            url = row[0]

            self.driver.get(url)

            resp1 = TextResponse(url=self.driver.current_url,
                                body=self.driver.page_source,
                                encoding='utf-8')

            item = OrderedDict()
            for field_name in self.field_names:
                item[field_name] = ''

            item['URL'] = url
            item['Nom'] = resp1.xpath('//div[@id="coordonnees-container"]/h1/text()').extract_first()

            addr = resp1.xpath('//div[@id="coordonnees-container"]//div[@itemprop="address"]/span/text()').extract()
            item['Adresse'] = ', '.join(addr)

            phone = resp1.xpath('//div[@id="coordonnees-container"]//span[@itemprop="telephone"]/a/@href').extract_first()
            if phone:
                phone = phone.replace('tel:', '')
                item['Tel'] = phone

            item['Lattitude'] = resp1.xpath('//meta[@itemprop="latitude"]/@content').extract_first()
            item['Longitude'] = resp1.xpath('//meta[@itemprop="longitude"]/@content').extract_first()

            hours = resp1.xpath('//div[@id="jours"]/div')
            hour_temps = []
            for h in hours:
                hour_temps.append(' '.join(h.xpath('./span/text()').extract()))

            item["Horaires"] = ' / '.join(hour_temps)

            prestations = resp1.xpath('//div[@id="prestations"]/ul/li//text()').extract()
            item["Prestations"] = ', '.join(prestations)

            self.total_count += 1
            print('Total count: ' + str(self.total_count))

            yield item