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

class ford_fr_otherSpider(Spider):
    name = "ford_fr_other"
    start_url = 'http://www.fordsafi.fr/'
    domain1 = 'https://www.ford.fr'

    driver = None
    conn = None
    use_selenium = True
    total_message_count = 0
    field_names = ['URL du site', 'URL de la Page', 'Nom', 'Nom du Site', 'Adresse', 'Tel', "Fax",
                   "Horaires VN", "Email VN", 'Tel VN',
                   'Horaires VO', 'Email VO', 'Tel VO',
                   'Horaires Ford Entreprise', 'Email Ford Entreprise', 'Tel Ford Entreprise',
                   'Horaires Financement', 'Email Financement', 'Tel Financement',
                   'Horaires PR', 'Email PR', 'Tel PR',
                   'Horaires Entretien', 'Email Entretien', 'Tel Entretien',
                   'Horaires Général', 'Email Général', 'Tel Général',
                   'Horaires Carrosserie', 'Email Carrosserie', 'Tel Carrosserie',
                   'Horaires Fleet', 'Email Fleet', 'Tel Fleet']
    dealer_ids = []
    total_count = 0

    def start_requests(self):
        fname = 'input_data/ford_urls.csv'

        def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
           csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
           for row in csv_reader:
               yield [cell for cell in row]

        # filename = 'da.csv'
        reader = unicode_csv_reader(open(fname, encoding='utf-8'))

        for i, row in enumerate(reader):
            url = row[0]
            yield Request(url, self.parse)
            break
        # yield Request('https://centres-auto.speedy.fr/garage/paris-invalides-75007/426', self.parse)

    def parse(self, response):
        data_branch_temps = response.xpath('//div[@class="gw_contactPanel__contactRotator"]/ul/li/a/@data-branch').extract()
        data_branch_list = []
        for data_branch in data_branch_temps:
            if data_branch in data_branch_list:
                continue
            data_branch_list.append(data_branch)

        for data_branch in data_branch_list:
            url = response.urljoin('/EmplacementConcession/' + data_branch)
            yield Request(url, self.parseDetail, meta={'domain': response.url})
            break

    def parseDetail(self, response):
        item = OrderedDict()
        for field_name in self.field_names:
            item[field_name] = ''
        item['URL du site'] = response.meta.get('domain')
        item['URL de la Page'] = response.url
        item['Nom'] = response.xpath('//h3[@property="name"]/text()').extract_first()

        address = response.xpath('//div[@property="address"]//text()').extract()
        item['Nom du Site'] = address[0]

        address.remove(address[0])
        item['Adresse'] = ', '.join(address)

        phoneNumberas = response.xpath('//div[@id="gw_branch__about"]//span[@class="phoneNumber"]/a/text()').extract()
        item['Tel'] = phoneNumberas[0]
        if len(phoneNumberas) > 1:
            item['Fax'] = phoneNumberas[0]

        panels = response.xpath('//div[@id="gw_branch__departments__info"]/div[@class="panel"]//div[@class="panel-body"]')
        for panel in panels:
            openingHours_temp = panel.xpath('.//div[@property="openingHours"]//text()').extract()
            openingHours = []
            for openingHour in openingHours_temp:
                openingHour = openingHour.strip()
                if openingHour:
                    if openingHour == "Horaires d'ouverture":
                        continue
                    openingHours.append(openingHour)
            openingHours = ' '.join(openingHours)

            email = panel.xpath('.//a[@property="email"]/text()').extract_first()
            phoneNumber = panel.xpath('.//span[@class="phoneNumber"]/a/text()').extract_first()

            openingHours_title = ''
            email_title = ''
            phone_title = ''
            name = panel.xpath('.//h4[@property="name"]/text()').extract_first()
            if name == 'Véhicules Neufs':
                openingHours_title = 'Horaires VN'
                email_title = 'Email VN'
                phone_title = 'Tel VN'
            elif name == 'Véhicules d’Occasion':
                openingHours_title = 'Horaires VO'
                email_title = 'Email VO'
                phone_title = 'Tel VO'
            elif name == 'Ford Entreprise':
                openingHours_title = 'Horaires Ford Entreprise'
                email_title = 'Email Ford Entreprise'
                phone_title = 'Tel Ford Entreprise'
            elif name == 'Financement':
                openingHours_title = 'Horaires Financement'
                email_title = 'Email Financement'
                phone_title = 'Tel Financement'
            elif name == 'Pièces et Accessoires':
                openingHours_title = 'Horaires PR'
                email_title = 'Email PR'
                phone_title = 'Tel PR'
            elif name == 'Entretien':
                openingHours_title = 'Horaires Entretien'
                email_title = 'Email Entretien'
                phone_title = 'Tel Entretien'
            elif name == 'General':
                openingHours_title = 'Horaires Général'
                email_title = 'Email Général'
                phone_title = 'Tel Général'
            elif name == 'Atelier de Carrosserie':
                openingHours_title = 'Horaires Carrosserie'
                email_title = 'Email Carrosserie'
                phone_title = 'Tel Carrosserie'
            elif name == 'Fleet':
                openingHours_title = 'Horaires Fleet'
                email_title = 'Email Fleet'
                phone_title = 'Tel Fleet'
            if email_title:
                item[openingHours_title] = openingHours
                item[email_title] = email
                item[phone_title] = phoneNumber
        yield item