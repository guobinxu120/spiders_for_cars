# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from collections import OrderedDict
from scrapy.http import TextResponse

import time, json, csv

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class volkswagen_frSpider(Spider):
    name = "volkswagen_fr"
    start_url = 'https://cdn6.prodworksngwapi.de/sds/search/v2/dealers/{}?dv={}&tenant=v-fra-dcc&comments=7'
    domain1 = 'https://cdn6.prodworksngwapi.de'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['URL', 'Nom', 'Adresse', 'Tel', 'Mail', 'Site Web',
                   'Contact Atelier', 'Tel Atelier', 'Mail Atelier', 'Horaires Ouverture Atelier', 'Contact VN', 'Tel VN',
                   'Mail VN', 'Horaires Ouverture VN', 'Contact VO', 'Tel VO', 'Mail VO', 'Horaires Ouverture VO',
                   'Services disponibles', 'Maps']
    ids = []
    total_count = 0

    def start_requests(self):
        fname = 'input_data/v_ids.csv'

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader):
            dealerid = row[1]
            dv = int(time.time() / 1000)
            url = self.start_url.format(dealerid, str(dv))
            # url = 'https://www.volkswagen.fr/app/trouver-un-concessionnaire/vw-fr/fr/Informations%20sur%20le%20concessionnaire/+/46.701336/1.2644024999999885/6/AXONE AUTOMOBILES SAS/07030/+/+'
            print(str(i))
            yield Request(url, self.parse, meta={'dealerid': dealerid})
            # break


        # f = open("html_volkswagen_fr.html", "r")
        # if f.mode == 'r':
        #     contents = f.read()
        #
        #     resp1 = TextResponse(url='https://cdn6.prodworksngwapi.de',
        #                             body=contents,
        #                             encoding='utf-8')
        #
        #     self.ids = resp1.xpath('//input[@class="StyledInput-sc-8x98id MxwzD"]/@value').extract()
        #
        #     dv = int(time.time() / 1000)
        #
        #     for dealerid in self.ids:
        #         # url = self.start_url.format('07030', str(dv))
        #         # dealerid = '07030'
        #         url = self.start_url.format(dealerid, str(dv))
        #         # url = 'https://www.volkswagen.fr/app/trouver-un-concessionnaire/vw-fr/fr/Informations%20sur%20le%20concessionnaire/+/46.701336/1.2644024999999885/6/AXONE AUTOMOBILES SAS/07030/+/+'
        #         yield Request(url, self.parse, meta={'dealerid': dealerid})
        #         # break

    def parse(self, response):
        item_data = json.loads(response.body).get('dealers')[0]

        item = OrderedDict()
        for field_name in self.field_names:
            item[field_name] = ''

        item['URL'] = 'https://www.volkswagen.fr/app/trouver-un-concessionnaire/vw-fr/fr/Trouvez%20votre%20concessionnaire%20Volkswagen/+/+/+/+/+/+/+/+'
        item['Nom'] = item_data.get('name')

        city = item_data.get('address').get('city')
        street = item_data.get('address').get('street')
        postalCode = item_data.get('address').get('postalCode')

        item['Adresse'] = '{}, {} {}'.format(street, postalCode, city)
        item['Tel'] = item_data.get('contact').get('phoneNumber')
        item['Mail'] = item_data.get('contact').get('email')
        item['Site Web'] = item_data.get('contact').get('website')

        for department_data in item_data.get('departments'):
            department_name = department_data.get('name')
            if not department_data.get('businessHours'):
                continue
            if department_name == 'SERVICE':
                item['Contact Atelier'] = department_data.get('salesPerson')
                item['Tel Atelier'] = department_data.get('contact').get('phoneNumber')
                item['Mail Atelier'] = department_data.get('contact').get('email')

                businessHours = department_data.get('businessHours').get('days')
                data_list = []
                for businessHoursData in businessHours:
                    dayOfWeek = businessHoursData.get('dayOfWeek')
                    week = ''
                    if dayOfWeek == 1:
                        week = 'Lundi'
                    elif dayOfWeek == 2:
                        week = 'Mardi'
                    elif dayOfWeek == 3:
                        week = 'Mercredi'
                    elif dayOfWeek == 4:
                        week = 'Jeudi'
                    elif dayOfWeek == 5:
                        week = 'Vendredi'
                    elif dayOfWeek == 6:
                        week = 'Samedi'
                    elif dayOfWeek == 7:
                        week = 'Dimanche'
                    times = businessHoursData.get('times')
                    times_list = []
                    for time_data in times:
                        times_list.append('{} - {}'.format(time_data.get('from'), time_data.get('till')))

                    data_list.append('{} {}'.format(week, ' '.join(times_list)))
                if len(businessHours) == 5:
                    data_list.append('Samedi Fermé')
                    data_list.append('Dimanche Fermé')
                elif len(businessHours) == 6:
                    data_list.append('Dimanche Fermé')

                item['Horaires Ouverture Atelier'] = '\n'.join(data_list)
            elif department_name == 'SALES_USED':
                item['Contact VN'] = department_data.get('salesPerson')
                item['Tel VN'] = department_data.get('contact').get('phoneNumber')
                item['Mail VN'] = department_data.get('contact').get('email')

                businessHours = department_data.get('businessHours').get('days')
                data_list = []
                for businessHoursData in businessHours:
                    dayOfWeek = businessHoursData.get('dayOfWeek')
                    week = ''
                    if dayOfWeek == 1:
                        week = 'Lundi'
                    elif dayOfWeek == 2:
                        week = 'Mardi'
                    elif dayOfWeek == 3:
                        week = 'Mercredi'
                    elif dayOfWeek == 4:
                        week = 'Jeudi'
                    elif dayOfWeek == 5:
                        week = 'Vendredi'
                    elif dayOfWeek == 6:
                        week = 'Samedi'
                    elif dayOfWeek == 7:
                        week = 'Dimanche'
                    times = businessHoursData.get('times')
                    times_list = []
                    for time_data in times:
                        times_list.append('{} - {}'.format(time_data.get('from'), time_data.get('till')))

                    data_list.append('{} {}'.format(week, ' '.join(times_list)))
                if len(businessHours) == 5:
                    data_list.append('Samedi Fermé')
                    data_list.append('Dimanche Fermé')
                elif len(businessHours) == 6:
                    data_list.append('Dimanche Fermé')

                item['Horaires Ouverture VN'] = '\n'.join(data_list)
            elif department_name == 'SALES':
                item['Contact VO'] = department_data.get('salesPerson')
                item['Tel VO'] = department_data.get('contact').get('phoneNumber')
                item['Mail VO'] = department_data.get('contact').get('email')

                businessHours = department_data.get('businessHours').get('days')
                data_list = []
                for businessHoursData in businessHours:
                    dayOfWeek = businessHoursData.get('dayOfWeek')
                    week = ''
                    if dayOfWeek == 1:
                        week = 'Lundi'
                    elif dayOfWeek == 2:
                        week = 'Mardi'
                    elif dayOfWeek == 3:
                        week = 'Mercredi'
                    elif dayOfWeek == 4:
                        week = 'Jeudi'
                    elif dayOfWeek == 5:
                        week = 'Vendredi'
                    elif dayOfWeek == 6:
                        week = 'Samedi'
                    elif dayOfWeek == 7:
                        week = 'Dimanche'
                    times = businessHoursData.get('times')
                    times_list = []
                    for time_data in times:
                        times_list.append('{} - {}'.format(time_data.get('from'), time_data.get('till')))

                    data_list.append('{} {}'.format(week, ' '.join(times_list)))
                if len(businessHours) == 5:
                    data_list.append('Samedi Fermé')
                    data_list.append('Dimanche Fermé')
                elif len(businessHours) == 6:
                    data_list.append('Dimanche Fermé')

                item['Horaires Ouverture VO'] = '\n'.join(data_list)
        # position = item_data.get('geoPosition').get('coordinates')
        self.total_count += 1
        print('total count: ' + str(self.total_count))
        yield item

        # page_url = 'https://www.volkswagen.fr/app/trouver-un-concessionnaire/vw-fr/fr/Informations%20sur%20le%20concessionnaire/+/46.701336/1.2644024999999885/6/{}/{}/+/+'.format(item['Nom'], str(response.meta.get('dealerid')))
        # yield Request(page_url, self.parsePage, meta={'item': item})

    def parsePage(self, response):
        item = response.meta.get('item')

        services = response.xpath('//div[contains(@class,"StyledContainer-sc-nhelkh ") and contains(@class," StyledBaseContainer-sc-1s9pby4 iNODrL")]')[-1].xpath('.//div[@class="StyledTextComponent-sc-1h30k8b bORLlf"]/text()').extract()
        item['Services disponibles'] = ', '.join(services)

        google_map_url = response.xpath('//div[@class="StyledChildWrapper-sc-1ayh1js bDXDMH"]/a/@href').extract_first()
        item['Maps'] = google_map_url

        self.total_count += 1
        print('total count: ' + str(self.total_count))

        yield item