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

import time, json, os, csv, math
import pgeocode
def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class peugeot_frSpider(Spider):
    name = "peugeot_fr"
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
                   'Tel Camping Car', 'Mail Camping Car',
                   'dealer_id_local']
    ids = []
    total_count = 0
    dealer_id_local_list = []

    def start_requests(self):
        nomi = pgeocode.Nominatim('fr')
        for i in range(95):
            n = str(i + 1)
            if len(n) < 2:
                n = '0' + n
            for j in range(10):
                post_code = n + str(j) + '00'

                res_data = nomi.query_postal_code(post_code)
                if math.isnan(res_data.values[9]):
                    continue
                lat = str(round(res_data.values[9], 2))
                lng = str(round(res_data.values[10], 2))

                base_url = 'https://www.peugeot.fr/api/search-pointofsale/fr/14/FR/1/1/300/30/0/0/0?departure={}%2C{}'
                yield Request(base_url.format(lat, lng), self.parse)




        # data_dict = OrderedDict()
        # for i in range(95):
        #     f = open("input_data/data_for_peugeot/GeocodeService ({}).js".format(str(i)), "r")
        #     if f.mode == 'r':
        #         contents = f.read()
        #         contents = contents.replace('\n', '').split('( ')[-1].replace(')', '')
        #
        #         data = json.loads(contents)
        #         results = data.get('results')
        #         if results:
        #             results = results[0]
        #             address_components = results.get('address_components')[0]
        #             postal_code = address_components.get('long_name')
        #
        #             geometry = results.get('geometry')
        #             location = geometry.get('location')
        #             lat = str(round(location.get('lat'), 2))
        #             lng = str(round(location.get('lng'), 2))
        #
        #             data_dict[postal_code] = {'lat': lat, 'lng':lng}
        #
        #             base_url = 'https://www.peugeot.fr/api/search-pointofsale/fr/14/FR/1/1/300/30/0/0/0?departure={}%2C{}'
        #             yield Request(base_url.format(lat, lng), self.parse, meta={'postal_code': postal_code})
        #     f.close()
        #     break
        #
        # yield Request('https://www.peugeot.fr/api/search-pointofsale/fr/14/FR/1/1/300/30/0/0/0?departure=48.81%2C2.12', self.parse)

    def parse(self, response):
        # self.total_count += 1
        # print('Total count: ' + str(self.total_count))

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
            item['dealer_id_local'] = dealer.get('dealer_id_local')
            # item['id'] = dealer.get('id')
            # item['rrdi'] = dealer.get('rrdi')
            self.total_count += 1
            print('Total count: ' + str(self.total_count))

            yield item