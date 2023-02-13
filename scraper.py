import constants
from data_cleaner import DataCleaner
from scrape_hardverapro import ScrapeHardverapro
from scrape_jofogas import ScrapeJofogas
from scrape_marketplace import ScrapeMarketplace
from database import Database
import pandas as pd


class Scraper:
    """
        Handles the scraping of data from the three websites
        and provides methods for cleaning and saving the scraped data.
        Attributes:
            _product_name (str): Search for this product.
            _price_min (int): Minimum price of the product.
            _price_max (int): Maximum price of the product.
            _stop (int): The scraping process stops once the specified number of products have been found.
            _jofogas_df (str): Stores the scraped data from jofogas
            _hardverapro_df (str): Stores the scraped data from hardverapro
            _marketplace_df (str): Stores the scraped data from marketplace
    """

    def __init__(self, product_name: str, price_min: int, price_max: int, stop: int):
        self._product_name = product_name
        self._price_min = price_min
        self._price_max = price_max
        self._stop = stop
        self._jofogas_df = pd.DataFrame(columns=constants.columns)
        self._hardverapro_df = pd.DataFrame(columns=constants.columns)
        self._marketplace_df = pd.DataFrame(columns=constants.columns)

    def extract_data(self, hardverapro: str, jofogas: str, marketplace: str):
        """
            Performs scraping on each website through the use of their respective scraping classes,
            namely ScrapeHardverapro, ScrapeJofogas, and ScrapeMarketplace
        """
        if hardverapro != '':
            self._hardverapro_df = pd.concat([self._hardverapro_df,
                                             ScrapeHardverapro(self._product_name, self._price_min, self._price_max,
                                                               self._stop).scrape()])

        if jofogas != '':
            self._jofogas_df = pd.concat([self._jofogas_df,
                                         ScrapeJofogas(self._product_name, self._price_min, self._price_max,
                                                       self._stop).scrape()])

        if marketplace != '':
            self._marketplace_df = pd.concat([self._marketplace_df,
                                             ScrapeMarketplace(self._product_name, self._price_min, self._price_max,
                                                               self._stop).scrape()])

    def clean_data(self):
        """
            Cleans the scraped data
        """
        data_cleaner = DataCleaner('')

        if len(self._marketplace_df.index) != 0:
            data_cleaner.site = 'marketplace'

            self._marketplace_df['listed'] = self._marketplace_df['listed'].apply(
                lambda data: data_cleaner.clean_date(data))
            self._marketplace_df['price'] = self._marketplace_df['price'].apply(
                lambda data: data_cleaner.clean_price(data))
            self._marketplace_df['description'] = self._marketplace_df['description'].apply(
                lambda data: data_cleaner.clean_description(data))

        if len(self._jofogas_df.index) != 0:
            data_cleaner.site = 'jofogas'

            self._jofogas_df['listed'] = self._jofogas_df['listed'].apply(
                lambda data: data_cleaner.clean_date(data))
            self._jofogas_df['price'] = self._jofogas_df['price'].apply(
                lambda data: data_cleaner.clean_price(data))
            self._jofogas_df['description'] = self._jofogas_df['description'].apply(
                lambda data: data_cleaner.clean_description(data))

        if len(self._hardverapro_df.index) != 0:
            data_cleaner.site = 'hardverapro'

            self._hardverapro_df['listed'] = self._hardverapro_df['listed'].apply(
                lambda data: data_cleaner.clean_date(data))
            self._hardverapro_df['price'] = self._hardverapro_df['price'].apply(
                lambda data: data_cleaner.clean_price(data))
            self._hardverapro_df['description'] = self._hardverapro_df['description'].apply(
                lambda data: data_cleaner.clean_description(data))

    def save_data(self, temp=False):
        """
            Saves the scraped data to database
        """
        concated_dfs = self.concat_dfs()
        Database.add_scraped_data(concated_dfs, temp)

    def concat_dfs(self) -> pd.DataFrame:
        """
            Concats the three dataframes
        """
        df_list = [self._hardverapro_df, self._jofogas_df, self._marketplace_df]
        return pd.concat(df_list)
