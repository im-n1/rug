import sys
import os

sys.path.insert(0, os.path.abspath("../rug"))

from rug.stocktwits import UnofficialAPI
from datetime import date, timedelta
import time


def test_get_earnings_calendar():

    api = UnofficialAPI()
    earnings = api.get_earnings_calendar(
        date.today(), date.today() + timedelta(days=10)
    )

    assert isinstance(earnings, list)
    assert isinstance(earnings[0], dict)
    assert list(earnings[0].keys()) == ["date", "symbol", "time", "when"]
    assert isinstance(earnings[0]["date"], date)
    assert isinstance(earnings[0]["time"], time.struct_time)
