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

# def is_ascii(s):
#     try:
#         s.decode('utf-8')
#         print "string is UTF-8, length %d bytes" % len(string)
#     except UnicodeError:
#         print "string is not UTF-8"
#     return all(ord(c) < 128 for c in s)

class citroen_frSpider(Spider):
    name = "citroen_fr_again"
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
    all_data = []
    all_data_old = []

    def start_requests(self):
        yield Request(self.start_url, self.parseMentions)

    def parseMentions(self, response):
        fname = 'result_citroen_fr.csv'
        got_urls_old = []
        got_urls = []

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader = unicode_csv_reader(open(fname, encoding='utf-8'))

        new_field_names = []
        old_datas = []
        for i, row in enumerate(reader):
            if i == 0:
                new_field_names = row
                continue
            old_datas.append(row)

        for i, d in enumerate(old_datas):
            item = OrderedDict()
            for field_index, val in enumerate(d):
                item[new_field_names[field_index]] = val
            self.all_data_old.append(item)
            got_urls_old.append(d[0])


        f2 = open('result_citroen_fr_again_10_17.csv')
        csv_items = csv.DictReader(f2)
        cat_data = {}

        for i, row in enumerate(csv_items):
            self.all_data.append(row)
            got_urls.append(row['Site Web'])
        f2.close()

        chrome_options = Options()
        chrome_options.add_argument("window-size=1500,1500")
        # chrome_options.add_argument('--proxy-server=' + proxy)

        self.driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
        self.driver.set_page_load_timeout(300)

        for i, d in enumerate(self.all_data_old):
            url = d['Site Web']
            index_new = got_urls.index(url)
            data_new = self.all_data[index_new]
            self.all_data_old[i]['Raison Sociale Mentions Légales'] = data_new['Raison Sociale Mentions LÃƒÂ©gales']
            yield self.all_data_old[i]