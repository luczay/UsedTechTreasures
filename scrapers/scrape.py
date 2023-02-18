import pandas as pd
from static import constants
from abc import ABC, abstractmethod
from typing import Union
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


class Scrape(ABC):
    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def _search(self):
        pass

    @abstractmethod
    def _extract(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def _get_data(self, name_of_data: str) -> str:
        pass

    @staticmethod
    def _find_by_css(driver, select: str, all_elems=False, wait=10) -> Union[list, WebElement]:
        """
            Encapsulates selenium's find_elements() and WebdriverWait (using it with CSS selectors)
        """
        if all_elems:
            return driver.find_elements(By.CSS_SELECTOR, select)
        else:
            return WebDriverWait(driver, wait).until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, select)))

    @staticmethod
    def _find_by_xpath(driver: webdriver, select: str, all_elems=False, wait=10) -> Union[list, WebElement]:
        """
            Encapsulates selenium's find_elements() and WebdriverWait (using it with XPATH)
        """
        if all_elems:
            return driver.find_elements(By.XPATH, select)
        else:
            return WebDriverWait(driver, wait).until(ec.presence_of_element_located((By.XPATH, select)))

    @staticmethod
    def _attempt_repetitively(driver: webdriver, selector_type: str,
                              select_str: str, init_time=1, steps=1, end_time=6):
        if not any(constants.selector_types):
            raise Exception('Wrong selector type!')

        data = ''
        time = init_time
        while (data is None or data == '') and time < end_time:
            sleep(time)

            try:
                if selector_type == 'xpath':
                    data = Scrape._find_by_xpath(driver, select_str, wait=4).text
                else:
                    data = Scrape._find_by_css(driver, select_str, wait=4).text
            except TimeoutException:
                pass

            time += steps

        if time == end_time and data is None or data == '':
            data = ''

        return data
