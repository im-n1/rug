import httpx


class BaseAPI:
    @staticmethod
    def _get(*args):
        """
        TBD
        """

        return httpx.get(*args)


class UnofficialAPI(BaseAPI):
    """
    Unofficial API wrapper class.
    Unofficial means this class calls some hidden endpoints
    and provides data that official API doesn't. Also doesn't
    need an authorization.
    """

    def __init__(self, symbol):
        """
        Constructor.

        :param str symbol: Symbol of te item we wanna get info about.
        """

        self.symbol = str(symbol)

    def get_dividends(self):
        """
        Fetches symbol dividends with following fields:

        * yield
        * sector_average_yield
        * payment_date
        * ex_date
        * receive_date
        * growth_since

        :return: List of dividend objects.
        :rtype: list
        """

        response = self._get(
            f"https://www.tipranks.com/api/stocks/getChartPageData/?ticker={self.symbol}"
        )
        data = response.json()

        dividends = []

        for item in data["dividends"]:
            dividends.append(
                {
                    "yield": item["yield"],
                    "sector_average_yield": item["sectorYield"],
                    "payment_date": item["payDate"],
                    "ex_date": item["exDate"],
                    "receive_date": item["recDate"],
                    "growth_since": item["growthSinceDate"],
                }
            )

        return dividends

    def get_year_highs_and_lows(self):
        """
        Fetches highs and lows for each year - maximum 7 years back.

        Each year has following fields:

        * year
        * high
        * low

        :return: List of years with the data.
        :rtype: list
        """

        response = self._get(
            f"https://www.tipranks.com/api/stocks/getChartPageData/?ticker={self.symbol}"
        )
        data = response.json()

        return data["historicalHighLow"]
