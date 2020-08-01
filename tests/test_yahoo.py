import sys
import os

sys.path.insert(0, os.path.abspath("../rug"))

from rug.yahoo import UnofficialAPI


def test_get_current_price():

    api = UnofficialAPI("AAPL")
    prices = api.get_current_price()

    assert isinstance(prices, dict)
    assert list(prices.keys()) == ["pre_market", "current_market", "post_market"]
    assert list(prices["pre_market"].keys()) == ["change", "value"]
    assert list(prices["pre_market"]["change"].keys()) == ["percents", "value"]
    assert list(prices["current_market"].keys()) == ["change", "value"]
    assert list(prices["current_market"]["change"].keys()) == ["percents", "value"]
    assert list(prices["post_market"].keys()) == ["change", "value"]
    assert list(prices["post_market"]["change"].keys()) == ["percents", "value"]
