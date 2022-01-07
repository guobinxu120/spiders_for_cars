from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from scrapy.http import TextResponse
from scrapy.exceptions import CloseSpider
from scrapy import signals
from selenium.webdriver.chrome.options import Options
from datetime import date
import json
import time

class SeleniumMiddleware(object):

    def __init__(self, s):
        self.exec_path = 'chromedriver.exe'
        self.first = False
###########################################################

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)

        crawler.signals.connect(obj.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(obj.spider_closed,
                                signal=signals.spider_closed)
        return obj

###########################################################

    def spider_opened(self, spider):
        try:
            self.d = self.init_driver(self.exec_path)
        except TimeoutException:
            CloseSpider('chromedriver Timeout Error!!!')

###########################################################

    def spider_closed(self, spider):
        self.d.quit()
###########################################################
    
    def process_request(self, request, spider):
        if spider.use_selenium:
            # print "############################ Received url request from scrapy #####"

            try:
                self.d.get(request.url)
                # if not self.first:
                #     self.first = True
                #     time.sleep(60)

            except TimeoutException as e:            
                raise CloseSpider('TIMEOUT ERROR')
            
            lastHeight = self.d.execute_script("return document.body.scrollHeight")
            if 'login.php?frm_action=login' in request.url:
                username_input = self.d.find_element_by_xpath('//input[@id="is3_trade_account_login_username"]')
                username_input.send_keys(spider.email)

                password_input = self.d.find_element_by_xpath('//input[@id="is3_trade_account_login_password"]')
                password_input.send_keys(spider.password)

                self.d.find_element_by_xpath('//button[@name="frm_action"]').click()

                try:
                    self.d.find_element_by_xpath('//a[@class="btn btn-default select-order-type"]').click()
                    time.sleep(2)
                    self.d.find_element_by_xpath('//div[@id="myModalOT"]//button[@button="btn btn-default"]').click()
                except:
                    pass

            # self.d.find_element_by_xpath('//button[@class="btn-signin item"]').click()
            # time.sleep(0.5)
            # self.d.find_element_by_xpath('//input[@id="username"]').send_keys('dabomtv01@gmail.com')
            # self.d.find_element_by_xpath('//input[@id="password"]').send_keys('11223344')
            # self.d.find_element_by_xpath('//button[@class="btn-red btn-signin"]').click()
            # time.sleep(2)
            # self.d.find_elements_by_xpath('//map[@id="uMap2Map22"]/area')[-1].click()
            #
            # response = TextResponse(url=self.d.current_url,
            #                     body=self.d.page_source,
            #                     encoding='utf-8')
            # response.request = request.copy()
            i = 0
            # print "*** Last Height = ", lastHeight
            # while True:
            #     resl = self.d.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            #     time.sleep(7)
            #     newHeight = self.d.execute_script("return document.body.scrollHeight")
            #     if newHeight == lastHeight:
            #         break
            #     lastHeight = newHeight

            # time.sleep(15)
            #
            # selector = None
            # city = None
            # button = None
            #
            # if not "categories" in spider.name:
            #
            #
            #
            #     resultData = ""
            #     next_count = 0
            #     while True:
            #
            #         response = TextResponse(url=self.d.current_url,
            #                     body=self.d.page_source,
            #                     encoding='utf-8')
            #         response.request = request.copy()
            #
            #         product_listing_container = response.xpath('//*[@class="product_listing_container"]')[0]
            #
            #         products = product_listing_container.xpath('.//*[@class="product"]')
            #
            #         print len(products)
            #         print "###########"
            #         print response.url
            #
            #         if not products: return
            #
            #         for i in products:
            #
            #
            #             item = {}
            #
            #             item['Vendedor'] = 140
            #             if not i.xpath('.//*[@class="promotionsApplied"]/@id').extract_first():
            #                 continue
            #             item['ID'] = i.xpath('.//*[@class="promotionsApplied"]/@id').extract_first().split('_')[0]
            #             item['Title'] = i.xpath('.//*[@class="product_name"]/a/text()').extract_first().strip()
            #             #item['Description'] = ''
            #
            #             price = i.xpath('.//*[contains(@id,"offerPrice_")]/text()').re(r'[\d.,]+')
            #             item['Price'] = ''
            #
            #             if price:
            #                 price[0] = price[0].replace('.', '')
            #                 price[0] = price[0].replace(',', '.')
            #                 # if price[0].count('.') == 2:
            #                 #     price[0] = price[0].replace('.', '', 1)
            #             else:
            #                 continue
            #             item['Price'] = price[0]
            #             item['Currency'] = 'CLP'
            #
            #             item['Category URL'] = response.meta['CatURL']
            #             item['Details URL'] = response.urljoin(i.xpath('.//*[@class="product_name"]/a/@href').extract_first().strip())
            #             item['Date'] = str(date.today())
            #
            #             resultData = resultData + json.dumps(item) + '+++++'
            #
            #         # count = len(response.xpath('//ul[@class="pagination"]/li'))
            #         next00 = response.xpath('//*[@class="right_arrow "]')
            #
            #
            #         if next00:
            #             selector = self.d.find_element_by_xpath('//*[@class="right_arrow "]')
            #             selector.click()
            #             time.sleep(1)
            #             continue
            #         break
            #     resp0 = TextResponse(url=self.d.current_url,
            #                         body=resultData, #self.d.page_source,
            #                         encoding='utf-8')
            #     resp0.request = request.copy()
            #
            #     return resp0

            # if response.xpath('//pre/text()').extract_first() == 'Retry later\n':
            #     qqqq = 1
            #     print('stop')


            resp1 = TextResponse(url=self.d.current_url,
                                body=self.d.page_source,
                                encoding='utf-8')
            resp1.request = request.copy()

            # check_str = resp1.xpath('//h1[@id="SearchResultMatches"]')
            # while True:
            #     resp1 = TextResponse(url=self.d.current_url,
            #                     body=self.d.page_source,
            #                     encoding='utf-8')
            #     resp1.request = request.copy()
            #
            #
            #     txt = resp1.xpath('//h5/text()').extract_first()
            #     if txt == "Please verify you're a human to continue.":
            #         time.sleep(2)
            #
            #         print('ERROR: ROBOT')
            #     else:
            #         break

            # check_str = resp1.xpath('//h1[@id="SearchResultMatches"]')
            # while True:
            #     resp1 = TextResponse(url=self.d.current_url,
            #                     body=self.d.page_source,
            #                     encoding='utf-8')
            #     resp1.request = request.copy()
            #
            #
            #     txt = resp1.xpath('//script[@id="hdpApolloPreloadedData"]/text()').extract_first()
            #     try:
            #         json_data = json.loads(json.loads(txt)['apiCache'])
            #         # ds_home_fact_list = resp1.xpath('//li[@class="ds-data-view-item"]/div')
            #         # for li in ds_home_fact_list:
            #         #     temp_name = li.xpath('./h2/text()').extract_first()
            #         #     if 'Listing provided by owner' in temp_name:
            #         #         continue
            #         break
            #     except:
            #         time.sleep(2)
            #
            #         print('ERROR: ROBOT')
            
            return resp1

###########################################################
###########################################################

    def init_driver(self, path):

        chrome_options = Options()
        # chrome_options.add_argument("window-size=3000,3000")
        # chrome_options.add_argument("window-position=-10000,0")
        self.d = webdriver.Chrome(path)
        self.d.set_page_load_timeout(300)

        return self.d