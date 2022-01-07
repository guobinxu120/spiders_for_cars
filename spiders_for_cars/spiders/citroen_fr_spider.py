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

class citroen_frSpider(Spider):
    name = "citroen_fr"
    start_url = 'https://reseau.citroen.fr/reparateur-callac-de-bretagne'
    domain1 = 'https://reseau.citroen.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['Site Web', 'Nom', 'Tel', 'Adresse', 'Longitude', 'Latitude', 'Raison Sociale Mentions Légales',
                   'Capital Social Mentions Légales', 'SIRET Mentions Légales', 'N° TVA Mentions Légales',
                   'Horraires Généraux', 'Horraires VN', 'Horraires VO',
                   'Horraires APV', 'Liste des Agents']
    ids = []
    total_count = 0

    def start_requests(self):
        fname = 'input_data/Citroen_got.csv'
        got_urls = []

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader):
            got_urls.append(row[0])


        fname = 'input_data/Citroen.csv'

        # filename = 'da.csv'
        reader1 = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader1):
            url = row[0]
            if 'https://' + url not in got_urls:
                yield Request('https://' + url, self.parse)
            # break
        #
        # yield Request('https://reseau.citroen.fr/reparateur-callac-de-bretagne', self.parse)

    def parse(self, response):
        item = OrderedDict()
        for field_name in self.field_names:
            item[field_name] = ''

        item['Site Web'] = response.url
        item['Nom'] = response.xpath('//span[@class="hlDealerName_DS"]/text()').extract_first()

        tel = response.xpath('//div[@class="info"]/p[@class="tel"]/text()').extract_first()
        if tel:
            tel = tel.split('Tél :')[-1].strip()
        item['Tel'] = tel

        addresses = response.xpath('//div[@class="info"]/address//text()').extract()
        add_list = []
        if addresses:
            for a in addresses:
                a = a.strip()
                if a:
                    add_list.append(a)
        item['Adresse'] = ', '.join(add_list)
        item['Longitude'] = response.xpath('//input[@id="ctl00_hdCoordX"]/@value').extract_first()
        item['Latitude'] = response.xpath('//input[@id="ctl00_hdCoordY"]/@value').extract_first()

        item['Raison Sociale Mentions Légales'] = ''
        item['Capital Social Mentions Légales'] = ''
        item['SIRET Mentions Légales'] = ''
        item['N° TVA Mentions Légales'] = ''

        info_utiles_url = response.url + '/nous-contacter/info-utiles/'
        yield Request(info_utiles_url, self.parseInfoUtiles, meta={'item':item})

    def parseInfoUtiles(self, response):
        item = response.meta.get('item')

        general_schedules = response.xpath('//p[contains(@id, "general_Schedule")]//span[@class="ScheduleFullText"]//text()').extract()
        data_list = []
        for general_schedule in general_schedules:
            general_schedule = general_schedule.strip()
            if general_schedule:
                data_list.append(general_schedule)
        item['Horraires Généraux'] = ' / '.join(data_list)


        row_items = response.xpath('//div[@class="content-box"]/div[@class="row"]/div[contains(@class,"item")]')
        for row_item in row_items:
            title = row_item.xpath('./h4/span/text()').extract_first()
            if title == 'Véhicule neuf':
                general_schedules = row_item.xpath('./div/span[@class="ScheduleFullText"]//text()').extract()
                data_list = []
                for general_schedule in general_schedules:
                    general_schedule = general_schedule.strip()
                    if general_schedule:
                        data_list.append(general_schedule)
                item['Horraires VN'] = ' / '.join(data_list)
            elif title == "Véhicule d'occasion":
                general_schedules = row_item.xpath('./div/span[@class="ScheduleFullText"]//text()').extract()
                data_list = []
                for general_schedule in general_schedules:
                    general_schedule = general_schedule.strip()
                    if general_schedule:
                        data_list.append(general_schedule)
                item['Horraires VO'] = ' / '.join(data_list)
            elif title == "Après vente":
                general_schedules = row_item.xpath('./div/span[@class="ScheduleFullText"]//text()').extract()
                data_list = []
                for general_schedule in general_schedules:
                    general_schedule = general_schedule.strip()
                    if general_schedule:
                        data_list.append(general_schedule)
                item['Horraires APV'] = ' / '.join(data_list)


        naves = response.xpath('//div[@id="nav2"]/ul/li/a')
        for nav in naves:
            title = nav.xpath('./span/text()').extract_first()
            if title:
                title = title.strip()
                if title == 'Nos agents':
                    item['Liste des Agents'] = response.urljoin(nav.xpath('./@href').extract_first())

        mentions_url = item['Site Web'] + '/accueil/mentions-legales-citroen/'
        yield Request(mentions_url, self.parseMentions, meta={'item':item})

    def parseMentions(self, response):
        item = response.meta.get('item')

        p_tags = response.xpath('//div[@id="content-container"]/p//text()').extract()
        for p in p_tags:
            p = p.strip()
            if 'Capital social : ' in p:
                p = p.replace('Capital social : ', '')
                item['Capital Social Mentions Légales'] = p
            elif 'N° de SIRET : ' in p:
                p = p.replace('N° de SIRET : ', '')
                item['SIRET Mentions Légales'] = p
            elif 'N° de TVA : ' in p:
                p = p.replace('N° de TVA : ', '')
                item['N° TVA Mentions Légales'] = p


        self.total_count += 1
        print('Total count: ' + str(self.total_count))

        yield item