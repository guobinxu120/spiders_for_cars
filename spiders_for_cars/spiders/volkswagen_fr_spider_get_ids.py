# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from collections import OrderedDict
from scrapy.http import TextResponse
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, json

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class volkswagen_frSpider(Spider):
    name = "get_ids"
    start_url = 'https://www.volkswagen.fr/app/trouver-un-concessionnaire/vw-fr/fr/Trouvez%20votre%20concessionnaire%20Volkswagen/+/+/+/+/+/+/+/+'
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
    postcods = []
    total_count = 0

    def start_requests(self):
        yield Request(self.start_url, self.parse1)

    def parse1(self, response):
        chrome_options = Options()
        chrome_options.add_argument("window-size=1500,1500")
        # chrome_options.add_argument('--proxy-server=' + proxy)

        self.driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
        self.driver.set_page_load_timeout(300)
        self.driver.get(self.start_url)

        try:
            wait = WebDriverWait(self.driver, 30)
            wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@aria-activedescendant="search_suggestion_1"]')))

        except:
            pass

        input_postcode = self.driver.find_element_by_xpath('//input[@aria-activedescendant="search_suggestion_1"]')
        for i in range(95):
            n = str(i + 1)
            if len(n) < 2:
                n = '0' + n
            post_code = n + '00'

            input_postcode.click()
            time.sleep(1)
            input_postcode.clear()

            input_postcode.send_keys(post_code)
            time.sleep(0.5)
            input_postcode.send_keys('0')
            input_postcode.click()
            input_postcode.send_keys(Keys.NULL)
            time.sleep(2)
            try:
                wait = WebDriverWait(self.driver, 30)
                wait.until(EC.visibility_of_element_located((By.XPATH, '//li[@id="search_suggestion_1"]/div/div[2]/a')))

            except:
                pass

            self.driver.find_element_by_xpath('//li[@id="search_suggestion_1"]/div/div[2]/a').click()
            time.sleep(15)

            resp1 = TextResponse(url=self.driver.current_url,
                                body=self.driver.page_source,
                                encoding='utf-8')

            ids_1 = resp1.xpath('//input[@class="StyledInput-sc-8x98id MxwzD"]/@value').extract()

            for id_val in ids_1:
                self.ids.append(id_val)
                yield {'postcode': n + '0', 'id': id_val}
                # if id_val not in self.ids:
                #     self.ids.append(id_val)
                #     yield {'postcode': n + '0', 'id': id_val}

