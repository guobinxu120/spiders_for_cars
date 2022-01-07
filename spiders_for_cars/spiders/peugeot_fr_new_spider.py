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

class peugeot_frSpider(Spider):
    name = "peugeot_fr_new"
    start_url = 'https://www.peugeot.fr/points-de-vente.html'
    domain1 = 'https://www.peugeot.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['URL', 'Raison Sociale', 'Horaires', 'Adresse', 'Tel', 'Mail', 'Site Web',
                   'Latitude', 'Longitude', 'Liste des Agents', 'Site du Groupe', 'Google Maps', 'Tel VN',
                   'Mail VN', 'Tel APV', 'Mail APV', 'Tel PR', 'Mail PR', 'Tel VO',
                   'Mail VO', 'Tel Service Rapide', 'Mail Service Rapide', 'Tel ODL', 'Mail ODL', 'Tel Carrosserie',
                   'Mail Carrosserie', 'Tel Reprise Autobiz', 'Mail Reprise Autobbiz', 'Tel Reprise Cash',
                   'Mail Reprise Cash', 'Tel Charte B2B Après-vente', 'Mail Charte B2B Après-vente',
                   'Tel Camping Car', 'Mail Camping Car']
    ids = []
    dealer_id_local_list = []
    total_count = 0

    def start_requests(self):
        f = open("22.html", "r")
        if f.mode == 'r':
            contents = f.read()
            temps = contents.split('X_COORDINATE=&quot;')
            x_val_list = []
            for t in temps:
                x_val = t.split('&quot')[0]
                try:
                    x_val = round(float(x_val), 2)
                    x_val_list.append(x_val)
                except:
                    continue

            temps = contents.split('Y_COORDINATE=&quot;')
            y_val_list = []
            for t in temps:
                y_val = t.split('&quot')[0]
                try:
                    y_val = round(float(y_val), 2)
                    y_val_list.append(y_val)
                except:
                    continue

            for i, lat in enumerate(y_val_list):
                lng = x_val_list[i]
                base_url = 'https://www.peugeot.fr/api/search-pointofsale/fr/14/FR/1/1/300/30/0/0/0?departure={}%2C{}'
                yield Request(base_url.format(lat, lng), self.parse)
                # break


            # resp1 = TextResponse(url='https://cdn6.prodworksngwapi.de',
            #                         body=contents,
            #                         encoding='utf-8')
            #
            #
            # self.ids = resp1.xpath('//input[@class="StyledInput-sc-8x98id MxwzD"]/@value').extract()
            #
            # dv = int(time.time() / 1000)
            #
            # for dealerid in self.ids:
            #     # url = self.start_url.format('07030', str(dv))
            #     # dealerid = '07030'
            #     url = self.start_url.format(dealerid, str(dv))
            #     # url = 'https://www.volkswagen.fr/app/trouver-un-concessionnaire/vw-fr/fr/Informations%20sur%20le%20concessionnaire/+/46.701336/1.2644024999999885/6/AXONE AUTOMOBILES SAS/07030/+/+'
            #     yield Request(url, self.parse, meta={'dealerid': dealerid})


    def parse(self, response):
        item_data = json.loads(response.body)
        listDealer = item_data.get('listDealer')
        # yield {"count": str(len(listDealer)), 'postal_code': response.meta.get('postal_code')}

        for i, dealer in enumerate(listDealer):
            if dealer.get('dealer_id_local') in self.dealer_id_local_list:
                continue
            self.dealer_id_local_list.append(dealer.get('dealer_id_local'))
            # if i != 5:
            #     continue
            item = OrderedDict()
            for field_name in self.field_names:
                item[field_name] = ''

            item['URL'] = 'https://www.peugeot.fr/points-de-vente.html'
            item['Raison Sociale'] = dealer.get('name')

            schedules = dealer.get('schedules')
            if schedules:
                schedules = schedules.replace('<br />', ' /').replace(' / ', '---').replace(' /', '').replace('---', ' / ')
            item['Horaires'] = schedules

            city = dealer.get('adress').get('city')
            street = dealer.get('adress').get('street')
            # postalCode = item_data.get('address').get('postalCode')

            item['Adresse'] = '{}, {}'.format(street, city)

            contact = dealer.get('contact')
            if contact.get('tel'):
                item['Tel'] = contact.get('tel')
            if contact.get('mail'):
                item['Mail'] = contact.get('mail')
            if contact.get('website'):
                item['Site Web'] = contact.get('website')

            item['Latitude'] = dealer.get('adress').get('lat')
            item['Longitude'] = dealer.get('adress').get('lng')

            ctaList = dealer.get('ctaList')
            for cta in ctaList:
                if cta.get('version') == 'cta-contact':
                    item['Liste des Agents'] = cta.get('url')
                elif cta.get('version') == 'cta-direction':
                    item['Google Maps'] = cta.get('url')

            services = dealer.get('services')
            for service in services:
                code = service.get('code')
                if code == 'vn':
                    item['Tel VN'] = service.get('tel')
                    item['Mail VN'] = service.get('mail')
                elif code == 'apv':
                    item['Tel APV'] = service.get('tel')
                    item['Mail APV'] = service.get('mail')
                elif code == 'pr':
                    item['Tel PR'] = service.get('tel')
                    item['Mail PR'] = service.get('mail')
                elif code == 'vo':
                    item['Tel VO'] = service.get('tel')
                    item['Mail VO'] = service.get('mail')
                elif code == 'd':
                    item['Tel Service Rapide'] = service.get('tel')
                    item['Mail Service Rapide'] = service.get('mail')
                elif code == 'a':
                    item['Tel ODL'] = service.get('tel')
                    item['Mail ODL'] = service.get('mail')
                elif code == 'k':
                    item['Tel Carrosserie'] = service.get('tel')
                    item['Mail Carrosserie'] = service.get('mail')
                elif code == '11096':
                    item['Tel Reprise Autobiz'] = service.get('tel')
                    item['Mail Reprise Autobbiz'] = service.get('mail')
                elif code == '4990':
                    item['Tel Reprise Cash'] = service.get('tel')
                    item['Mail Reprise Cash'] = service.get('mail')
                elif code == '7607':
                    item['Tel Charte B2B Après-vente'] = service.get('tel')
                    item['Mail Charte B2B Après-vente'] = service.get('mail')
                elif code == '6943':
                    item['Tel Camping Car'] = service.get('tel')
                    item['Mail Camping Car'] = service.get('mail')

            self.total_count += 1
            print('Total count: ' + str(self.total_count))

            yield item