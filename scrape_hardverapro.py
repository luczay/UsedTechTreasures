import pandas as pd
from time import sleep
from selenium import webdriver
import constants
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, \
    StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from scrape import Scrape


class ScrapeHardverapro(Scrape):
    """
        hardverapro.hu scraper
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

    def scrape(self):
        """
            This utilizes the private methods 'search()' and 'extract()' to perform scraping on hardverapro.hu.
        """
        self._search()
        return self._extract()

    def _search(self):
        """
            Opens the website hardverapro.hu and initiates a search using the provided details.
        """
        driver = self.driver
        driver.get('https://hardverapro.hu/index.html')

        self._find_by_xpath(driver, '//span[@data-original-title="Részletes keresés..."]').click()
        self._find_by_xpath(driver, '//input[@placeholder="Keresés"]').send_keys(self.product_name)
        self._find_by_xpath(driver, '//input[@placeholder="Min. ár"]').send_keys(self.price_min)
        self._find_by_xpath(driver, '//input[@placeholder="Max. ár"]').send_keys(self.price_max)
        self._find_by_xpath(driver, '//button[@type="submit"]').click()
        sleep(4)

        try:
            self._find_by_xpath(driver, '//div[@id="cookie-accept"]//button').click()
        except TimeoutException:
            pass

        try:
            self._find_by_xpath(driver, '//div[@id="rules-accept"]//button').click()
        except TimeoutException:
            pass

        sleep(3)
        self._find_by_xpath(driver, '(//span[@class="fas fa-chevron-down"])[3]').click()
        self._find_by_xpath(driver, '//*[contains(text(), "olcsók")]').click()

    def _extract(self) -> pd.DataFrame:
        """
            This method finds web elements which will link to a product
            then clicks on them, extract data to a pandas dataframe and goes back to the previous page
            to continue this loop until given number of product data found or there is no more elements to click.
            If there is no more elements, the method will try to find a next page button, if it exists clicks on it and
            continue the loop, if it doesn't exist then returns dataframe with scraped data.
        """
        df = pd.DataFrame(columns=constants.columns)
        driver = self.driver
        next_page = True

        while next_page:
            try:
                self._find_by_xpath(driver, '//a[@class="uad-image align-self-center"]')
            except TimeoutException:
                print("Unable to locate web elements that lead to product")
                break

            listing_elements = self._find_by_xpath(driver, '//a[@class="uad-image align-self-center"]', True)
            for listing in range(len(listing_elements)):
                # Should make a new list everytime because the site reloads in each iteration
                element = self._find_by_xpath(driver, '//a[@class="uad-image align-self-center"]', True)[listing]

                if 'hardverapro.hu' not in element.get_attribute('href'):
                    continue

                time = 1
                for click in range(3):
                    sleep(time)
                    time += 0.5
                    try:
                        element.click()
                    except ElementClickInterceptedException:
                        try:
                            driver.execute_script('arguments[0].click()', element)
                        except StaleElementReferenceException:
                            continue
                    except StaleElementReferenceException:
                        continue

                try:
                    self._find_by_xpath(driver, '//a[@title="Kattints a teljes mérethez!"]')
                except TimeoutException:
                    self._find_by_xpath(driver, '//a[@title="Kattints a teljes mérethez!"]')

                df.loc[len(df.index)] = [self._get_data('name'), self._get_data('link'),
                                         self._get_data('price'), self._get_data('listed'),
                                         self._get_data('site'), self._get_data('description')]

                # Listing starts from zero
                if listing + 1 == self.stop:
                    driver.quit()
                    return df

                driver.execute_script('window.history.go(-1)')

            try:
                driver.get(self._find_by_xpath(driver, '//a[@rel="next"]').get_attribute('href'))
            except TimeoutException:
                break

        return df

    def _get_data(self, name_of_data: str) -> str:
        """
            This method finds the web element where passed name_of_data located then extracts and returns it
            Empty string is returned if element can't be found.
            Args:
                name_of_data (str): Data to get from the page.
        """
        driver = self.driver
        try:
            if name_of_data == 'name':
                return self._find_by_xpath(driver, '//div[@class="uad-content-block"]/h1', wait=4).text
            elif name_of_data == 'link':
                return driver.current_url
            elif name_of_data == 'price':
                return self._find_by_xpath(driver, '//h2[contains(text(), "Ft")]', wait=4).text
            elif name_of_data == 'listed':
                return self._find_by_xpath(driver, '//span[@data-original-title="Feladás időpontja"]', wait=4).text
            elif name_of_data == 'site':
                return 'hardverapro'
            elif name_of_data == 'description':
                return self._find_by_xpath(driver, '//p[@class="mgt0"]', wait=4).text
        except TimeoutException:
            return ''
