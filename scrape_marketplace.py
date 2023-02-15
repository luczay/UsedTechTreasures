from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import constants
from scrape import Scrape


class ScrapeMarketplace(Scrape):
    """
        marketplace.com scraper
        Attributes:
            driver (Webdriver()): Selenium's chrome webdriver object.
            email (str): Login email.
            password (str): Login password.
            product_name (str): Search for this product.
            price_min (int): Minimum price of the product.
            price_max (int): Maximum price of the product.
            stop (int): The scraping process stops once the specified number of products have been found.
    """

    def __init__(self, product_name: str, price_min: int, price_max: int, stop: int):
        options = Options()
        options.add_argument('window-size=1980,1080')
        options.add_argument('headless=true')
        options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})

        self.driver = webdriver.Chrome(options=options, executable_path=constants.driver_path)
        self.email = 'luczay99@freemail.hu'
        self.password = 'Never.Mind99'
        self.product_name = product_name
        self.price_min = price_min
        self.price_max = price_max
        self.stop = stop

    def scrape(self):
        """
            This utilizes the private methods 'search()' and 'extract()' to perform scraping on marketplace.com.
        """
        self._login()
        self._search()
        return self._extract()

    def _login(self):
        """
            This method launches the Facebook website and logs in to the dummy account.
        """
        driver = self.driver
        driver.get('https://www.facebook.com/')

        self._find_by_xpath(driver, '//button[@data-cookiebanner="accept_button"]').click()
        self._find_by_xpath(driver, '//input[@name="email"]').send_keys(self.email)
        self._find_by_xpath(driver, '//input[@type="password"]').send_keys(self.password)
        sleep(1)
        self._find_by_xpath(driver, '//button[@type="submit"]').click()

    def _search(self):
        """
            Opens the website marketplace.com and initiates a search using the provided details.
        """
        driver = self.driver

        sleep(4)
        self._find_by_xpath(driver, '//*[contains(text(), "Marketplace")]').click()
        sleep(4)
        self._find_by_xpath(driver, '//input[@placeholder="Keresés a Marketplace-en"]').send_keys(self.product_name,
                                                                                                  Keys.ENTER)
        self._find_by_xpath(driver, '//input[@placeholder="Min."]').send_keys(self.price_min)
        sleep(4)
        self._find_by_xpath(driver, '//input[@placeholder="Max."]').send_keys(self.price_max, Keys.ENTER)
        sleep(4)

    def _extract(self) -> pd.DataFrame:
        """
            This method scrolls down the page, if necessary, to load more products. It then locates web elements that
            contain a link to a product, clicks on them to extract the data, and stores it in a Pandas dataframe.
        """
        df = pd.DataFrame(columns=constants.columns)
        driver = self.driver

        for one_scroll in range(int(self.stop / 8)):
            self._scroll()

        listing_elements = self._find_by_xpath(driver, '//a[contains(@href, "marketplace")]//img', True)

        for listing in range(len(listing_elements)):
            element = listing_elements[listing]
            driver.execute_script('arguments[0].scrollIntoView(true)', element)

            if 'scontent' not in element.get_attribute('src'):
                continue

            sleep(1)
            try:
                element.click()
            except (ElementClickInterceptedException, ElementNotInteractableException):
                driver.execute_script('arguments[0].click()', element)

            sleep(1)
            df.loc[len(df.index)] = [self._get_data('name'), self._get_data('link'),
                                     self._get_data('price'), self._get_data('listed'),
                                     self._get_data('site'), self._get_data('description')]

            if listing + 1 == self.stop:
                driver.quit()
                return df

            sleep(2)
            driver.execute_script('window.history.go(-1)')
        return df

    def _scroll(self):
        driver = self.driver
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        sleep(2)

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
                return self._find_by_xpath(driver, '//div[@aria-label="Marketplace-hirdetés megtekintése"]//span['
                                                   '@dir="auto"]', wait=4).text
            elif name_of_data == 'link':
                return driver.current_url
            elif name_of_data == 'price':
                return self._find_by_xpath(driver, '//div[@aria-label="Marketplace-hirdetés megtekintése"]//span['
                                                   'contains(text(), "Ft")]', wait=4).text
            elif name_of_data == 'listed':
                return self._find_by_xpath(driver, '(//div[@aria-label="Marketplace-hirdetés megtekintése"]//span['
                                                   '@dir="auto"])[3]', wait=4).text
            elif name_of_data == 'site':
                return 'marketplace'
            elif name_of_data == 'description':
                description = self._find_by_xpath(driver, '//ul/following-sibling::div//div//span', wait=4).text
                wait = 1
                while (description is None or description == '') and wait < 6:
                    sleep(wait)
                    description = self._find_by_xpath(driver, '//ul/following-sibling::div//div//span', wait=4).text
                    wait += 1
                return description
        except TimeoutException:
            return ''
