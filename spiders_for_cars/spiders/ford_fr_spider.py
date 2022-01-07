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
import pgeocode, math
import time, json, os, csv, requests

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class ford_frSpider(Spider):
    name = "ford_fr"
    start_url = 'https://www.ford.fr/votre-concessionnaire#/search/02100/dealer/FordFF54658%20%20FRA/'
    domain1 = 'https://www.ford.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['URL', 'Nom', 'Adresse', 'Map', 'Tel', 'Site Web',
                   "Horaires d’ouverture", "Horaires d’ouverture pièces", "Horaires d’ouverture service",
                   'Prestations', 'Raison Sociale des Mentions Légales', 'Capital des Mentions Légales',
                   'SIREN des Mentions Légales', 'Siège Social des Mentions Légales']
    dealer_ids = []
    total_count = 0

    def start_requests(self):
        yield Request(self.start_url, self.parse)

    def parse(self, response):
        dealer_data = {}
        nomi = pgeocode.Nominatim('fr')
        temp_entityIDS = []
        for i in range(95):
            n = str(i + 1)
            if len(n) < 2:
                n = '0' + n
            # for j in range(10):
            post_code = n + '000'
            dealer_data[post_code] = []

            res_data = nomi.query_postal_code(post_code)
            if math.isnan(res_data.values[9]):
                continue
            lat = str(res_data.values[9])
            lng = str(res_data.values[10])

            # base_url = 'https://spatial.virtualearth.net/REST/v1/data/1652026ff3b247cd9d1f4cc12b9a080b/FordEuropeDealers_Transition/Dealer?spatialFilter=nearby({},{},160)&$select=*,__Distance&$filter=CountryCode%20Eq%20%27FRA%27&$top=100&$format=json&key=Al1EdZ_aW5T6XNlr-BJxCw1l4KaA0tmXFI_eTl1RITyYptWUS0qit_MprtcG7w2F&Jsonp=collectResults&$skip=0'.format(lat, lng)
            # resp = requests.get(base_url)
            # temp = resp.text.replace('collectResults(', '')
            # temp = temp[: len(temp) - 1]
            # json_data = {}
            # try:
            #     json_data = json.loads(temp).get('d').get('results')
            #     for data in json_data:
            #         entityID = data.get('EntityID')
            #         if entityID in temp_entityIDS:
            #             continue
            #         temp_entityIDS.append(entityID)
            #         dealer_data[post_code].append(entityID)
            #
            #         print('post code: {}, entityID: {}'.format(post_code, entityID))
            #
            #         item = OrderedDict()
            #         for field_name in self.field_names:
            #             item[field_name] = ''
            #         item['URL'] = 'https://www.ford.fr/votre-concessionnaire#/search/'
            #
            #         item['Nom'] = data.get('DealerName')
            #         item['Adresse'] = '{}, {} {}'.format(data.get('AddressLine1'), data.get('Locality'), data.get('PostCode'))
            #
            #         item['Map'] = 'https://maps.google.com?saddr={} Saint-Denis-lès-Bourg, France&daddr=7 Impasse de la Madone+SANCE+71000&output=classic'
            #
            #         tels = resp1.xpath('//p[@class="dl-telephone ng-binding"]//text()').extract()
            #         if tels:
            #             for tel in tels:
            #                 tel = tel.strip()
            #                 if tel:
            #                     item['Tel'] = tel
            #                     break
            #         dealer_primaryURL = resp1.xpath('//p[@data-ng-show="dealer.PrimaryURL"]/a/@href').extract_first()
            #         if dealer_primaryURL and ('http' in dealer_primaryURL):
            #             item['Site Web'] = dealer_primaryURL
            #
            #         dl_dealer_info_tags = resp1.xpath('//div[@class="row dl-dealer-info"]/div/div')
            #         for dl_dealer_info_tag in dl_dealer_info_tags:
            #             title = dl_dealer_info_tag.xpath('./h5/text()').extract_first()
            #             if title:
            #                 title = title.strip()
            #
            #             if title == 'Horaires d’ouverture' or title == 'Horaires d’ouverture pièces' or title == 'Horaires d’ouverture service':
            #                 if item[title]:
            #                     continue
            #                 accordion_content_trs = dl_dealer_info_tag.xpath('./div/table/tbody/tr')
            #                 accordion_vals = []
            #                 for accordion_content_tr in accordion_content_trs:
            #                     vals = accordion_content_tr.xpath('./td/text()').extract()
            #                     val_temps = []
            #                     for v in vals:
            #                         v = v.strip()
            #                         if v:
            #                             val_temps.append(v)
            #                     accordion_vals.append(' '.join(val_temps))
            #                 item[title] = ' / '.join(accordion_vals)
            #
            #             elif title == 'Prestations':
            #                 if item[title]:
            #                     continue
            #                 vals = dl_dealer_info_tag.xpath('./div/p/text()').extract()
            #                 item[title] = ', '.join(vals)
            #         self.total_count += 1
            #         print('Total count: ' + str(self.total_count))
            #         yield item
            # except:
            #     continue

            # break
        print("total entity: " + str(len(temp_entityIDS)))

        chrome_options = Options()
        chrome_options.add_argument("window-size=1500,1500")
        # chrome_options.add_argument('--proxy-server=' + proxy)

        self.driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
        self.driver.set_page_load_timeout(300)

        for post_code in dealer_data.keys():
            entityIDs = dealer_data.get(post_code)
            for entityID in entityIDs:
                url = 'https://www.ford.fr/votre-concessionnaire#/search/{}/dealer/{}/'.format(post_code, entityID.replace(' ', '%20'))
                self.driver.get(url)
                time.sleep(2)

                resp1 = TextResponse(url=url,
                                    body=self.driver.page_source,
                                    encoding='utf-8')

                item = OrderedDict()
                for field_name in self.field_names:
                    item[field_name] = ''
                item['URL'] = 'https://www.ford.fr/votre-concessionnaire#/search/'

                item['Nom'] = resp1.xpath('//h3[contains(@class,"dl-dealer-name dl-dealer-name-details")]/text()').extract_first().strip()

                addresses = resp1.xpath('//p[@class="dl-address-line ng-binding"]/text()').extract()
                add_list = []
                if addresses:
                    for a in addresses:
                        a = a.strip()
                        if a:
                            add_list.append(a)
                item['Adresse'] = ', '.join(add_list)

                item['Map'] = resp1.xpath('//p[@class="dl-directions"]/a/@href').extract_first()

                tels = resp1.xpath('//p[@class="dl-telephone ng-binding"]//text()').extract()
                if tels:
                    for tel in tels:
                        tel = tel.strip()
                        if tel:
                            item['Tel'] = tel
                            break
                dealer_primaryURL = resp1.xpath('//p[@data-ng-show="dealer.PrimaryURL"]/a/@href').extract_first()
                if dealer_primaryURL and ('http' in dealer_primaryURL):
                    item['Site Web'] = dealer_primaryURL

                dl_dealer_info_tags = resp1.xpath('//div[@class="row dl-dealer-info"]/div/div')
                for dl_dealer_info_tag in dl_dealer_info_tags:
                    title = dl_dealer_info_tag.xpath('./h5/text()').extract_first()
                    if title:
                        title = title.strip()

                    if title == 'Horaires d’ouverture' or title == 'Horaires d’ouverture pièces' or title == 'Horaires d’ouverture service':
                        if item[title]:
                            continue
                        accordion_content_trs = dl_dealer_info_tag.xpath('./div/table/tbody/tr')
                        accordion_vals = []
                        for accordion_content_tr in accordion_content_trs:
                            vals = accordion_content_tr.xpath('./td/text()').extract()
                            val_temps = []
                            for v in vals:
                                v = v.strip()
                                if v:
                                    val_temps.append(v)
                            accordion_vals.append(' '.join(val_temps))
                        item[title] = ' / '.join(accordion_vals)

                    elif title == 'Prestations':
                        if item[title]:
                            continue
                        vals = dl_dealer_info_tag.xpath('./div/p/text()').extract()
                        item[title] = ', '.join(vals)
                self.total_count += 1
                print('Total count: ' + str(self.total_count))
                yield item