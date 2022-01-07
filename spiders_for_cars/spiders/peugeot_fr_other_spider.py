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

class peugeot_fr_otherSpider(Spider):
    name = "peugeot_fr_other"
    start_url = 'https://concessions.peugeot.fr/bourg01/nous-contacter/agents/liste/'
    domain1 = 'https://concessions.peugeot.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['Liste des Agents de la Concession', 'Raison Sociale', 'Adresse', 'Téléphone', 'Email', 'Site Web']
    ids = []
    total_count = 0

    def start_requests(self):
        fname = 'input_data/data_for_peugeot/input_site.csv'

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader):
            url = row[0]
            # url = 'https://concessions.peugeot.fr/bourg01'
            yield Request(url + '/nous-contacter/agents/liste/', self.parse)
            # break
        #
        # yield Request('https://concessions.peugeot.fr/grcourtois/nous-contacter/agents/liste/', self.parse)

    def parse(self, response):
        agent_list = response.xpath('//div[@class="agent_list"]/ul/li')
        for agent in agent_list:
            item = OrderedDict()
            for field_name in self.field_names:
                item[field_name] = ''

            item['Liste des Agents de la Concession'] = response.url

            p_tags = agent.xpath('./p')
            for p_tag in p_tags:
                title = p_tag.xpath('./span[1]/text()').extract_first()
                if title == 'Concession: ':
                    item['Raison Sociale'] = p_tag.xpath('./span[2]/text()').extract_first()
                elif title == 'Adresse: ':
                    temps = p_tag.xpath('./span[2]//text()').extract()
                    item['Adresse'] = ', '.join(temps)
                elif title == 'Téléphone: ':
                    phone = p_tag.xpath('./span[2]/a/text()').extract_first()
                    n = 2
                    sl = [phone[i:i+n] for i in range(0, len(phone), n)]
                    result = ' '.join(sl)
                    item['Téléphone'] = result
                elif title == 'E-mail: ':
                    email = p_tag.xpath('./span[2]/a/text()').extract_first()
                    item['Email'] = email
            if agent.xpath('./a[@class="more"]/@href').extract_first():
                website = response.urljoin(agent.xpath('./a[@class="more"]/@href').extract_first())
                item['Site Web'] = website

            self.total_count += 1
            print('Total count: ' + str(self.total_count))

            yield item