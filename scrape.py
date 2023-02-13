from abc import ABC, abstractmethod
import pandas as pd
from typing import Union

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


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
