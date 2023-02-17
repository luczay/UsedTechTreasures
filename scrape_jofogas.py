from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, \
    ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import constants
from scrape import Scrape


class ScrapeJofogas(Scrape):
    """
        jofogas.hu scraper
        Attributes:
            driver (Webdriver()): Selenium's chrome webdriver object.
            product_name (str): Search for this product.
            price_min (int): Minimum price of the product.
            price_max (int): Maximum price of the product.
            stop (int): The scraping process stops once the specified number of products have been found.
    """

    def __init__(self, product_name: str, price_min: int, price_max: int, stop: int):
        options = Options()
        options.add_argument('window-size=1980,1080')
        options.add_argument('headless=true')

        self.driver = webdriver.Chrome(options=options, executable_path=constants.driver_path)
        self.product_name = product_name
        self.price_min = price_min
        self.price_max = price_max
        self.stop = stop

    def scrape(self) -> pd.DataFrame:
        """
            This utilizes the private methods 'search()' and 'extract()' to perform scraping on jofogas.hu.
        """
        self._search()
        return self._extract()

    def _search(self):
        """
            Opens the website jofogas.hu and initiates a search using the provided details.
        """
        driver = self.driver
        driver.get('https://www.jofogas.hu/')

        try:
            self._find_by_css(driver, 'button[aria-label="Elfogadás és bezárás: '
                                      'Adatfeldolgozásunk engedélyezése és bezárás"]').click()
        except (TimeoutException, ElementNotInteractableException):
            pass

        self._find_by_css(driver, 'input[type="text"]').send_keys(self.product_name, Keys.ENTER)
        self._find_by_css(driver, 'input[aria-label="Min."]').send_keys(self.price_min)
        self._find_by_css(driver, 'input[aria-label="Max."]').send_keys(self.price_max)
        self._find_by_xpath(driver, '//button[contains(text(), "Keresés")]').click()
        self._find_by_css(driver, 'select[aria-label="Rendezés"]').send_keys(Keys.DOWN, Keys.ENTER)
        self._find_by_css(driver, 'select[aria-label="Rendezés"] > option[value="1"]').click()

    def _extract(self) -> pd.DataFrame:
        """
            Locates web elements that have a link to a product, clicks on them to extract the data,
            and stores it in a Pandas dataframe. Repeats this process until either the specified number of product
            data has been found or there are no more elements to click. If there are no more elements, the method checks
            for the existence of a 'next page' button and, if found, clicks on it to continue the loop. If the button
            does not exist, the method returns the scraped data in the dataframe.
        """
        df = pd.DataFrame(columns=constants.columns)
        driver = self.driver
        next_page = True

        while next_page:
            try:
                self._find_by_xpath(driver, '//a[.//img[@loading="lazy"]]')
            except TimeoutException:
                print("Elements which link to products not found")
                break

            listing_elements = self._find_by_xpath(driver, '//img[@loading="lazy"]', True)
            for listing in range(len(listing_elements)):
                # It's necessary to create a new list in each iteration due to the site reloading
                element = self._find_by_xpath(driver, '//img[@loading="lazy"]', True)[listing]

                if 'jofogas.hu' not in element.get_attribute('src'):
                    continue

                sleep(1)
                try:
                    element.click()
                except ElementClickInterceptedException:
                    driver.execute_script('arguments[0].click()', element)

                try:
                    self._find_by_xpath(driver, '//a[@title="Képek mutatása"]', wait=4)
                except TimeoutException:
                    self._find_by_xpath(driver, '//img[contains(@style, "placeholder")]')

                df.loc[len(df.index)] = [self._get_data('name'), self._get_data('link'),
                                         self._get_data('price'), self._get_data('listed'),
                                         self._get_data('site'), self._get_data('description')]

                # Listing starts from zero
                if listing + 1 == self.stop:
                    driver.quit()
                    return df

                driver.execute_script('window.history.go(-1)')

            try:
                driver.get(
                    self._find_by_xpath(driver, '//a[@class="ad-list-pager-item ad-list-pager-item-next active-item '
                                                'js_hist_li js_hist jofogasicon-right"]').get_attribute('href'))
            except TimeoutException:
                next_page = False
        return df

    def _get_data(self, name_of_data: str) -> str:
        """
            This method locates the web element where the specified 'name_of_data' is located,
            extracts it, and returns it.
            If the element cannot be found, an empty string is returned.
            Args:
                name_of_data (str): The data to be collected from the page.
        """
        driver = self.driver
        try:
            if name_of_data == 'name':
                return self._find_by_css(driver, 'h1[class="title ng-binding ng-scope"]', wait=4).text
            elif name_of_data == 'link':
                return driver.current_url
            elif name_of_data == 'price':
                return self._find_by_css(driver, 'span[class="price-value"]', wait=4).text
            elif name_of_data == 'listed':
                return self._find_by_css(driver, 'span[class="time"]', wait=4).text
            elif name_of_data == 'site':
                return 'jofogas'
            elif name_of_data == 'description':
                return self._find_by_css(driver, 'div[id="linkifyDescription"]', wait=4).text
        except TimeoutException:
            return ''
