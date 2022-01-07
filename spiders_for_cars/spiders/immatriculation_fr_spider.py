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

class immatriculation_frSpider(Spider):
    name = "immatriculation_fr"
    start_url = 'https://immatriculation.ants.gouv.fr/Services-associes/Ou-immatriculer-mon-vehicule?displayMap=list&deptNumber={}&types%5B0%5D=garage&order=town'
    domain1 = 'https://reseau.citroen.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['URL', 'Nom', 'Adresse', 'Tel', 'Email', 'Map', 'Latitude', 'Longitude', 'Horraires']

    total_count = 0

    def start_requests(self):
        # ids = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '2A', '2B', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '971', '972', '973', '974', '975', '976', '986', '987', '988', '989']
        ids = ['971', '972', '973', '974', '975', '976', '986', '987', '988', '989']
        for i in ids:
            yield Request(self.start_url.format(i), self.parse, meta={'id_val': i, 'offset': 0})
            # break

    def parse(self, response):

        tags = response.xpath('//div[contains(@class, "col-block col-xs-12 col-sm-4 col-md-4")]/div')
        if not tags:
            return
        for tag in tags:
            item = OrderedDict()
            for field_name in self.field_names:
                item[field_name] = ''

            item['URL'] = response.urljoin(tag.xpath('.//h2[@class="block-document-title"]/a/@href').extract_first())
            item['Nom'] = tag.xpath('.//h2[@class="block-document-title"]/a/text()').extract_first()
            if tag.xpath('.//div[@class="block-document-content"]/a/p/text()').extract_first():
                item['Adresse'] = tag.xpath('.//div[@class="block-document-content"]/a/p/text()').extract_first().strip()

            style = tag.xpath('./@style').extract_first()
            lat = style.split('center=')[-1].split('&markers=')[0].split(',')[0]
            lng = style.split('center=')[-1].split('&markers=')[0].split(',')[1]

            item['Map'] = 'https://maps.google.com/maps?ll={},{}&z=12&t=m&hl=en-US&gl=US&mapclient=apiv3'.format(lat, lng)
            item['Latitude'] = lat
            item['Longitude'] = lng

            yield Request(item['URL'], self.parseInfoUtiles, meta={'item':item})

            # break
        id_val = response.meta.get('id_val')
        offset = response.meta.get('offset') + len(tags)
        response.meta['offset'] = offset
        next_url = 'https://immatriculation.ants.gouv.fr/geoloc/list?types%5B0%5D=garage&offset={}&limit=24&deptNumber={}&order=town'.format(str(offset), id_val)
        yield Request(next_url, self.parse, meta=response.meta)

    def parseInfoUtiles(self, response):
        item = response.meta.get('item')

        datas = response.xpath('//div[@class="article-intro"]//text()').extract()
        tel = ''
        email = ''
        for i, d in enumerate(datas):
            d = d.strip()
            if 'Téléphone' in d:
                tel = datas[i + 1]
            elif 'Adresse mél' in d:
                email = datas[i + 1]
        item['Tel'] = tel
        item['Email'] = email
        item['Horraires'] = response.xpath('//div[@class="article-wysiwyg"]/p/text()').extract_first()

        self.total_count += 1
        print('Total count: ' + str(self.total_count))

        yield item