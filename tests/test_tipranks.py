import sys
import os

sys.path.insert(0, os.path.abspath("../rug"))

from rug.tipranks import UnofficialAPI


def test_get_dividends():

    api = UnofficialAPI("AAPL")
    dividends = api.get_dividends()

    assert isinstance(dividends, list)
    assert list(dividends[0].keys()) == [
        "yield",
        "sector_average_yield",
        "payment_date",
        "ex_date",
        "receive_date",
        "growth_since",
    ]


def test_year_highs_and_lows():

    api = UnofficialAPI("AAPL")
    values = api.get_year_highs_and_lows()

    assert isinstance(values, list)
    assert list(values[0].keys()) == [
        "year",
        "high",
        "low",
    ]


def test_get_basic_info():

    api = UnofficialAPI("AAPL")
    info = api.get_basic_info()

    assert isinstance(info, dict)
    assert list(info.keys()) == [
        "company_name",
        "market",
        "description",
        "market_cap",
        "has_dividends",
        "similar_stocks",
        "yoy_change",
        "year_low",
        "year_high",
        "pe_ratio",
        "eps",
    ]
    assert list(info["similar_stocks"][0].keys()) == [
        "ticker",
        "company_name",
    ]
