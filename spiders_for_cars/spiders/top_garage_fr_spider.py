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

class top_garage_frSpider(Spider):
    name = "top_garage_fr"
    start_url = 'https://reseau.top-garage.fr'
    domain1 = 'https://reseau.top-garage.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['URL', 'Nom', 'Tel', 'Fax', "Mail", 'Horaires', 'Map',
                   'Latitude', 'Longitude', 'Responsable', 'Prestatations']
    ids = []
    total_count = 0

    def start_requests(self):
        fname = 'input_data/top_garage_urls.csv'
        got_urls = []

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader1 = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader1):
            url = row[0]
            # url = 'https://reseau.top-garage.fr/1003-garage-2000'
            yield Request(url, self.parse)
            # break

    def parse(self, response):

        item = OrderedDict()
        for field_name in self.field_names:
            item[field_name] = ''

        json_data = {}

        script_data = response.xpath('//script[@type="text/javascript"]/text()').extract()
        for script in script_data:
            if 'window.bridge.bootstrap("locations",' in script:
                script = script.split('\n')[1].replace('window.bridge.bootstrap("locations",', '').strip()
                script = script[:len(script)-2]
                json_data = json.loads(script)
                break

        #########################################
        street = response.xpath('//div[@class="lf-locations-address-default__street"]/text()').extract_first().strip()
        city_data_temp = response.xpath('//div[@class="lf-locations-address-default__city"]/span/text()').extract()
        temp = []
        for city_data in city_data_temp:
            city_data = city_data.strip()
            if city_data:
                temp.append(city_data)
        city = ' '.join(temp)
        temp = [street, city]

        item['URL'] = response.url
        item['Nom'] = ', '.join(temp)

        components = json_data.get('components')
        map_data = components.get('map')
        locations = map_data.get('locations')[0]
        contact = locations.get('contact')
        phone = contact.get('phone')

        item['Tel'] = phone.get('number')
        item['Fax'] = contact.get('fax')
        item['Mail'] = contact.get('email')

        lf_openinghours_tags = response.xpath('//div[@id="lf-openinghours"]/div/div[contains(@class,"lf-location-opening-hours-default__row__column")]')
        lf_openinghours_list = []
        for lf_openinghours_tag in lf_openinghours_tags:
            txts = lf_openinghours_tag.xpath('.//text()').extract()
            txt_list = []
            for t in txts:
                t = t.strip()
                if t:
                    txt_list.append(t)
            lf_openinghours_list.append(' '.join(txt_list))
        item['Horaires'] = '\n'.join(lf_openinghours_list)

        localisation = locations.get('localisation')

        address1 = localisation.get('address1')


        coordinates = localisation.get('coordinates')
        city_name = localisation.get('city').get('name')
        postalCode = localisation.get('postalCode')

        map_url = 'https://www.google.com/maps?saddr=&daddr={},{}{}'.format(address1, city_name, postalCode).replace(' ', '%20')
        item['Map'] = map_url

        item['Latitude'] = coordinates.get('latitude')
        item['Longitude'] = coordinates.get('longitude')

        author = response.xpath('//div[@class="lf-location__store-details__left-col__description__content__author"]/text()').extract_first()
        if author:
            author = author.strip()
            item['Responsable'] = author

        availableOfferRanges = locations.get('availableOfferRanges')
        if availableOfferRanges:
            availableOffers = availableOfferRanges[0].get('availableOffers')
            if availableOffers:
                availableOffers_list = []
                for availableOffer in availableOffers:
                    name = availableOffer.get('name')
                    if name:
                        availableOffers_list.append(name)
                item['Prestatations'] = '\n'.join(availableOffers_list)

        self.total_count += 1
        print('Total count: ' + str(self.total_count))

        yield item


