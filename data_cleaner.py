import datetime
import constants
from dateutil.relativedelta import relativedelta


class DataCleaner:
    """
        Data cleaner for the scraped data
        Attributes:
            _months(dict): Contains Hungarian month names and their corresponding numerical representation.
            _days(dict): Contains Hungarian names for numbers and their numerical equivalents.
            site(str): Employ the cleaning techniques specific to this site.
    """

    def __init__(self, site):
        self._months = constants.months
        self._days = constants.days
        self.site = site

    def clean_date(self, data: str) -> str:
        """
            Clean the date data depending on the specified site.
        """
        if self.site == 'jofogas':
            return self._date_from_words_jofogas(data)
        elif self.site == 'hardverapro':
            return data[0:10]
        elif self.site == 'marketplace':
            return self._date_from_words_marketplace(data)

    def clean_price(self, data: str) -> int:
        """
            Clean the price data depending on the specified site.
        """
        try:
            if self.site == 'jofogas':
                price = int(data.replace(' ', ''))
            else:
                data = data.replace(' ', '')
                data = data[0:(data.find('Ft') + 2)]
                price = int(data.replace('Ft', ''))
        except ValueError:
            print('This data (price) caused a value error while trying to convert it to int : ' + data)
            price = 1

        return price

    def _date_from_words_marketplace(self, listing_date: str) -> str:
        """
            Responsible for converting a date string from the marketplace site into a standardized string
            representation of the date in the format YYYY-MM-DD.
        """
        listing_date = listing_date.lower()

        if 'órája' not in listing_date and 'perce' not in listing_date:
            try:
                listing_time = listing_date[listing_date.index(' ') + 1:listing_date.index(",")]
                listing_time_num = listing_time[0:listing_time.index(' ')]
            except ValueError:
                print('This data caused a value error while trying to convert it to date: ' + listing_date)
                return datetime.date.today().strftime('%Y-%m-%d')

            if any(word in listing_time_num for word in self._days.keys()):
                listing_time_num = self._days[listing_time_num]

            listing_time_type = listing_time[listing_time.index(' ') + 1:]

            if listing_time_type == 'napja':
                return (datetime.date.today() + relativedelta(days=-int(listing_time_num))).strftime('%Y-%m-%d')
            elif listing_time_type == 'hete':
                return (datetime.date.today() + relativedelta(weeks=-int(listing_time_num))).strftime('%Y-%m-%d')
            elif listing_time_type == 'hónapja':
                return (datetime.date.today() + relativedelta(months=-int(listing_time_num))).strftime('%Y-%m-%d')
        else:
            return datetime.date.today().strftime('%Y-%m-%d')

    def _date_from_words_jofogas(self, listing_date: str) -> str:  # Add documentation
        """
            Responsible for converting a date string from the jofogas site into a standardized string
            representation of the date in the format YYYY-MM-DD.
        """
        listing_date = listing_date.lower()
        listing_day = ''
        listing_month = ''
        listing_year = ''

        for month in self._months:
            if month in listing_date:
                slice_at = listing_date.index(" ")
                listing_month = self._months[listing_date[0:slice_at]]
                listing_day = listing_date[slice_at + 1:slice_at + 3]

                if listing_day[1] == '.':
                    listing_day = '0' + listing_day[0]

                listing_year = str(datetime.date.today().year)

        return listing_year + '-' + listing_month + '-' + listing_day

    @staticmethod
    def clean_description(data: str) -> str:
        """
           Removes newline characters.
        """
        return data.replace('\n', '')
