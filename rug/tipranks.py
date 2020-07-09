import asyncio
import time

import httpx

from .exceptions import HttpException


class BaseAPI:
    def _get(self, *args):
        """
        TBD
        """

        try:
            return httpx.get(*args)
        except Exception as exc:
            raise HttpException(
                f"Couldn't perform GET request with args {args}"
            ) from exc

    async def _aget(self, *args):

        async with httpx.AsyncClient() as client:

            response = await client.get(*args)

            return response.json()


class UnofficialAPI(BaseAPI):
    """
    Unofficial API wrapper class for TipRanks.com.
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

    def get_basic_info(self):
        """
        Downloads basic info. Data are:

        * company_name
        * market
        * description
        * market_cap
        * has_dividends
        * similar_stocks
            * ticker
            * company_name
        * yoy_change
        * year_low
        * year_high
        * pe_ratio
        * eps

        :return: Dict with data.
        :rtype: dict
        """

        async def download_basics(symbol):
            """
            Downloads basic info about symbol. Data are:

            * company_name
            * market
            * description
            * market_cap
            * has_dividends
            * similar_stocks
                * ticker
                * company_name
            * yoy_change

            :param str symbol: Symbol the data will be downloaded for.
            :return: Dict with data.
            :rtype: dict
            """

            """
            Other meaningful returner properties are:

            {
                "hasEarnings": true,
                "consensuses":[{"rating":3,"nB":7,"nH":10,"nS":8,"period":3,"bench":1,"mStars":1,"d":"8/7/20","isLatest":1,"priceTarget":null}, ...],
                "experts":[
                    {
                        "name":"Luke Lango ","firm":"InvestorPlace","eUid":"4d8c5e4398e9bcf39f366e879626160cb149d76a","eTypeId":3,"expertImg":null,"ratings":[
                            {"ratingId":1,"actionId":8,"date":"2020-07-07T00:00:00","d":"1d","url":"https://investorplace.com/2020/07/strong-tesla-deliveries-confirm-that-tsla-stock-is-on-its-way-to-2000/","pos":4,"time":"2020-07-07T00:00:00","priceTarget":null,"convertedPriceTarget":null,"quote":{
                                    "title":"Strong Tesla Deliveries Confirm That TSLA Stock is On its Way to $2,000","date":"2020-07-07T00:00:00","quote":null,"site":"investorplace.com","link":"https://investorplace.com/2020/07/strong-tesla-deliveries-confirm-that-tsla-stock-is-on-its-way-to-2000/","siteName":"InvestorPlace"
                                },
                                "siteName":"InvestorPlace",
                                "site":"investorplace.com",
                                "id":27976100,
                                "rD":"2020-07-07T00:00:00",
                                "timestamp":"2020-07-07T15:42:19.893",
                                "priceTargetCurrency":null,
                                "convertedPriceTargetCurrency":null,
                                "convertedPriceTargetCurrencyCode":null,
                                "priceTargetCurrencyCode":null
                            }
                        ],
                        "stockSuccessRate":0.8888888888888888888888888889,
                        "stockAverageReturn":0.6676666666666666666666666667,
                        "stockTotalRecommendations":9,
                        "stockGoodRecommendations":8,
                        "rankings":[
                            {"period":3,"bench":1,"lRank":1,"gRank":1,"gRecs":402,"tRecs":505,"avgReturn":0.325,"stars":5.0,"originalStars":4.9992602455984613108447995265,"tPos":4.6}
                        ],
                        "stockid":0,
                        "newPictureUrl":null,
                        "includedInConsensus":false
                    },
                    ...
                ],
                ptConsensus":[
                    { "period":3,"bench":1,"priceTarget":915.64,"priceTargetCurrency":1,"priceTargetCurrencyCode":"USD","high":1500.0000,"low":350.0000},
                    ...
                ],
                "insiderTrading":null,
                "numOfAnalysts":6759,
                "numOfBloggers":7463,
                "numOfExperts":14222,
                "marketCap":257784965921,
                "tipranksStockScore":{"score":10,"returnOnAssets":0.0,"returnOnEquity":-2.0950,"sixMonthsMomentum":0.0,"volatilityLevel":0.0,"volatilityLevelRating":2,"twelveMonthsMomentum":4.9625,"simpleMovingAverage":1.0000,"assetGrowth":28.8360},
                "expertRatingsFilteredCount":10,
                "consensusOverTime":[
                    {"buy":7,"hold":5,"sell":12,"date":"2019-07-05T00:00:00+00:00","consensus":3,"priceTarget":262.17424242424244},
                    ...
                ],
                "bloggerSentiment":{
                    "bearish":"45","bullish":"53","bullishCount":48,"bearishCount":40,"score":2,"avg":0.7153,"neutral":"2","neutralCount":2
                },
                "corporateInsiderTransactions":[
                    {"sharesBought":null,"insidersBuyCount":0,"sharesSold":null,"insidersSellCount":1,"month":7,"year":2020,"transBuyCount":0,"transSellCount":1,"transBuyAmount":0.0,"transSellAmount":3250500.00,"informativeBuyCount":0,"informativeSellCount":0,"informativeBuyAmount":0.0,"informativeSellAmount":0.0},
                    ...
                ],
                "corporateInsiderActivity":{
                    "informativeSum":13,"nonInformativeSum":46,"totalSum":59,"informative":[
                        {"transactionTypeID":7,"count":7,"amount":82627749.42},
                        ...
                    ],
                    "nonInformative":[
                        {"transactionTypeID":5,"count":44,"amount":52055348.28},
                        ...
                    ]
                },
                "insiders":[
                    {"uId":"5a7f2ac6e8b812a670993ff2653c7a19c930e5cb","name":"Jerome Guillen","company":"Tesla","isOfficer":true,"isDirector":false,"isTenPercentOwner":false,"isOther":false,"officerTitle":"President, Automotive","otherText":"","transTypeId":5,"action":4,"date":"2d","amount":3250500.00,
                    "currencyTypeId":1,"rank":29950,"stars":3.0,"expertImg":null,"rDate":"2020-07-06T00:00:00","newPictureUrl":null,"link":"http://sec.gov/Archives/edgar/data/1584518/000158451820000008/xslF345X03/edgardoc.xml","numberOfShares":3000},
                    ...
                ],
                "insidrConfidenceSignal":{"stockScore":0.2053,"sectorScore":0.4632,"score":3},
                "numOfInsiders":73699,
                "yearlyDividendYield":0.0,
                "yearlyDividend":0.0,
                "insiderslast3MonthsSum":-2453860.00,
                "hedgeFundData":{
                    "stockID":11886,"holdingsByTime":[
                        {"date":"2018-06-30T00:00:00","holdingAmount":1164781,"institutionHoldingPercentage":0.0,"isComplete":true},
                        ...
                    ],
                    "sentiment":0.9562,
                    "trendAction":1,
                    "trendValue":1053300.0,
                    "institutionalHoldings":[
                        {"institutionID":794,"managerName":"John Horseman","institutionName":"Horseman Capital Management Ltd","action":4,"value":0,"expertUID":"54548c8413a95cbb25bd006e3cc7fcd15b2f1914","change":-100.0,"percentageOfPortfolio":0.000,"rank":75,"totalRankedInstitutions":200,"imageURL":null,"isActive":false,"stars":3.125},
                        ...
                    ]
                },
                "followerCount":33517,
                "momentum":{"baseDate":"2019-07-08T00:00:00","basePrice":230.34,"latestPrice":1389.86,"latestDate":"2020-07-07T00:00:00","momentum":5.0339498133194408266041503864},
                "portfolioHoldingData":{
                    "ticker":"TSLA","stockType":"stock","sectorId":"consumergoods","analystConsensus":{
                        "consensus":"neutral","rawConsensus":3,"distribution":{"buy":7.0,"hold":10.0,"sell":8.0}
                    },
                    "bestAnalystConsensus":{
                        "consensus":"neutral","rawConsensus":3,"distribution":{"buy":6.0,"hold":4.0,"sell":3.0}
                    },
                    "nextDividendDate":null,
                    "lastReportedEps":{
                        "date":"2020-04-29T00:00:00","company":"Tesla","ticker":"TSLA","periodEnding":"Mar 2020","eps":"-1.57","reportedEPS":"0.08","lastEps":"-4.1","consensus":null,"bpConsensus":null,"ratingsAndPT":{"priceTarget":null,"numBuys":null,"numHolds":null,"numSells":null},
                        "bpRatingsAndPT":{"priceTarget":null,"numBuys":null,"numHolds":null,"numSells":null},"marketCap":257784965921,"sector":18731,"stockId":11886,"stockTypeId":1,"surprise":-20.625,"timeOfDay":1,"isConfirmed":true},
                    "nextEarningsReport":{"date":"2020-07-22T00:00:00","company":"Tesla","ticker":"TSLA","periodEnding":"Jun 2020","eps":"-2.35","reportedEPS":null,"lastEps":"-2.31","consensus":null,"bpConsensus":null,"ratingsAndPT":{"priceTarget":null,"numBuys":null,
                    "numHolds":null,"numSells":null},"bpRatingsAndPT":{"priceTarget":null,"numBuys":null,"numHolds":null,"numSells":null},"marketCap":257784965921,"sector":18731,"stockId":11886,"stockTypeId":1,"surprise":null,"timeOfDay":4,"isConfirmed":false},
                    "stockUid":"e4ea3be6",
                    "companyName":"Tesla",
                    "priceTarget":843.53,
                    "bestPriceTarget":915.64,
                    "dividend":null,
                    "dividendYield":null,
                    "peRatio":null,
                    "stockId":11886,
                    "high52Weeks":null,
                    "low52Weeks":null,
                    "hedgeFundSentimentData":{ "rating":1,"score":0.9562},
                    "insiderSentimentData":{"rating":3,"stockScore":0.2053},
                    "bloggerSentimentData":{"ratingIfExists":2,"rating":2,"bearishCount":40,"bullishCount":48},
                    "shouldAddLinkToStockPage":true,
                    "expenseRatio":null,
                    "marketCap":257784965921,
                    "newsSentiment":0,
                    "landmarkPrices":{"yearToDate":{"date":"2020-01-02T00:00:00","d":"2/1/20","p":430.26},"threeMonthsAgo":{"date":"2020-04-09T00:00:00","d":"9/4/20","p":573.00},"yearAgo":{"date":"2019-07-08T00:00:00","d":"8/7/19","p":230.34}},
                    "priceTargetCurrencyId":0
                },
            }
            """

            async with httpx.AsyncClient() as client:

                start = time.time()
                json_data = await self._aget(
                    f"https://www.tipranks.com/api/stocks/getData/?name={symbol}"
                )

                return {
                    "company_name": json_data["companyName"],
                    "market": json_data["market"],
                    "description": json_data["description"],
                    "market_cap": int(json_data["marketCap"]),
                    "has_dividends": bool(json_data["hasDividends"]),
                    "similar_stocks": [
                        {"ticker": stock["ticker"], "company_name": stock["name"]}
                        for stock in json_data["similarStocks"]
                    ],
                    "yoy_change": float(json_data["momentum"]["momentum"]) * 100,
                }

        async def download_additionals(symbol):
            """
            Downloads additional info. Data are:

            * year_low
            * year_high
            * pe_ratio
            * eps

            :param str symbol: Symbol the data will be downloaded for.
            :return: Dict with data.
            :rtype: dict
            """

            async with httpx.AsyncClient() as client:

                json_data = await self._aget(
                    f"https://market.tipranks.com/api/details/GetRealTimeQuotes/?tickers={symbol}"
                )

                return {
                    "year_low": json_data[0]["yLow"],
                    "year_high": json_data[0]["yHigh"],
                    "pe_ratio": json_data[0]["pe"],
                    "eps": json_data[0]["eps"],
                }

        async def main():

            basic, additionals = await asyncio.gather(
                download_basics(self.symbol), download_additionals(self.symbol)
            )
            basic.update(additionals)

            return basic

        return asyncio.run(main())
